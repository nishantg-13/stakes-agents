"""ProbeAgent: tau2's LLMAgent plus sampling-based probes, and (v0) STAKES deliberation.

Modes
-----
measure      Baseline pilot. At write steps (and a fraction of reads), sample k extra candidates
             and log disagreement. Candidates are NEVER executed; probe tokens are measurement.
uniform      At every tool step: sample k candidates, execute the majority action.
unc_only     At every tool step: sample k candidates, vote; run the verifier only when the
             samples disagree (p_hat > 0). Allocation ignores the action's effect type.
verify_writes  Rule baseline: run the verifier on every state-changing step; no sampling.
stakes       STAKES v0 (fixed rule). READ steps: nothing. Writes: sample k and vote. COMPENSABLE
             and IRREVERSIBLE writes: additionally run the verifier *regardless of p_hat*,
             because a confident mistake there cannot be undone.
voc          STAKES (Algorithm 1). Writes: sample k and vote; then run the verifier iff
             p_err(effect, p_hat) * C(effect) * phi - lam * kappa > 0 (see stakes.voc).
             Sweeping lam traces the cost-reliability frontier.

In the acting modes, deliberation tokens are real agent compute and are reported as
`delib_*` so conditions can be compared at total cost. The verifier is an LLM policy check
(operator o3 in the proposal). If it says REVISE, the agent regenerates once with the
reviewer's note appended to its context.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from dataclasses import asdict, dataclass, field

from tau2.agent.llm_agent import LLMAgent
from tau2.data_model.message import SystemMessage, UserMessage
from tau2.utils.llm_utils import generate

from stakes.canon import disagreement, proposal_disagreement
from stakes.effects import EffectRegistry, EffectType
from stakes.voc import VocParams

MODES = ("measure", "uniform", "unc_only", "verify_writes", "stakes", "voc")
HIGH_STAKES = (EffectType.COMPENSABLE, EffectType.IRREVERSIBLE)

# One prompt for every mode and effect type, so conditions differ only in *where* it is used
# (D-011). The effect line tells the reviewer what kind of action it is judging, which keeps it
# from applying write-only checks (confirmation, eligibility) to read-only lookups.
VERIFIER_PROMPT = """You are a careful reviewer checking ONE proposed action by a customer-service
agent before it is executed.

<policy>
{policy}
</policy>

Check the proposed action against the policy and the conversation:
- Are all identifiers and arguments exactly the ones the customer specified or the tools returned?
- For an action that changes data: did the agent check every precondition the policy requires
  (status, eligibility, rules), and did the customer explicitly confirm this exact action when
  the policy requires confirmation?
- Is this action what the customer actually asked for?

Default to APPROVE. Reply REVISE only if you can name a specific violated policy rule, a wrong or
unverified argument, or a missing required confirmation. Do not REVISE because a different
action would also be acceptable, and never ask for the action that is already proposed.

Reply with exactly one line, starting with APPROVE or REVISE:
APPROVE
or
REVISE: <one-sentence reason>"""

EFFECT_DESCRIPTIONS = {
    EffectType.READ: "read-only lookup; it changes nothing",
    EffectType.IDEMPOTENT: "changes data; repeating it has no further effect",
    EffectType.REVERSIBLE: "changes data; the agent can undo it later with another tool",
    EffectType.COMPENSABLE: "changes data; it can only be partly undone, at a cost (fees, fare change)",
    EffectType.IRREVERSIBLE: "changes data; it cannot be undone",
}


def parse_verdict(text: str) -> tuple[str, str | None]:
    """Strict parse of the reviewer reply. Returns (verdict, reason).

    Only the first non-empty line counts. Anything that is not clearly APPROVE or REVISE is
    treated as APPROVE ("UNPARSED"): fail open, so a garbled reply can never block an action.
    """
    first = next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "")
    first = first.strip("*`_ ")  # tolerate markdown emphasis
    if re.match(r"^APPROVE\b", first, flags=re.IGNORECASE):
        return "APPROVE", None
    m = re.match(r"^REVISE\b\s*:?\s*(.*)", first, flags=re.IGNORECASE)
    if m:
        return "REVISE", (m.group(1).strip()[:500] or "The reviewer flagged this action.")
    return "UNPARSED", None


@dataclass
class ProbeRecord:
    agent_turn: int  # 0-based count of messages this agent has generated in the episode
    proposal: str  # canonical key of the first sampled message
    effect: str
    probed: bool
    mode: str = "measure"
    executed: str | None = None  # canonical key of the message actually returned
    candidates: list[str] = field(default_factory=list)
    p_hat: float | None = None  # share of candidates disagreeing with the proposal
    modal_disagreement: float | None = None
    switched_by_vote: bool = False
    verified: bool = False
    verdict: str | None = None
    revised: bool = False
    voc: float | None = None  # verifier VOC at this step (voc mode only)
    probe_cost: float = 0.0  # all extra LLM calls (candidates, verifier, revision)
    probe_prompt_tokens: int = 0
    probe_completion_tokens: int = 0
    probe_errors: int = 0


def _calls(message) -> list[tuple[str, dict]]:
    return [(tc.name, tc.arguments) for tc in (message.tool_calls or [])]


def _usage_tokens(message) -> tuple[int, int]:
    usage = getattr(message, "usage", None) or {}
    return int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0)


def _render(messages, limit: int = 40, max_chars: int = 1500) -> str:
    lines = []
    for m in messages[-limit:]:
        role = getattr(m, "role", "?")
        if role == "system":
            continue
        text = (getattr(m, "content", None) or "").strip()
        calls = getattr(m, "tool_calls", None) or []
        if calls:
            text = (text + " " if text else "") + "; ".join(
                f"CALL {tc.name}({tc.arguments})" for tc in calls
            )
        lines.append(f"[{role}] {text[:max_chars]}")
    return "\n".join(lines)


class ProbeAgent(LLMAgent):
    def __init__(
        self,
        *args,
        registry: EffectRegistry,
        k0: int = 3,
        probe_temperature: float = 1.0,
        probe_reads_frac: float = 0.0,
        probe_seed: int = 0,
        mode: str = "measure",
        verifier_llm: str | None = None,
        voc_params: VocParams | None = None,
        lam: float = 0.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        self.registry = registry
        self.k0 = k0
        self.probe_temperature = probe_temperature
        self.probe_reads_frac = probe_reads_frac
        self.mode = mode
        self.verifier_llm = verifier_llm
        if mode == "voc" and voc_params is None:
            raise ValueError("mode 'voc' needs voc_params (fit them with python -m stakes.voc)")
        self.voc_params = voc_params
        self.lam = lam
        self._rng = random.Random(probe_seed)
        self.probe_log: list[ProbeRecord] = []
        self._turn = 0

    # -- LLM helpers ---------------------------------------------------------------------
    def _account(self, record: ProbeRecord, msg) -> None:
        record.probe_cost += float(getattr(msg, "cost", None) or 0.0)
        p, c = _usage_tokens(msg)
        record.probe_prompt_tokens += p
        record.probe_completion_tokens += c

    def _sample(self, context, record: ProbeRecord, n: int) -> list:
        out = []
        for _ in range(n):
            # tau2 pins llm_args["seed"] per trial; reusing it would make every candidate
            # identical on providers that honour seeds (faking p_hat = 0). Each sample gets its
            # own seed from a seeded RNG, so runs stay reproducible.
            args = {
                **self.llm_args,
                "temperature": self.probe_temperature,
                "seed": self._rng.randrange(2**31),
            }
            try:
                cand = generate(
                    model=self.llm,
                    tools=self.tools,
                    messages=context,
                    call_name="stakes_probe",
                    **args,
                )
            except Exception:  # noqa: BLE001 - a failed sample must never kill the episode
                record.probe_errors += 1
                continue
            self._account(record, cand)
            out.append(cand)
        return out

    def _verify(self, context, proposal, record: ProbeRecord) -> str | None:
        """Return None if approved, else the reviewer's reason."""
        record.verified = True
        calls = _calls(proposal)
        action = "; ".join(f"{n}({a})" for n, a in calls)
        effect = self.registry.max_type([n for n, _ in calls]) if calls else EffectType.READ
        try:
            reply = generate(
                model=self.verifier_llm or self.llm,
                messages=[
                    SystemMessage(role="system", content=VERIFIER_PROMPT.format(policy=self.domain_policy)),
                    UserMessage(
                        role="user",
                        content=f"<conversation>\n{_render(context)}\n</conversation>\n\n"
                        f"<proposed_action>\n{action}\n</proposed_action>\n"
                        f"Effect of this action: {EFFECT_DESCRIPTIONS[effect]}.",
                    ),
                ],
                call_name="stakes_verifier",
                temperature=0.0,
            )
        except Exception:  # noqa: BLE001 - fail open: an unavailable verifier must not block
            record.probe_errors += 1
            record.verdict = "ERROR"
            return None
        self._account(record, reply)
        text = (reply.content or "").strip()
        verdict, reason = parse_verdict(text)
        record.verdict = text[:300] if verdict != "UNPARSED" else f"UNPARSED: {text[:280]}"
        return reason

    def _revise(self, context, reason: str, record: ProbeRecord):
        note = SystemMessage(
            role="system",
            content=(
                "Internal reviewer note (not from the customer): your planned action "
                f"was flagged before execution. Reason: {reason} "
                "Reconsider. If information or confirmation is missing, ask the customer "
                "instead of acting."
            ),
        )
        revised = self._sample(context + [note], record, 1)
        if revised:
            record.revised = True
            return revised[0]
        return None

    # -- main hook -------------------------------------------------------------------------
    def _generate_next_message(self, message, state):
        proposal = super()._generate_next_message(message, state)
        # super() appended the incoming message to state.messages; the proposal is not in it yet,
        # so this is exactly the context the proposal was sampled from.
        context = state.system_messages + state.messages
        calls = _calls(proposal)
        effect = self.registry.max_type([n for n, _ in calls]) if calls else EffectType.READ
        key = self.registry.canon(calls)
        record = ProbeRecord(
            agent_turn=self._turn, proposal=key, effect=effect.value, probed=False, mode=self.mode
        )
        chosen = proposal
        if calls:
            chosen = self._deliberate(context, proposal, key, effect, record)
        record.executed = self.registry.canon(_calls(chosen))
        self.probe_log.append(record)
        self._turn += 1
        return chosen

    def _deliberate(self, context, proposal, key, effect, record):
        mode = self.mode
        sample = False
        verify = False
        if mode == "measure":
            sample = self.k0 > 0 and (
                effect.is_write or self._rng.random() < self.probe_reads_frac
            )
        elif mode == "uniform" or mode == "unc_only":
            sample = True
        elif mode == "verify_writes":
            verify = effect.is_write
        elif mode == "stakes":
            sample = effect.is_write
            verify = effect in HIGH_STAKES
        elif mode == "voc":
            sample = effect.is_write  # Algorithm 1: READ executes directly

        chosen = proposal
        if sample and self.k0 > 0:
            record.probed = True
            cands = self._sample(context, record, self.k0)
            keys = [self.registry.canon(_calls(c)) for c in cands]
            record.candidates = keys
            if keys:
                record.p_hat = proposal_disagreement(key, keys)
                record.modal_disagreement = disagreement([key, *keys])
            if mode != "measure" and keys:
                pool = [(key, proposal)] + list(zip(keys, cands))
                top_key, top_n = Counter(k for k, _ in pool).most_common(1)[0]
                if top_key != key and top_n > Counter(k for k, _ in pool)[key]:
                    chosen = next(m for k, m in pool if k == top_key)
                    record.switched_by_vote = True
            if mode == "unc_only" and (record.p_hat or 0) > 0:
                verify = True

        if mode == "voc" and effect.is_write:
            # the vote may have changed the action; price the verifier on what will execute
            chosen_calls = _calls(chosen)
            eff = self.registry.max_type([n for n, _ in chosen_calls]) if chosen_calls else EffectType.READ
            record.voc = self.voc_params.voc_verify(eff, record.p_hat, self.lam)
            verify = eff.is_write and record.voc > 0

        if verify:
            reason = self._verify(context, chosen, record)
            if reason:
                revised = self._revise(context, reason, record)
                if revised is not None:
                    chosen = revised
        return chosen

    def probe_dicts(self) -> list[dict]:
        return [asdict(r) for r in self.probe_log]

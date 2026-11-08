"""Effect ledger built from a finished episode, plus decisive-error classification.

Writes are judged against tau2's *reference* trajectory (evaluation_criteria.actions). tau2
uses that trajectory to derive the target DB state; it is not the only valid path. So:
  * a write that matches no remaining reference write is marked `erroneous`;
  * we only *attribute failures* in episodes that actually failed (reward < 1);
  * erroneous writes in *successful* episodes are counted as matcher false positives,
    which is a sanity metric for this labelling (see `matcher_false_positive_rate`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from stakes.effects import EffectRegistry, EffectType


@dataclass
class LedgerEntry:
    turn: int  # index of the assistant message within the episode
    name: str
    arguments: dict
    effect: str
    tool_error: bool  # the tool raised or rejected the call, so assume no state change
    erroneous: bool = False  # executed write that matches no remaining reference write
    matched_gold: str | None = None
    p_hat: float | None = None  # filled from the probe log when available


@dataclass
class EpisodeLedger:
    entries: list[LedgerEntry] = field(default_factory=list)
    unmatched_gold_writes: list[str] = field(default_factory=list)

    def to_dicts(self) -> list[dict]:
        return [asdict(e) for e in self.entries]


def _covers(gold, call) -> bool:
    """Does the agent's value contain everything the reference value specifies?

    Dicts: every reference key must be present and match; extra keys in the call are allowed
    (e.g. the agent adds 'origin'/'price' to a flight that the reference gives as
    {flight_number, date}, and the tool ignores the extras). Lists: same length, matched in
    order. Scalars: equal, with 2 == 2.0.
    """
    if isinstance(gold, dict):
        return isinstance(call, dict) and all(k in call and _covers(v, call[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return (
            isinstance(call, list)
            and len(gold) == len(call)
            and all(_covers(g, c) for g, c in zip(gold, call, strict=True))
        )
    if isinstance(gold, (int, float)) and isinstance(call, (int, float)) and not isinstance(gold, bool):
        return float(gold) == float(call)
    return gold == call


def _args_match(gold: dict, call_args: dict) -> bool:
    """Match a call against a reference action on the reference's arguments (or compare_args)."""
    keys = gold.get("compare_args")
    ref = gold["arguments"] if keys is None else {k: gold["arguments"].get(k) for k in keys}
    return _covers(ref, call_args)


def build_ledger(
    calls: list[dict], gold_actions: list[dict], registry: EffectRegistry
) -> EpisodeLedger:
    """calls: agent tool calls in order, as {turn, name, arguments, error}.
    gold_actions: reference actions as {action_id, name, arguments, compare_args, requestor}.
    """
    gold_writes = [
        g
        for g in gold_actions
        if g.get("requestor", "assistant") == "assistant"
        and registry.type_of(g["name"]).is_write
        and registry.mutates(g["name"])
    ]
    remaining = list(gold_writes)
    ledger = EpisodeLedger()
    for c in calls:
        effect = registry.type_of(c["name"])
        entry = LedgerEntry(
            turn=c["turn"],
            name=c["name"],
            arguments=c.get("arguments") or {},
            effect=effect.value,
            tool_error=bool(c.get("error")),
        )
        # Only DB-mutating writes can be "erroneous": success is judged on DB state (D-003).
        if effect.is_write and registry.mutates(c["name"]) and not entry.tool_error:
            match = next(
                (g for g in remaining if g["name"] == c["name"] and _args_match(g, entry.arguments)),
                None,
            )
            if match is None:
                entry.erroneous = True
            else:
                entry.matched_gold = match.get("action_id")
                remaining.remove(match)
        ledger.entries.append(entry)
    ledger.unmatched_gold_writes = [g.get("action_id", g["name"]) for g in remaining]
    return ledger


@dataclass
class DecisiveError:
    kind: str  # "wrong_write" | "missed_write" | "no_write_error"
    effect: str | None = None
    p_hat: float | None = None
    turn: int | None = None
    tool: str | None = None


def decisive_error(ledger: EpisodeLedger) -> DecisiveError:
    """Classify the failure of a *failed* episode by its first erroneous write."""
    for e in ledger.entries:
        if e.erroneous:
            return DecisiveError("wrong_write", e.effect, e.p_hat, e.turn, e.name)
    if ledger.unmatched_gold_writes:
        return DecisiveError("missed_write")
    return DecisiveError("no_write_error")  # e.g. a communication or policy-explanation failure


def write_effects() -> set[str]:
    return {t.value for t in EffectType if t.is_write}

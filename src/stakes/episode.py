"""Turn a finished tau2 SimulationRun plus the probe log into one JSON-serialisable record."""

from __future__ import annotations

from stakes.effects import EffectRegistry
from stakes.ledger import build_ledger, decisive_error
from stakes.metrics import is_success


def _usage(msg) -> tuple[int, int]:
    u = getattr(msg, "usage", None) or {}
    return int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)


def extract_agent_calls(messages) -> tuple[list[dict], list]:
    """Agent tool calls in order, with turn = index among assistant messages."""
    tool_errors = {}
    for m in messages:
        if getattr(m, "role", None) == "tool":
            tool_errors[getattr(m, "id", "")] = bool(getattr(m, "error", False))
    calls, assistant_msgs = [], []
    for m in messages:
        if getattr(m, "role", None) != "assistant":
            continue
        turn = len(assistant_msgs)
        assistant_msgs.append(m)
        for tc in m.tool_calls or []:
            calls.append(
                {
                    "turn": turn,
                    "name": tc.name,
                    "arguments": tc.arguments,
                    "error": tool_errors.get(tc.id, False),
                }
            )
    return calls, assistant_msgs


def gold_actions(task) -> list[dict]:
    crit = task.evaluation_criteria
    return [
        {
            "action_id": a.action_id,
            "name": a.name,
            "arguments": a.arguments,
            "compare_args": a.compare_args,
            "requestor": a.requestor,
        }
        for a in ((crit.actions if crit else None) or [])
    ]


def build_record(*, result, task, trial, seed, registry: EffectRegistry, probes: list[dict], meta):
    calls, assistant_msgs = extract_agent_calls(result.messages or [])
    ledger = build_ledger(calls, gold_actions(task), registry)

    # Align probes (one per message the agent generated) with transcript assistant messages.
    # The transcript also holds assistant messages the agent never generated, e.g. tau2's fixed
    # opening greeting, so align in order by canonical key and skip non-matching messages.
    by_turn = {}
    j = 0
    for i, msg in enumerate(assistant_msgs):
        if j >= len(probes):
            break
        key = registry.canon([(tc.name, tc.arguments) for tc in (msg.tool_calls or [])])
        if key == (probes[j].get("executed") or probes[j]["proposal"]):
            by_turn[i] = probes[j]
            j += 1
    mismatches = len(probes) - len(by_turn)  # probes that found no transcript message
    for e in ledger.entries:
        p = by_turn.get(e.turn)
        if p is not None:
            e.p_hat = p["p_hat"]

    reward = result.reward_info.reward if result.reward_info else None
    prompt_toks = sum(_usage(m)[0] for m in assistant_msgs)
    completion_toks = sum(_usage(m)[1] for m in assistant_msgs)
    # tau2's own agent_cost is None whenever any assistant message lacks a cost (its fixed
    # opening greeting never has one), so sum the costed messages ourselves.
    agent_cost = sum(float(m.cost) for m in assistant_msgs if getattr(m, "cost", None) is not None)
    rec = {
        **meta,
        "task_id": task.id,
        "trial": trial,
        "seed": seed,
        "reward": reward,
        "success": is_success(reward),
        "termination_reason": str(result.termination_reason),
        "agent_cost": agent_cost,
        "user_cost": result.user_cost,
        "agent_prompt_tokens": prompt_toks,
        "agent_completion_tokens": completion_toks,
        "probe_cost": sum(p["probe_cost"] for p in probes),
        "probe_prompt_tokens": sum(p["probe_prompt_tokens"] for p in probes),
        "probe_completion_tokens": sum(p["probe_completion_tokens"] for p in probes),
        "n_assistant_msgs": len(assistant_msgs),
        "n_probes": len(probes),
        "probe_join_mismatches": mismatches,
        "ledger": ledger.to_dicts(),
        "unmatched_gold_writes": ledger.unmatched_gold_writes,
        "probes": probes,
        "decisive_error": None,
    }
    if not rec["success"]:
        rec["decisive_error"] = vars(decisive_error(ledger))
    return rec

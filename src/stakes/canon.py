"""Canonical keys for proposed actions, and disagreement-based error probability (p-hat)."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from typing import Any

TEXT_REPLY = "<text>"  # key for a message with no tool calls (agent replies to the user)


def _norm(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.strip().split()).lower()
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        # 2 and 2.0 compare equal; avoid float noise
        return round(float(value), 6)
    if isinstance(value, dict):
        return {str(k): _norm(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value]
    return str(value)


def canon_call(name: str, arguments: dict | None) -> str:
    return f"{name}({json.dumps(_norm(arguments or {}), sort_keys=True)})"


def canon_message(tool_calls: Iterable[tuple[str, dict | None]] | None) -> str:
    """Key for a whole assistant message. Order-insensitive across parallel tool calls."""
    calls = sorted(canon_call(n, a) for n, a in (tool_calls or []))
    return " | ".join(calls) if calls else TEXT_REPLY


def disagreement(keys: list[str]) -> float:
    """p-hat = 1 - (count of the modal key) / (number of samples). 0 means full agreement."""
    if not keys:
        raise ValueError("need at least one sample")
    return 1.0 - Counter(keys).most_common(1)[0][1] / len(keys)


def proposal_disagreement(proposal: str, candidates: list[str]) -> float:
    """Fraction of extra candidates that differ from the executed proposal.

    This is the error signal for *this specific action*. It differs from `disagreement`
    when the proposal is not the modal sample.
    """
    if not candidates:
        raise ValueError("need at least one candidate")
    return sum(c != proposal for c in candidates) / len(candidates)

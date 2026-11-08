import pytest

import stakes.tau2_setup  # noqa: F401
from stakes.pilot import analyze


def _ep(task, trial, success, decisive=None, probes=None, ledger=None):
    return {
        "task_id": task,
        "trial": trial,
        "reward": 1.0 if success else 0.0,
        "success": success,
        "agent_cost": 0.01,
        "user_cost": 0.01,
        "probe_cost": 0.002,
        "agent_prompt_tokens": 100,
        "agent_completion_tokens": 10,
        "probe_prompt_tokens": 50,
        "probe_completion_tokens": 5,
        "probe_join_mismatches": 0,
        "probes": probes or [],
        "ledger": ledger or [],
        "decisive_error": decisive,
    }


def _ww(effect, p_hat):
    return {"kind": "wrong_write", "effect": effect, "p_hat": p_hat, "turn": 3, "tool": "x"}


def test_analysis_go_decision_and_breakdown():
    eps = [
        _ep("a", 0, True, ledger=[{"effect": "IRREVERSIBLE", "tool_error": False, "erroneous": False}]),
        _ep("a", 1, False, _ww("IRREVERSIBLE", 0.0)),       # confident wrong write
        _ep("b", 0, False, _ww("COMPENSABLE", 1 / 3)),      # still "low" (<= 1/3)
        _ep("b", 1, False, _ww("IRREVERSIBLE", 2 / 3)),     # uncertain wrong write
        _ep("c", 0, False, {"kind": "missed_write"}),
        _ep("c", 1, True),
    ]
    r = analyze(eps)
    assert r["n_failed"] == 4
    assert r["confident_wrong_write_share_of_failures"] == pytest.approx(2 / 4)
    assert r["decision"] == "GO"
    assert r["decisive_error_kinds"] == {"wrong_write": 3, "missed_write": 1}
    assert r["wrong_write_by_effect"] == {"IRREVERSIBLE": 2, "COMPENSABLE": 1}
    assert r["matcher_false_positive_rate"] == 0.0
    assert set(r["reliability"]) == {1, 2}


def test_analysis_pivot_decision():
    eps = [_ep(f"t{i}", 0, False, {"kind": "no_write_error"}) for i in range(9)]
    eps.append(_ep("t9", 0, False, _ww("IRREVERSIBLE", 0.0)))  # 1/10 < 0.15
    assert analyze(eps)["decision"] == "PIVOT to Idea #2"


def test_read_share():
    probes = [
        {"proposal": "get()", "effect": "READ"},
        {"proposal": "get()", "effect": "READ"},
        {"proposal": "cancel()", "effect": "IRREVERSIBLE"},
        {"proposal": "<text>", "effect": "READ"},  # text replies are not tool steps
    ]
    r = analyze([_ep("a", 0, True, probes=probes)])
    assert r["read_share_of_tool_steps"] == pytest.approx(2 / 3)

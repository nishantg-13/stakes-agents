import math

import pytest

from stakes.metrics import (
    bootstrap_ci,
    irreversible_error_rate,
    pass_at_k,
    pass_at_k_task,
    pass_hat_k,
    pass_hat_k_task,
    per_task_counts,
)


def test_pass_hat_k_hand_computed():
    # 3 of 4 trials succeed: P(2 random trials both succeed) = C(3,2)/C(4,2) = 3/6
    assert pass_hat_k_task(4, 3, 2) == pytest.approx(0.5)
    assert pass_hat_k_task(4, 3, 1) == pytest.approx(0.75)
    assert pass_hat_k_task(4, 3, 4) == 0.0
    assert pass_hat_k_task(4, 4, 4) == 1.0


def test_pass_at_k_hand_computed():
    # 1 of 4 succeeds: P(at least one of 2 succeeds) = 1 - C(3,2)/C(4,2) = 1 - 3/6
    assert pass_at_k_task(4, 1, 2) == pytest.approx(0.5)
    assert pass_at_k_task(4, 0, 3) == 0.0
    assert pass_at_k_task(4, 3, 2) == 1.0  # fewer than k failures


def test_k1_estimators_agree_with_success_rate():
    for n, c in [(4, 0), (4, 1), (8, 5), (8, 8)]:
        assert pass_hat_k_task(n, c, 1) == pytest.approx(c / n)
        assert pass_at_k_task(n, c, 1) == pytest.approx(c / n)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        pass_hat_k_task(4, 5, 1)
    with pytest.raises(ValueError):
        pass_hat_k_task(4, 2, 5)


def test_aggregate_over_tasks():
    recs = [{"task_id": "a", "reward": r} for r in (1, 1, 1, 0)] + [
        {"task_id": "b", "reward": r} for r in (0, 0, 1, 0)
    ]
    assert per_task_counts(recs) == {"a": (4, 3), "b": (4, 1)}
    assert pass_hat_k(recs, 2) == pytest.approx((0.5 + 0.0) / 2)
    assert pass_at_k(recs, 2) == pytest.approx((1.0 + 0.5) / 2)


def test_partial_reward_is_failure():
    recs = [{"task_id": "a", "reward": 0.99}, {"task_id": "a", "reward": None}]
    assert per_task_counts(recs) == {"a": (2, 0)}


def test_bootstrap_ci_brackets_mean():
    counts = {f"t{i}": (4, i % 5) for i in range(40)}
    m, lo, hi = bootstrap_ci(counts, 2, n_boot=2000)
    assert lo <= m <= hi
    assert not math.isnan(m)


def test_irreversible_error_rate():
    eps = [
        {"ledger": [{"effect": "IRREVERSIBLE", "erroneous": True}, {"effect": "READ", "erroneous": False}]},
        {"ledger": [{"effect": "REVERSIBLE", "erroneous": True}]},  # reversible errors don't count
        {"ledger": [{"effect": "COMPENSABLE", "erroneous": True}]},
    ]
    assert irreversible_error_rate(eps) == pytest.approx(2 / 3)

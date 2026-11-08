"""Reliability metrics. pass^k and pass@k use the unbiased estimators from tau-bench / Codex."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from math import comb

import numpy as np

SUCCESS_EPS = 1e-6


def is_success(reward: float | None) -> bool:
    return reward is not None and reward >= 1.0 - SUCCESS_EPS


def pass_hat_k_task(n: int, c: int, k: int) -> float:
    """P(all k of k i.i.d. trials succeed), estimated from c successes in n trials."""
    _check(n, c, k)
    return comb(c, k) / comb(n, k)


def pass_at_k_task(n: int, c: int, k: int) -> float:
    """P(at least one of k i.i.d. trials succeeds), estimated from c successes in n trials."""
    _check(n, c, k)
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def _check(n: int, c: int, k: int) -> None:
    if not (0 <= c <= n) or not (1 <= k <= n):
        raise ValueError(f"need 0<=c<=n and 1<=k<=n, got n={n} c={c} k={k}")


def per_task_counts(records: Iterable[dict]) -> dict[str, tuple[int, int]]:
    """records: dicts with 'task_id' and 'reward'. Returns task_id -> (n, c)."""
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in records:
        counts[r["task_id"]][0] += 1
        counts[r["task_id"]][1] += int(is_success(r["reward"]))
    return {t: (n, c) for t, (n, c) in counts.items()}


def mean_over_tasks(counts: dict[str, tuple[int, int]], k: int, fn) -> float:
    vals = [fn(n, c, k) for n, c in counts.values() if n >= k]
    if not vals:
        raise ValueError(f"no task has >= {k} trials")
    return float(np.mean(vals))


def pass_hat_k(records: Iterable[dict], k: int) -> float:
    return mean_over_tasks(per_task_counts(records), k, pass_hat_k_task)


def pass_at_k(records: Iterable[dict], k: int) -> float:
    return mean_over_tasks(per_task_counts(records), k, pass_at_k_task)


def bootstrap_ci(
    counts: dict[str, tuple[int, int]],
    k: int,
    fn=pass_hat_k_task,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Point estimate and percentile CI, resampling *tasks* with replacement."""
    vals = np.array([fn(n, c, k) for n, c in counts.values() if n >= k])
    if vals.size == 0:
        raise ValueError(f"no task has >= {k} trials")
    rng = np.random.default_rng(seed)
    boots = rng.choice(vals, size=(n_boot, vals.size), replace=True).mean(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(vals.mean()), float(lo), float(hi)


def irreversible_error_rate(episodes: Iterable[dict]) -> float:
    """Mean number of erroneous IRREVERSIBLE or COMPENSABLE commits per episode.

    Each episode needs a 'ledger' list of dicts with 'effect' and 'erroneous' keys.
    """
    eps = list(episodes)
    if not eps:
        raise ValueError("no episodes")
    bad = {"IRREVERSIBLE", "COMPENSABLE"}
    return float(
        np.mean([sum(e["erroneous"] and e["effect"] in bad for e in ep["ledger"]) for ep in eps])
    )

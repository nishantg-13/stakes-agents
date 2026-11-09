"""Side-by-side comparison of several runs (one per mode) on the same tasks.

    uv run python -m stakes.compare results/demo_measure results/demo_unc_only \
        results/demo_verify_writes results/demo_stakes --out results/demo_comparison.json

Only tasks and trials present in *every* run are compared, so the conditions stay paired.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from stakes.metrics import (
    bootstrap_ci,
    irreversible_error_rate,
    pass_hat_k_task,
    per_task_counts,
)
from stakes.pilot import load_episodes

LABELS = {
    "measure": "Baseline (single run)",
    "unc_only": "Uncertainty-only",
    "verify_writes": "Verify every write",
    "stakes": "STAKES v0 (fixed rule)",
    "voc": "STAKES (VOC)",
}


def compare(run_dirs: list[Path]) -> dict:
    runs, base_mode, labels = {}, {}, {}
    for d in run_dirs:
        eps = load_episodes(d)
        cfg = json.loads((d / "run_config.json").read_text())
        base = cfg.get("mode", d.name)
        lam = cfg.get("lam")
        mode = base if lam is None else f"{base}@{lam:g}"  # several voc runs differ only by lam
        if mode in runs:
            raise ValueError(f"two run dirs map to the same condition {mode!r}")
        base_mode[mode] = base
        labels[mode] = LABELS.get(base, base) + ("" if lam is None else f", λ={lam:g}")
        runs[mode] = {(e["task_id"], e["trial"]): e for e in eps}
    common = set.intersection(*(set(r) for r in runs.values())) if runs else set()
    rows = []
    for mode, by_key in runs.items():
        eps = [by_key[k] for k in sorted(common)]
        counts = per_task_counts(eps)
        k_max = min(n for n, _ in counts.values())
        p1 = bootstrap_ci(counts, 1, pass_hat_k_task)
        pk = bootstrap_ci(counts, k_max, pass_hat_k_task) if k_max > 1 else None
        steps = [p for e in eps for p in e["probes"]]
        cost = [(e["agent_cost"] or 0) + (e["probe_cost"] or 0) for e in eps]
        toks = [
            e["agent_prompt_tokens"] + e["agent_completion_tokens"]
            + e["probe_prompt_tokens"] + e["probe_completion_tokens"]
            for e in eps
        ]
        # In "measure" mode probes are never executed: report its cost WITHOUT probe tokens,
        # since the baseline agent would not pay them.
        if base_mode[mode] == "measure":
            cost = [(e["agent_cost"] or 0) for e in eps]
            toks = [e["agent_prompt_tokens"] + e["agent_completion_tokens"] for e in eps]
        wrong_irrev = [
            sum(x["erroneous"] and x["effect"] in ("IRREVERSIBLE", "COMPENSABLE") for x in e["ledger"])
            for e in eps
        ]
        rows.append(
            {
                "mode": mode,
                "label": labels[mode],
                "n_episodes": len(eps),
                "n_tasks": len(counts),
                "success_rate": p1,  # pass^1 = pass@1, with 95% bootstrap CI over tasks
                f"pass^{k_max}": pk,
                "irreversible_error_rate": irreversible_error_rate(eps),
                "episodes_with_wrong_irreversible": float(np.mean([w > 0 for w in wrong_irrev])),
                "cost_per_episode_usd": float(np.mean(cost)),
                "tokens_per_episode": float(np.mean(toks)),
                "vote_switches": sum(p.get("switched_by_vote", False) for p in steps),
                "verified_steps": sum(p.get("verified", False) for p in steps),
                "verifier_revisions": sum(p.get("revised", False) for p in steps),
            }
        )
    return {"common_episodes": len(common), "rows": rows}


def to_markdown(report: dict) -> str:
    rows = report["rows"]
    kcol = next((k for k in rows[0] if k.startswith("pass^")), None) if rows else None
    head = ["Method", "Success (95% CI)", kcol or "pass^k", "Wrong irreversible / ep",
            "Cost / ep (USD)", "Tokens / ep", "Vote switches", "Verifier revisions"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        s = r["success_rate"]
        pk = r.get(kcol) if kcol else None
        out.append(
            "| " + " | ".join([
                r["label"],
                f"{s[0]:.2f} [{s[1]:.2f}, {s[2]:.2f}]",
                f"{pk[0]:.2f} [{pk[1]:.2f}, {pk[2]:.2f}]" if pk else "n/a",
                f"{r['irreversible_error_rate']:.2f}",
                f"{r['cost_per_episode_usd']:.3f}",
                f"{r['tokens_per_episode']:,.0f}",
                str(r["vote_switches"]),
                str(r["verifier_revisions"]),
            ]) + " |"
        )
    return "\n".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="stakes.compare")
    p.add_argument("run_dirs", nargs="+")
    p.add_argument("--out", default=None)
    args = p.parse_args(argv)
    report = compare([Path(d) for d in args.run_dirs])
    md = to_markdown(report)
    print(f"Paired episodes per method: {report['common_episodes']}\n")
    print(md)
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2))
        Path(args.out).with_suffix(".md").write_text(md + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

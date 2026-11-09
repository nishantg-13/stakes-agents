"""Go/no-go pilot: run the baseline tau2 agent with write-step probes, then analyse.

    uv run python -m stakes.pilot run --domain airline --split train \
        --agent-llm gemini/<model> --user-llm gemini/<model> --trials 4 --num-tasks 5
    uv run python -m stakes.pilot analyze results/<run-dir>

The run is resumable: finished (task, trial) episodes are skipped.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import stakes.tau2_setup  # noqa: F401  (must run before any tau2 import)
from stakes.effects import EffectRegistry
from stakes.episode import build_record
from stakes.probe_agent import MODES, ProbeAgent
from stakes.tau2_setup import REPO_ROOT, TAU2_COMMIT
from stakes.voc import VocParams

# Pre-registered thresholds (docs/decisions.md D-004). Do not change after seeing pilot data.
LOW_P_HAT = 1 / 3 + 1e-9  # "confident" = at most 1 of k0=3 candidates disagrees
GO_SHARE = 0.30
PIVOT_SHARE = 0.15


def _build(domain: str):
    from tau2.runner import build_environment

    env = build_environment(domain)
    return EffectRegistry.from_env(domain, env)


def cmd_run(args) -> int:
    from tau2 import TextRunConfig
    from tau2.evaluator.evaluator import EvaluationType
    from tau2.registry import registry as tau2_registry
    from tau2.runner import build_text_orchestrator, get_tasks, run_simulation

    effect_registry = _build(args.domain)
    missing = effect_registry.unlabeled()
    if missing:
        print(f"Unlabeled state-changing tools: {missing}", file=sys.stderr)
        return 2

    voc_params = None
    if args.mode == "voc":
        if not args.voc_params:
            print("--mode voc needs --voc-params (fit with python -m stakes.voc)", file=sys.stderr)
            return 2
        voc_params = VocParams.load(args.voc_params)

    out = Path(args.out or REPO_ROOT / "results" / f"pilot_{args.domain}_{args.split}")
    (out / "episodes").mkdir(parents=True, exist_ok=True)
    meta = {
        "domain": args.domain,
        "split": args.split,
        "agent_llm": args.agent_llm,
        "user_llm": args.user_llm,
        "agent_temperature": args.agent_temperature,
        "user_temperature": args.user_temperature,
        "k0": args.k0,
        "probe_temperature": args.probe_temperature,
        "probe_reads_frac": args.probe_reads_frac,
        "mode": args.mode,
        "verifier_llm": args.verifier_llm or args.agent_llm,
        "verifier_prompt": "v2",  # D-011: shared, effect-aware prompt + strict parse
        "lam": args.lam if args.mode == "voc" else None,
        "voc_params": voc_params.__dict__ if voc_params else None,
        "evaluation": "ENV (DB + env assertions only; no LLM judge)",
        "tau2_commit": TAU2_COMMIT,
    }
    cfg_path = out / "run_config.json"
    if cfg_path.exists():
        old = json.loads(cfg_path.read_text())
        if {k: old.get(k) for k in meta} != meta:
            print(f"{out} holds a run with a different config; use another --out", file=sys.stderr)
            return 2
    else:
        cfg_path.write_text(json.dumps({**meta, "created": _now()}, indent=2))

    tasks = get_tasks(args.domain, task_split_name=args.split, num_tasks=args.num_tasks)
    jobs = [
        (t, trial)
        for t in tasks
        for trial in range(args.trials)
        if not (out / "episodes" / f"{t.id}__t{trial}.json").exists()
    ]
    print(f"{len(tasks)} tasks x {args.trials} trials; {len(jobs)} episodes to run -> {out}")

    def run_one(task, trial):
        seed = args.seed + trial
        agent_name = f"stakes_probe_{task.id}_{trial}_{time.time_ns()}"
        holder = {}

        def factory(tools, domain_policy, **kw):
            agent = ProbeAgent(
                tools=tools,
                domain_policy=domain_policy,
                llm=kw.get("llm"),
                llm_args=kw.get("llm_args"),
                registry=effect_registry,
                k0=args.k0,
                probe_temperature=args.probe_temperature,
                probe_reads_frac=args.probe_reads_frac,
                probe_seed=seed * 1000 + zlib.crc32(task.id.encode()) % 1000,
                mode=args.mode,
                verifier_llm=args.verifier_llm,
                voc_params=voc_params,
                lam=args.lam,
            )
            holder["agent"] = agent
            return agent

        tau2_registry.register_agent_factory(factory, agent_name)
        config = TextRunConfig(
            domain=args.domain,
            agent=agent_name,
            llm_agent=args.agent_llm,
            llm_args_agent={"temperature": args.agent_temperature},
            llm_user=args.user_llm,
            llm_args_user={"temperature": args.user_temperature},
            max_steps=args.max_steps,
        )
        orch = build_text_orchestrator(config, task, seed=seed)
        result = run_simulation(orch, evaluation_type=EvaluationType.ENV)
        rec = build_record(
            result=result,
            task=task,
            trial=trial,
            seed=seed,
            registry=effect_registry,
            probes=holder["agent"].probe_dicts(),
            meta={k: meta[k] for k in ("domain", "split", "agent_llm", "user_llm", "k0", "mode", "lam")},
        )
        path = out / "episodes" / f"{task.id}__t{trial}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str))
        tmp.rename(path)  # atomic: a crash never leaves a half-written episode
        return rec

    failures = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_one, t, tr): (t.id, tr) for t, tr in jobs}
        for f in as_completed(futs):
            tid, tr = futs[f]
            try:
                r = f.result()
                print(f"  {tid} t{tr}: success={r['success']} reward={r['reward']}")
            except Exception:  # noqa: BLE001 - log any episode failure and continue
                failures += 1
                err = out / "errors.log"
                with err.open("a") as fh:
                    fh.write(f"--- {_now()} {tid} t{tr}\n{traceback.format_exc()}\n")
                print(f"  {tid} t{tr}: ERROR (see {err})")
    print(f"done; {failures} episode errors")
    return 1 if failures else 0


def load_episodes(run_dir: Path) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((run_dir / "episodes").glob("*.json"))]


def analyze(eps: list[dict], k_max: int | None = None) -> dict:
    from stakes.metrics import (
        bootstrap_ci,
        irreversible_error_rate,
        pass_at_k_task,
        pass_hat_k_task,
        per_task_counts,
    )

    counts = per_task_counts(eps)
    k_max = k_max or min(n for n, _ in counts.values())
    rel = {}
    for k in range(1, k_max + 1):
        m, lo, hi = bootstrap_ci(counts, k, pass_hat_k_task)
        a, alo, ahi = bootstrap_ci(counts, k, pass_at_k_task)
        rel[k] = {"pass^k": [m, lo, hi], "pass@k": [a, alo, ahi]}

    steps = [p for e in eps for p in e["probes"]]
    tool_steps = [p for p in steps if p["proposal"] != "<text>"]
    read_steps = [p for p in tool_steps if p["effect"] == "READ"]

    failed = [e for e in eps if not e["success"]]
    kinds: dict[str, int] = {}
    low_conf_wrong_write = 0
    wrong_write_by_effect: dict[str, int] = {}
    for e in failed:
        d = e["decisive_error"] or {"kind": "unknown"}
        kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
        if d["kind"] == "wrong_write":
            wrong_write_by_effect[d["effect"]] = wrong_write_by_effect.get(d["effect"], 0) + 1
            if d.get("p_hat") is not None and d["p_hat"] <= LOW_P_HAT:
                low_conf_wrong_write += 1

    succ = [e for e in eps if e["success"]]
    succ_writes = [x for e in succ for x in e["ledger"] if x["effect"] != "READ" and not x["tool_error"]]
    fp = sum(x["erroneous"] for x in succ_writes)

    share = low_conf_wrong_write / len(failed) if failed else float("nan")
    if not failed:
        decision = "NO DATA (no failures)"
    elif share >= GO_SHARE:
        decision = "GO"
    elif share >= PIVOT_SHARE:
        decision = "GO, lead with RQ1"
    else:
        decision = "PIVOT to Idea #2"

    return {
        "n_episodes": len(eps),
        "n_tasks": len(counts),
        "reliability": rel,
        "agent_cost_usd": sum(e["agent_cost"] or 0 for e in eps),
        "user_cost_usd": sum(e["user_cost"] or 0 for e in eps),
        "probe_cost_usd": sum(e["probe_cost"] or 0 for e in eps),
        "agent_tokens": sum(e["agent_prompt_tokens"] + e["agent_completion_tokens"] for e in eps),
        "probe_tokens": sum(e["probe_prompt_tokens"] + e["probe_completion_tokens"] for e in eps),
        "read_share_of_tool_steps": len(read_steps) / len(tool_steps) if tool_steps else None,
        "irreversible_error_rate": irreversible_error_rate(eps) if eps else None,
        "n_failed": len(failed),
        "decisive_error_kinds": kinds,
        "wrong_write_by_effect": wrong_write_by_effect,
        "confident_wrong_write_share_of_failures": share,
        "matcher_false_positive_rate": fp / len(succ_writes) if succ_writes else None,
        "probe_join_mismatches": sum(e["probe_join_mismatches"] for e in eps),
        "total_cost_usd": sum((e["agent_cost"] or 0) + (e["probe_cost"] or 0) for e in eps),
        "total_cost_per_episode_usd": (
            sum((e["agent_cost"] or 0) + (e["probe_cost"] or 0) for e in eps) / len(eps)
        ),
        "deliberation": {
            "sampled_steps": sum(p.get("probed", False) for p in steps),
            "vote_switches": sum(p.get("switched_by_vote", False) for p in steps),
            "verified_steps": sum(p.get("verified", False) for p in steps),
            "verifier_revisions": sum(p.get("revised", False) for p in steps),
        },
        "decision_rule": f"GO if share >= {GO_SHARE}; PIVOT if < {PIVOT_SHARE}; low p_hat <= 1/3",
        "decision": decision,
    }


def cmd_analyze(args) -> int:
    eps = load_episodes(Path(args.run_dir))
    if not eps:
        print("no episodes found", file=sys.stderr)
        return 2
    report = analyze(eps)
    text = json.dumps(report, indent=2)
    print(text)
    (Path(args.run_dir) / "analysis.json").write_text(text)
    return 0


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="stakes.pilot")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--domain", default="airline", choices=["airline", "retail"])
    r.add_argument("--split", default="train", help="tau2 split; 'train' is our dev split")
    r.add_argument("--agent-llm", required=True, help="LiteLLM id, e.g. gemini/<model>")
    r.add_argument("--user-llm", required=True)
    r.add_argument("--agent-temperature", type=float, default=0.0)
    r.add_argument("--user-temperature", type=float, default=0.0)
    r.add_argument("--k0", type=int, default=3)
    r.add_argument("--probe-temperature", type=float, default=1.0)
    r.add_argument("--probe-reads-frac", type=float, default=0.25)
    r.add_argument(
        "--mode",
        default="measure",
        choices=list(MODES),
        help="measure = baseline pilot (probes never executed); others act on deliberation",
    )
    r.add_argument("--verifier-llm", default=None, help="defaults to --agent-llm")
    r.add_argument("--voc-params", default=None, help="YAML from python -m stakes.voc (voc mode)")
    r.add_argument("--lam", type=float, default=0.0, help="price per LLM call (voc mode)")
    r.add_argument("--trials", type=int, default=4)
    r.add_argument("--num-tasks", type=int, default=None)
    r.add_argument("--max-steps", type=int, default=100)
    r.add_argument("--seed", type=int, default=300)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--out", default=None)
    r.set_defaults(func=cmd_run)
    a = sub.add_parser("analyze")
    a.add_argument("run_dir")
    a.set_defaults(func=cmd_analyze)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

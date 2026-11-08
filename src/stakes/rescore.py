"""Recompute ledgers and decisive errors for saved episodes, e.g. after a matcher fix.

    uv run python -m stakes.rescore results/demo_measure results/demo_stakes ...

Uses only what each episode file already records (tool calls, arguments, tool errors,
p-hat), plus the pinned tau2 task data. Makes no LLM calls. Rewrites the files in place.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from stakes.effects import EffectRegistry
from stakes.episode import gold_actions
from stakes.ledger import build_ledger, decisive_error


def rescore_dir(run_dir: Path) -> tuple[int, int]:
    from tau2.runner import build_environment, get_tasks

    cfg = json.loads((run_dir / "run_config.json").read_text())
    domain = cfg["domain"]
    reg = EffectRegistry.from_env(domain, build_environment(domain))
    tasks = {t.id: t for t in get_tasks(domain, task_split_name=cfg.get("split"))}
    changed = 0
    files = sorted((run_dir / "episodes").glob("*.json"))
    for path in files:
        rec = json.loads(path.read_text())
        calls = [
            {"turn": e["turn"], "name": e["name"], "arguments": e["arguments"], "error": e["tool_error"]}
            for e in rec["ledger"]
        ]
        p_hat = {(e["turn"], e["name"]): e.get("p_hat") for e in rec["ledger"]}
        ledger = build_ledger(calls, gold_actions(tasks[rec["task_id"]]), reg)
        for e in ledger.entries:
            e.p_hat = p_hat.get((e.turn, e.name))
        new_ledger = ledger.to_dicts()
        new_decisive = None if rec["success"] else vars(decisive_error(ledger))
        if new_ledger != rec["ledger"] or new_decisive != rec["decisive_error"]:
            changed += 1
        rec["ledger"] = new_ledger
        rec["unmatched_gold_writes"] = ledger.unmatched_gold_writes
        rec["decisive_error"] = new_decisive
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str))
        tmp.rename(path)
    return len(files), changed


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="stakes.rescore")
    p.add_argument("run_dirs", nargs="+")
    args = p.parse_args(argv)
    for d in args.run_dirs:
        n, changed = rescore_dir(Path(d))
        print(f"{d}: {n} episodes, {changed} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

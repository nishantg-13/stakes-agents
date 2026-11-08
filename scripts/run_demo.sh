#!/usr/bin/env bash
# Demo comparison: 4 modes on the same airline dev tasks. Usage: scripts/run_demo.sh [num_tasks] [trials]
set -euo pipefail
cd "$(dirname "$0")/.."
N="${1:-15}"; T="${2:-2}"
MODEL="gemini/gemini-2.5-flash"
COMMON=(--domain airline --split train --agent-llm "$MODEL" --user-llm "$MODEL"
        --num-tasks "$N" --trials "$T" --workers 4)
mkdir -p results/logs
uv run python -m stakes.pilot run "${COMMON[@]}" --mode measure --k0 3 --out results/demo_measure > results/logs/measure.log 2>&1 &
uv run python -m stakes.pilot run "${COMMON[@]}" --mode unc_only --k0 2 --probe-reads-frac 0 --out results/demo_unc_only > results/logs/unc_only.log 2>&1 &
uv run python -m stakes.pilot run "${COMMON[@]}" --mode verify_writes --k0 2 --probe-reads-frac 0 --out results/demo_verify_writes > results/logs/verify_writes.log 2>&1 &
uv run python -m stakes.pilot run "${COMMON[@]}" --mode stakes --k0 2 --probe-reads-frac 0 --out results/demo_stakes > results/logs/stakes.log 2>&1 &
wait || true
for m in measure unc_only verify_writes stakes; do
  n=$(ls "results/demo_$m/episodes" 2>/dev/null | wc -l | tr -d ' ')
  e=$( [ -f "results/demo_$m/errors.log" ] && grep -c '^---' "results/demo_$m/errors.log" || echo 0)
  echo "== $m: $n episodes, $e errors"
done

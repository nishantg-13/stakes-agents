#!/usr/bin/env bash
# Method comparison on the airline dev split, paired with the baseline pilot (same tasks, trials,
# seeds). Usage: scripts/run_comparison.sh [num_tasks] [trials] [lams...]
# Baseline = results/pilot_airline_measure (measure mode never changes the executed action).
set -euo pipefail
cd "$(dirname "$0")/.."
N="${1:-30}"; T="${2:-4}"; shift $(( $# >= 2 ? 2 : $# )) || true
LAMS=("${@:-0.03 0.1 0.2}"); read -r -a LAMS <<< "${LAMS[*]}"
MODEL="gemini/gemini-2.5-flash"
COMMON=(--domain airline --split train --agent-llm "$MODEL" --user-llm "$MODEL"
        --num-tasks "$N" --trials "$T" --workers 4 --k0 2 --probe-reads-frac 0)
mkdir -p results/logs
for m in unc_only verify_writes stakes; do
  uv run python -m stakes.pilot run "${COMMON[@]}" --mode "$m" --out "results/cmp_$m" \
    > "results/logs/cmp_$m.log" 2>&1 &
done
for l in "${LAMS[@]}"; do
  uv run python -m stakes.pilot run "${COMMON[@]}" --mode voc --voc-params params/tau2_airline.yaml \
    --lam "$l" --out "results/cmp_voc_$l" > "results/logs/cmp_voc_$l.log" 2>&1 &
done
wait || true
dirs=(results/pilot_airline_measure results/cmp_unc_only results/cmp_verify_writes results/cmp_stakes)
for l in "${LAMS[@]}"; do dirs+=("results/cmp_voc_$l"); done
uv run python -m stakes.compare "${dirs[@]}"

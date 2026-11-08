# STAKES: Stakes-Weighted Test-Time Deliberation for Tool-Using Agents

Research prototype. **Status: prototype.** Instrumentation, the go/no-go pilot and STAKES v0 are built
(32 offline tests). The first small comparison is preliminary (15 tasks × 2 trials).

The core idea: allocate an agent's extra test-time compute by **expected error cost**, i.e.
P(the action is wrong) × cost(the action is wrong, which depends on whether it is read-only,
reversible, compensable or irreversible), rather than by uncertainty alone.
The full design is in `~/agent-studio/research/06-proposal.md`.

## What exists now
| Module | Purpose |
|---|---|
| `registries/tau2_{airline,retail}.yaml` | Effect type for every state-changing tool, with a rationale for each |
| `stakes/effects.py` | EffectType, EffectRegistry; errors on any unlabelled write tool |
| `stakes/canon.py` | Canonical action keys, disagreement-based p̂ |
| `stakes/ledger.py` | Effect ledger vs the reference trajectory; decisive-error classification |
| `stakes/metrics.py` | pass^k / pass@k (unbiased), bootstrap CIs, irreversible-error rate |
| `stakes/probe_agent.py` | tau2 LLMAgent with 5 modes: `measure` (pilot probes), `uniform`, `unc_only`, `verify_writes`, `stakes` (v0) |
| `stakes/compare.py` | Paired side-by-side table across modes |
| `scripts/run_demo.sh` | Runs the 4-mode demo comparison |
| `report/stakes_prototype.html` | One-page project brief with the preliminary results |
| `stakes/pilot.py` | Resumable pilot runner and analysis with the pre-registered decision rule |
| `docs/decisions.md` | Decisions (D-###) and open assumptions (A-###) |

## Setup
```bash
uv sync
# tau2 task data (pinned commit), fetched into vendor/ (gitignored):
mkdir -p vendor && cd vendor && git init -q tau2-bench && cd tau2-bench \
  && git remote add origin https://github.com/sierra-research/tau2-bench \
  && git fetch -q --depth 1 origin 033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f \
  && git checkout -q FETCH_HEAD && cd ../..
cp .env.example .env   # then put your GEMINI_API_KEY in .env
uv run pytest          # offline; makes no API calls
```

## Run the pilot
```bash
# smoke test: 2 tasks x 1 trial (a few cents)
uv run python -m stakes.pilot run --domain airline --split train \
  --agent-llm gemini/<model> --user-llm gemini/<model> \
  --num-tasks 2 --trials 1 --out results/smoke

# full go/no-go pilot (dev split only)
uv run python -m stakes.pilot run --domain airline --split train \
  --agent-llm gemini/<model> --user-llm gemini/<model> --trials 4 --out results/pilot_airline
uv run python -m stakes.pilot analyze results/pilot_airline
```

The analysis prints:
- pass^k and pass@k with 95% CIs;
- cost and tokens (agent and probes reported separately);
- the share of tool steps that are reads;
- the irreversible-error rate;
- the breakdown of decisive errors;
- the matcher false-positive rate;
- the **GO / PIVOT** decision under rule D-004.

## Important caveats
- Success uses tau2's DB/environment check only (D-003). It is not comparable to the tau2
  leaderboard, which also uses LLM judges.
- "Erroneous write" is defined relative to one reference trajectory (A-003).

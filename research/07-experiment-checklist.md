# 07 — Experiment Checklist

Tick each box in order. Items marked **(gate)** block everything below them.

## A. Before any code
- [ ] Re-run the novelty searches in `checklists/novelty-recheck.md`, and log the date.
- [ ] Freeze the RQs, hypotheses and primary metric (pass^4 at B*) in `06-proposal.md` §4 and §13.
- [ ] Record the resource assumptions: GPU model and memory, Gemini tier and quota, monthly spend cap.
- [ ] Set a hard spending alert on the Gemini key.

## B. Environment setup
- [ ] τ²-bench cloned and pinned to a commit hash. One airline task runs end to end with Gemini Flash-tier.
- [ ] Confirm that τ²-bench gold actions and DB-state grading are accessible programmatically.
- [ ] Choose the user simulator model and temperature; freeze them for **all** conditions.
- [ ] AppWorld installed, version pinned, and one task runs end to end.
- [ ] AgentAbstain: verify code and data availability and the licence. If unavailable, drop it and note why.
- [ ] vLLM serves the open 7–8B model with tool calling. Parity check: 20 τ² tasks run without format errors.
- [ ] Token accounting reads provider usage fields (input / output / cached), never estimates.

## C. Instrumentation (gate)
- [ ] Effect registry YAML per τ² domain. Labelling protocol documented; second-annotator agreement reported.
- [ ] Canonicalizer unit tests cover argument order, whitespace, number formats and case.
- [ ] Ledger records pre/post DB diffs. Unit test: a known wrong write is flagged as erroneous.
- [ ] pass^k and pass@k estimators unit-tested against hand-computed examples. These must match
      τ-bench's definition.
- [ ] IER and duplicate-rate computed from the ledger, and unit-tested.
- [ ] The runner is resumable and caches by content hash; killing it mid-run loses nothing.

## D. Go/no-go pilot (gate — see `13-what-to-build-first.md`)
- [ ] 50 baseline τ²-airline episodes × k = 4 with Gemini Flash-tier.
- [ ] Locate each failed episode's decisive error step using gold actions; record its effect type
      and p̂.
- [ ] Decision rule (written down **before** looking at the data):
  - **GO**, if ≥ 30% of decisive errors are writes with low p̂ (H3a plausible).
  - **PIVOT** to Idea #2 (the compute–reliability audit) as the flagship, if < 15%.
  - In between: GO, but lead with RQ1.

## E. Fitting (dev split only)
- [ ] Dev/test split by task ID, committed to the repo, with a hash recorded.
- [ ] Fit φ_o(τ) and κ_o per (environment, model). Report CIs.
- [ ] Estimate the empirical C(τ). Define the stylised cost tables (3 variants).
- [ ] Choose the λ-grid (≈ 6 points) so the token range spans 1×–6× single-run cost.

## F. Main runs
- [ ] RQ1: uniform strategies × 3 budgets × k trials.
- [ ] RQ2: all baselines + STAKES × λ-grid × k trials, per (environment, model).
- [ ] Spot-check 10 trajectories per condition for harness bugs before scaling up.
- [ ] Track spend against the budget after every batch.

## G. Analysis
- [ ] Frontiers with bootstrap CIs (10k resamples over tasks).
- [ ] Paired permutation tests at B*. Holm correction across environments.
- [ ] RQ3 step-class decomposition (Table 3).
- [ ] RQ4 LedgerWorld ρ sweep (main-track version).
- [ ] RQ5 robustness: mislabel rates and cost-table scaling.
- [ ] RQ6 vs verify-before-write at every budget point.
- [ ] Failure taxonomy: 100 failed episodes annotated, with κ on a 30-episode overlap.
- [ ] Provider nondeterminism: 20 tasks × 5 repeats at temperature 0.

## H. Integrity
- [ ] No prompt changes after the first test-split run. Any change → rerun all conditions.
- [ ] LedgerWorld test seeds generated after code freeze.
- [ ] Every number in the paper traces back to a `results/` file via a script (no hand-copied numbers).
- [ ] ABC (E12) checklist filled in and attached.
- [ ] Cost reported for every row (AI Agents That Matter, E10).

## I. Release
- [ ] Repo public with licence. `make table1` … reproduces the open-model numbers.
- [ ] Trajectory logs uploaded (check licences).
- [ ] Model IDs, API dates, and the commit hashes of all benchmarks listed.

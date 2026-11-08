# Decisions and Assumptions

Append-only. Never rewrite a row; add a new one and mark the old one `Superseded`.
Research design: `~/agent-studio/research/06-proposal.md`.

## Decisions (D-###)

| ID | Date | Decision | Why | Status |
|---|---|---|---|---|
| D-001 | 2026-11-08 | Flagship = STAKES (stakes-weighted deliberation). | Chosen by Nishant from the shortlist (research/05). | Active |
| D-002 | 2026-11-08 | Environment: tau2-bench pinned at commit `033bf082`, airline and retail domains. | Reproducibility; DB-state grading; gold reference trajectories. | Active |
| D-003 | 2026-11-08 | Success = tau2 `EvaluationType.ENV` (DB + env assertions). No COMMUNICATE or NL_ASSERTION components. | Those components call OpenAI LLM judges (gpt-5.5, gpt-5.4-mini) we have no key for, and the proposal commits to judge-free metrics (W3). Consequence: our numbers are **not** comparable to the tau2 leaderboard. | Active |
| D-004 | 2026-11-08 | Pre-registered go/no-go rule. Share of failed episodes whose decisive error is a wrong write with p̂ ≤ 1/3 (k0 = 3): **≥ 0.30 → GO; 0.15–0.30 → GO, lead with RQ1; < 0.15 → PIVOT to Idea #2.** | Fixed before any data is seen, to avoid tuning the rule to the result. Thresholds live in `stakes/pilot.py`. | Active |
| D-005 | 2026-11-08 | Dev split = tau2 `train` (airline 30, retail 74). Test = tau2 `test` (20, 40). The pilot and all fitting use train only. | Keeps the test split untouched until method freeze. | Active |
| D-006 | 2026-11-08 | Probes are measurement-only: candidates are never executed, and probe tokens are logged separately from agent cost. | The pilot must measure the *baseline* agent, unchanged. | Active |
| D-007 | 2026-11-08 | STAKES v0 = voting (2 extra samples + proposal) on every write, plus an LLM policy verifier on every COMPENSABLE/IRREVERSIBLE write regardless of p̂. A verifier objection triggers one regeneration with the reviewer's note. Baselines: `unc_only` (vote at every tool step; verify only if p̂ > 0) and `verify_writes` (verify every write, no voting). | The smoke run showed a confident (p̂ = 0) irreversible policy violation that voting alone cannot catch. v0 is a fixed-rule approximation of the VOC allocator, so it is **not yet budget-matched**; the cost-matched λ-sweep comes next. | Active |
| D-008 | 2026-11-08 | `transfer_to_human_agents` stays IRREVERSIBLE for allocation, but can never be a "wrong write", because tau2 marks it non-mutating and success is DB-based. Its free-text `summary` is ignored when comparing samples. | The smoke run falsely flagged a transfer (p̂ = 1.0 purely from differently worded summaries) in a successful episode. | Active |
| D-009 | 2026-11-08 | Agent cost = sum of costed assistant messages. tau2's own `agent_cost` is None whenever its fixed greeting message (which has no cost) is present. | Found in the smoke run. | Active |
| D-010 | 2026-11-08 | Demo comparison: 15 airline train tasks × 2 trials × 4 modes, gemini-2.5-flash as agent and user. | Nishant approved the lean option (~$5–8) for the professor demo. Small-sample and preliminary. | Active |

## Assumptions (A-###), awaiting confirmation

| ID | Date | Assumption | How to confirm | Status |
|---|---|---|---|---|
| A-001 | 2026-11-08 | GPU size on the SSH server is unknown; it decides the open-model size (7–8B vs ~30B). | Nishant to report the GPU model and VRAM. | Open (non-blocking until W5) |
| A-002 | 2026-11-08 | Reversibility is **policy-compliant and agent-relative**: an action is REVERSIBLE only if the agent's own tools can undo it while following the domain policy. Labels and rationales are in `registries/*.yaml`. | Second-annotator review of both registries (checklist §C). | Open |
| A-003 | 2026-11-08 | "Erroneous write" = an executed write matching no remaining write in tau2's reference trajectory. This can false-flag valid alternative paths, so failures are attributed only in failed episodes, and the false-flag rate is measured on successful ones. | Inspect `matcher_false_positive_rate` in the pilot analysis; if > ~10%, refine the matching. | Open |
| A-004 | 2026-11-08 | Agent temperature 0 (tau2 default), probe temperature 1.0, user temperature 0. Every probe gets its own seed (tau2 pins a per-trial seed in `llm_args`). | Check in the smoke run that probes actually vary (p̂ is not always 0). | Open |
| A-005 | 2026-11-08 | Gemini model IDs (LiteLLM `gemini/<model>`) are chosen at run time and recorded in each run's `run_config.json`. | Confirmed by the smoke run. | Open |

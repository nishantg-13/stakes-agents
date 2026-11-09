# 09 — Week-by-Week Plan

- **Start date.** Mon 2026-11-16, after your Info Edge interview on Nov 14. Nothing here touches
  your interview-prep timetable.
- **Load.** Assumes about 15–20 h/week alongside your job. If you have less, stretch Phase 1
  rather than cutting its gates.
- **Deadlines** are approximate; verify them on the venue sites in early January.

## Phase 1 — Workshop paper (W1–W12)

| Week | Dates | Goal | Concrete deliverables | Exit check |
|---|---|---|---|---|
| W1 | Nov 16–22 | Ground yourself and the environment | Read the Tier-1 papers in `10-reading-order.md`. Clone and pin τ²-bench; run 10 airline tasks with Gemini Flash-tier; note cost per task. | Can explain pass^k and τ² grading from memory; know the cost per episode |
| W2 | Nov 23–29 | Instrumentation | Repo skeleton (`08-repo-structure.md`). Effect registries for τ² airline + retail. Ledger with DB diffs. pass^k/IER metrics + unit tests. | Tests green; a known wrong write is flagged |
| W3 | Nov 30–Dec 6 | **Go/no-go pilot** | 50 tasks × k=4 baseline. Decisive-error analysis by effect type and p̂ (`13-what-to-build-first.md`). | **GO / PIVOT decision written in `docs/decisions.md`** |
| W4 | Dec 7–13 | Operators | Canonicalizer, disagreement estimator, o₁ vote, o₂ read-back, o₃ verify. Uniform baselines working. | 10 hand-checked trajectories per operator |
| W5 | Dec 14–20 | Allocator + fitting | VOC allocator in all modes. Algorithm 3 on the dev split; φ, κ, C tables. | Allocator unit tests; fitted tables with CIs |
| W6 | Dec 21–27 | *Holiday buffer* (light) | vLLM open-8B serving; tool-call parity check. | 20 tasks run on the open model without format errors |
| W7 | Dec 28–Jan 3 | *Holiday buffer* (light) | LedgerWorld v0: 2 services, one ρ knob, ~100 tasks, scripted user. | Exact-state grader tested |
| W8 | Jan 4–10 | RQ1 runs | Uniform strategies × 3 budgets × k=4, τ² airline + retail, both models. | Table 2 filled |
| W9 | Jan 11–17 | RQ2 runs | All baselines + STAKES × λ-grid. | Table 1 (τ² rows) + frontier figure |
| W10 | Jan 18–24 | Analysis | RQ3 decomposition; LedgerWorld v0 ρ sweep; 50-episode error taxonomy. | Tables 3–4 drafted |
| W11 | Jan 25–31 | Write | 4–6 page workshop paper: intro, formulation, method, results, limitations. | Full draft |
| W12 | Feb 1–7 | Polish + submit | Internal read (ask one peer); fix figures; anonymise; submit to an ICLR 2027 workshop (non-archival preferred). | **Submitted** |

## Phase 2 — Main-track paper (W13–W26, target NeurIPS 2027, ~mid-May)

| Week | Goal | Deliverables |
|---|---|---|
| W13–14 | LedgerWorld v1 | 4 services; ρ ∈ {0, .1, .25, .5}; trap-density knob; 300 tasks per level; test seeds generated after freeze |
| W15 | AppWorld adapter | Registry, ledger hooks, parity run |
| W16 | AgentAbstain adapter (if public) | Paired tasks running; commit-check grading only |
| W17 | o₄ ask/abstain rung | User-simulator hook for τ²; scripted user for LedgerWorld; interruption metric |
| W18–19 | Robustness | LLM effect typer + accuracy; mislabel injection; cost-table scaling; logprob p̂ for open models |
| W20–22 | Full runs | All environments × 3–4 models (add a Pro-tier subset and an open ~30B model if the GPU allows) × k=8 |
| W23 | Ablations | Table 6; 100-episode error taxonomy with second-annotator κ |
| W24 | Theory | Prove or bound the §3 proposition, or drop it and say so honestly |
| W25 | Write | Full 9-page paper + appendix (ABC checklist, cost tables, prompts) |
| W26 | Submit | Code + logs release prep; submit |

## Weekly habits
- Monday: write the week's goal in `docs/decisions.md`, and log any new assumption as an A-### row.
- Friday: append a continuity entry (what was done, where you stopped, spend so far).
- Run the monthly novelty re-check (`checklists/novelty-recheck.md`) in the first week of each
  month.

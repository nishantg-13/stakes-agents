# 05 — Ranking, Shortlist, Recommendation

> **Status: DECIDED 2026-11-08: you chose #1. Resources: paid Gemini key + GPU. Venue: workshop first, then main track.** Scores are my judgement (1–5) and are not measured.
> "Cost" is scored so that **5 = cheapest**.
> Weights: novelty 0.25 · feasibility 0.20 · impact 0.25 · evaluation clarity 0.15 · cost 0.15.

## Full ranking

| Rank | Idea | Nov | Feas | Impact | Eval | Cost | **Weighted** | Novelty risk |
|---|---|---|---|---|---|---|---|---|
| 1 | **#1 Stakes-weighted deliberation** | 4 | 4 | 5 | 4 | 3 | **4.10** | med–high |
| 2 | #5 Context under prompt-cache economics | 3 | 5 | 3 | 5 | 5 | **4.00** | medium |
| 3 | #3 Utility-calibrated ask/abstain | 4 | 4 | 4 | 3 | 4 | **3.85** | medium |
| 4 | #4 Points of no return | 4 | 3 | 4 | 4 | 3 | 3.65 | medium |
| 4 | #7 Attribution-guided harness repair | 4 | 3 | 4 | 4 | 3 | 3.65 | medium |
| 6 | #2 Does compute buy reliability? | 3 | 4 | 4 | 5 | 2 | 3.60 | medium |
| 6 | #8 Effect-evidence contracts | 2 | 5 | 3 | 4 | 5 | 3.60 | high |
| 8 | #9 Multi-hop memory invalidation | 3 | 4 | 3 | 4 | 4 | 3.50 | med–high |
| 8 | #10 Single-vs-MAS reliability router | 3 | 4 | 3 | 4 | 4 | 3.50 | medium |
| 10 | #6 Harness overfitting | 3 | 3 | 4 | 5 | 2 | 3.40 | high |
| 11 | #11 MCP tool re-exposure | 2 | 4 | 3 | 4 | 4 | 3.25 | high |
| 12 | #12 Compact state + archive (RL) | 3 | 2 | 4 | 4 | 1 | 2.90 | medium |

Sensitivity check:
- If **impact** is weighted higher (0.35, with cost at 0.05), #5 drops to 4th, and #4 and #7 move
  up next to #3.
- #1 stays first under every reasonable weighting I tried.
- #5 ranks high mainly because it is cheap. It would make a good fast side paper, not the flagship.

## Top-3 decision table

| Criterion | #1 Stakes-weighted deliberation | #3 Ask/abstain policy | #5 Prompt-cache economics |
|---|---|---|---|
| Core claim | Allocating compute by *expected error cost* beats uncertainty-only allocation on reliability per token | A calibrated utility policy beats prompted/threshold abstention on utility-vs-interruption | Cache-stable compaction minimises USD per solved task |
| Closest prior art | CATTS, AVA (uncertainty-only, no side effects); Irreversibility Budget (admission only) | AgentAbstain (benchmark only); 2602.11619 (signal, not policy) | H18 Complexity Trap; ACON; CommitKV/SparseRead (serving side) |
| Novelty argument strength | Strong: two literatures that don't cite each other | Medium: method on a new benchmark | Medium: economics framing |
| Reviewer-proofness | Needs matched-compute curves plus a cost-table sensitivity analysis | Needs non-LLM ground truth for "should ask" | Pricing churn invites the critique "this is engineering" |
| Infrastructure | API + 1 GPU; τ²-bench, AgentAbstain, AppWorld | API; depends on AgentAbstain release | API only; cheapest |
| Est. API cost | ~$1.5–4k (estimate) | ~$0.5–1.5k | ~$0.3–1k |
| Time to first signal | ~3 weeks | ~2 weeks | ~1 week |
| Venue fit | NeurIPS / ICLR / ICML main, COLM | ACL / EMNLP / COLM | EMNLP / COLM short, MLSys workshop |
| Scoop risk | Medium–high (CATTS/AVA authors could add stakes) | Medium | Medium |
| Composability | Can absorb #3 (the "ask" rung) and #2 (its RQ1) | Can be a component of #1 | Independent |

## Recommendation (my view, before your input)

**Pursue #1, Stakes-Weighted Deliberation, as the flagship paper:**
- fold #2 in as its first research question ("does compute buy reliability at all?");
- fold #3 in as the top rung of its operator ladder;
- keep #5 as an optional quick side paper.

Why #1:
1. **The novelty argument is structural, not incremental.** It joins two 2026 literatures, adaptive
   test-time compute and irreversibility/side-effects, that currently don't address each other's
   problem. It grounds the joint in a classical principle, the value of computation.
2. **Evaluation is state-grounded.** τ²-bench, AgentAbstain and AppWorld all grade by environment
   state, so the headline metrics avoid LLM judges (W3).
3. **Feasible for one person.** The method is harness middleware, with no training required. Open
   models make it reproducible.
4. **Falsifiable.** H2 predicts *where* gains come from: high-stakes, low-uncertainty steps. A
   per-step breakdown can refute it.
5. **It still yields a paper if H1 fails.** The compute-matched reliability analysis (#2) remains
   a contribution: "uncertainty-only allocation is sufficient", or "no allocation buys reliability".

## Questions for you (please answer before I write the proposal)

1. Do you agree with **#1**, or would you rather pursue #3, #5, or another idea as the flagship?
2. **Budget and compute:** roughly how much API spend and GPU access can you commit?
3. **Target venue and deadline:** which do you have in mind? This sets the timeline in the proposal.

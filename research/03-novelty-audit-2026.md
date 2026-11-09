# 03 — Novelty Audit Against 2026 Frontier Work

> **Why this file exists.** The five slice reviews proposed about 30 "open problems". Before
> ranking ideas, I searched (2026-11-08) for each leading candidate. Several had been published in
> the preceding 3–9 months. A research idea written from the slice reviews alone would have gone
> to reviewers already scooped. This file records what was found, so the novelty claims in
> `04-research-ideas.md` can be audited.
>
> **Verification levels:**
> - **[V]** = I read the arXiv abstract page or the venue page myself.
> - **[S]** = seen only in search-result snippets. Treat as a lead and verify before citing.

## A. Papers that close or narrow candidate ideas

| Candidate idea (from slice reviews) | 2026 work found | Level | Status |
|---|---|---|---|
| Counterfactual-replay failure attribution on Who&When | AgenTracer (arXiv 2509.03312): counterfactual replay plus fault injection to label root causes. Causal Agent Replay (2606.08275): resamples a step under the same policy; validated on planted cases. EMFA (2610.11600): error propagation plus counterfactual verification; SOTA step-level on Who&When. DCFA (2609.04749). | [S] | **Closed.** The residual gap is attribution → *automatic repair* (Idea 7). |
| Memory poisoning against real memory systems (Mem0, A-MEM) | MemPoison (2605.29960; reported as accepted at ACM CCS 2026): bypasses extract/rewrite pipelines; ASR up to 0.95 on A-Mem, LangMem, Mem0. GhostWriter (2607.06595): five architectures including A-Mem and Mem0. Systematic study (2606.04329). | [S] | **Closed.** |
| Context rot inside multi-turn agent trajectories | "Diagnosing and Mitigating Context Rot in Long-horizon Search" (2606.29718): four models, three benchmarks; parallel sampling vs context management. "Self-Compacting LM Agents" (2606.23525). ACM (2607.23809). | [S] | **Mostly closed** for search agents. Coding remains, but that alone is incremental. |
| Irreversibility / side-effect benchmark | AgentAbstain (2607.10059): 263 paired tasks, 42 sandboxes, 17 LLMs, 4 harnesses; best 59.5% paired accuracy; names "post-hoc abstention". LIMBO / "Where Does Exactly-Once Live?" (2609.29095): 25,930 episodes; idempotency keys cut duplicates from 28% to 4%; agents report success in 90% of duplicated episodes. LPS-Bench (2602.03255): NeurIPS 2026 E&D track, 570 cases. | [V] | **Closed as a benchmark.** These become *evaluation substrates* for us. |
| Effect-aware checkpoint and rollback | ACRFence (2603.20625; CoDAIM workshop 2026): replay-or-fork semantics with an effect log. DART (2605.23311): admissible restore points. DeltaBox (2605.22781). | [V] | **Closed** at the runtime level. |
| Reversibility taxonomy | "Revisable by Design" (2604.23283): idempotent, reversible, compensable, irreversible; Revision Absorber, an earliest-conflict rollback rule for *user revisions*. | [V] | We **reuse** the taxonomy and cite it. |
| Fleet-level irreversibility control | "The Irreversibility Budget" (2609.00275; SOSP AgenticOS workshop 2026): value-at-risk accounting and admission control; per-action gates overdraw up to 48×. Does **not** allocate deliberation compute. | [V] | Adjacent. Its open problem, effect pricing, is relevant to us. |
| False success / overclaiming | "Characterizing False Success in LLM Agents" (2606.09863): 9,876 τ²-bench trajectories; dual control suppresses false success 10×. "Quantifying Overclaiming Propensity" (2609.20812). | [S] | **Closed as measurement.** |
| Belief / state drift in long-horizon agents | "Beyond Memory… Explicit Belief States" (2610.01415). "Can Agent Memory Systems Track Evolving State?" (2608.19652). EnvProbe (2606.31422). Agent-BRACE (2605.11436). | [S] | **Crowded.** |
| MAS shared-state concurrency | "Verified Detection and Prevention of Concurrency Anomalies in MAS" (2606.17182). "LM Teams as Distributed Systems" (2603.12229). S-Bus (2605.17076). CodeCRDT (2510.18893). | [S] | **Crowded.** |
| Cache-aware context management | CommitKV (2608.07855). SparseRead (2608.22237). IntentKV (2606.09916). AGORA (2605.26596). | [S] | **Narrowed** on the serving side. The *API-economics* angle remains (Idea 5). |
| Reliability metrics beyond pass@1 | Towards a Science of AI Agent Reliability (2602.16666; ICML 2026): 12 metrics, 15 models, GAIA plus a τ-bench airline subset. **Tests no interventions and no matched compute** (checked in the paper body). | [V] | Defines our *metrics*, not our method. |
| Uncertainty-triggered per-step compute in agents | CATTS (2602.12276; preprint): vote entropy and margin decide when to spend more compute; WebArena-Lite, Online-Mind2Web, GoBrowse; up to 11.8% over majority voting. **Uncertainty only; no stakes or irreversibility; no pass^k.** AVA, Anytime Verified Agents (TMLR 2026; openreview.net/forum?id=JMDCMf7mlF): allocates across search, sampling and verification by uncertainty and marginal reliability gain; GSM8K, MATH, HotpotQA, HumanEval. **No side-effecting actions, no stakes weighting.** | [V] | **The closest prior art for our recommended idea.** We must beat CATTS-style allocation as a baseline. |
| Action-level voting for reliability | Six Sigma Agent (2601.22290; preprint): per-action consensus over diverse LLMs; claims rest on an independence assumption, with no public benchmark visible in the abstract. Behavioral Consistency (2602.11619; ICML'26 UQ workshop): voting adds only about 0–2 pp in multi-step settings; divergence concentrates at step 2. | [V] | Motivation for *selective*, not uniform, deliberation. |

## B. What survives (summarised; full ideas in `04-research-ideas.md`)

1. **Stakes-weighted test-time compute for side-effecting agents** (Idea 1). This combination does
   not appear in any of the work above:
   - the per-step allocation signal is **expected error cost**, not uncertainty alone;
   - the actions have **real, partly irreversible side effects**;
   - the outcome is reported as **reliability** (pass^k, irreversible-error rate);
   - everything is compared **at matched compute**.
2. **Does test-time compute buy reliability?** (Idea 2). Rabanser et al. explicitly tested no
   interventions.
3. **Utility-calibrated ask/abstain policies** (Idea 3). AgentAbstain is a *benchmark*; a
   *method* evaluated on it is open.
4. **Ideas 4–12** are narrower or costlier. Each carries its own novelty-risk note.

## C. How to keep this audit current

The field is moving month by month. Before submitting:
- re-run the searches in `checklists/novelty-recheck.md`;
- set an arXiv alert on: "test-time compute agent", "irreversible", "side effect", "pass^k",
  "abstain agent", "value of computation LLM".

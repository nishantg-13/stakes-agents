# 04 — Research Ideas (12)

> **Conventions**
> - **Established** = supported by a cited paper (IDs from `01-literature-matrix.md`, 2026 work
>   from `03-novelty-audit-2026.md`).
> - **Hypothesis** = ours. Nothing in this file has been run, and none of these numbers are results.
> - **Difficulty**: S = 1 person, about 6 weeks · M = about 10–12 weeks · L = 4+ months, or needs
>   training compute.
> - **Novelty risk** = how likely a near-identical paper appears before submission, given the 2026
>   pace.

---

## Idea 1 — Stakes-Weighted Deliberation: test-time compute allocated by expected error cost (★ recommended)

- **Research question.** When an agent acts in a world with side effects, does allocating extra
  deliberation (sampling, verification, look-ahead) by **expected error cost** improve reliability
  per token more than uniform or uncertainty-only allocation? Expected error cost is
  P(error) × cost(error | action reversibility, position, scope).
- **Motivation and gap.**
  - Established:
    - Uniform per-step compute saturates (CATTS).
    - Uniform voting adds only about 0–2 pp in multi-step tasks, because early errors lock in (2602.11619).
    - Agents commit irreversible actions before noticing they should not (AgentAbstain).
    - Duplicate and irreversible effects are frequent and falsely reported as success (LIMBO).
    - Uncertainty-only allocation exists (CATTS, AVA), but on side-effect-free tasks and without
      cost weighting.
  - Gap: no method uses action **stakes** to allocate *deliberation*. The Irreversibility Budget
    uses stakes for admission control, not for thinking.
- **Hypothesis.**
  - H1: At matched total tokens, stakes-weighted allocation raises pass^k and lowers the
    irreversible-error rate more than uniform and uncertainty-only allocation. The gain is larger
    in domains with a higher share of irreversible actions.
  - H2: The gain comes mainly from steps that are *high-stakes but low-uncertainty*, where
    uncertainty-only methods spend nothing. That is, confident-but-wrong commits.
- **Proposed method.** A harness-level controller, *STAKES*.
  1. **Effect typing.** Each tool call is typed using the four classes from Revisable by Design:
     idempotent, reversible, compensable, irreversible. Typing comes from tool metadata, with an
     LLM fallback classifier.
  2. **Error-probability estimate.** A cheap estimate of p̂(error) from behavioural disagreement
     across k₀ = 2–3 samples (the CATTS / 2602.11619 signal).
  3. **Value-of-computation rule.** Classical metareasoning (Russell & Wefald) sets the
     deliberation budget for step t:
     `b_t ∝ p̂_t · c(type_t, scope_t) · g(b)`
     - `c` is a cost table: irreversible ≫ compensable > reversible > read.
     - `g` is a learned or fitted marginal-fix curve.
  4. **Escalating deliberation operators.** In increasing cost:
     - (a) resample and vote;
     - (b) environment read-back / precondition check (state-grounded, which avoids W3);
     - (c) critic or verifier pass;
     - (d) ask-the-user, where the benchmark supports it.
- **System architecture.** Agent ↔ STAKES middleware ↔ tool layer. The middleware holds:
  - an effect-type registry;
  - a disagreement estimator;
  - a budget allocator with a global token budget B;
  - the operator ladder;
  - an effect ledger for evaluation.

  The middleware is model-agnostic and wraps any tool-calling loop. The diagram is in
  `06-proposal.md`.
- **Data and infrastructure.** Environments (all public):
  - τ²-bench (airline, retail, telecom; DB-state grading);
  - AgentAbstain (paired act/abstain, deterministic commit check);
  - AppWorld (programmatic state tests);
  - LIMBO, if its code is released (unverified).

  Models: 2 API models plus 2 open-weight models (e.g. Qwen-class 7–32B via vLLM). Budget:
  roughly USD 1.5–4k of API spend, or 1×A100/H100 for the open models (estimate).
- **Baselines.**
  - Single run.
  - Uniform self-consistency per step at matched B.
  - Best-of-N trajectories at matched B.
  - Reflexion-style retry.
  - CATTS-style uncertainty-only allocation.
  - AVA-style allocation, where reimplementable.
  - Always-verify-before-write.
  - Oracle stakes (an upper bound).
- **Evaluation metrics.**
  - pass^1 and pass^k (k = 4, 8).
  - **Irreversible-error rate**: wrong irreversible commits per episode.
  - Duplicate-effect rate.
  - Harm-weighted utility.
  - Tokens and USD.
  - Paired accuracy on AgentAbstain.
  - The Rabanser reliability profile: consistency, robustness, predictability.
  - All reported as cost–reliability curves with bootstrap CIs.
- **Ablations.**
  - Remove the stakes term (reduces to uncertainty-only).
  - Remove the uncertainty term (stakes-only).
  - Coarse vs fine effect typing.
  - Learned vs LLM-inferred effect types.
  - Each operator rung alone.
  - Budget-allocation curve g: fitted vs constant.
  - Sensitivity to the cost table.
  - Noise injected into effect typing (robustness to mislabelled tools).
- **Risks and failure modes.**
  - Gains may be concentrated in a few tasks.
  - The cost table could look hand-tuned. Mitigation: a sensitivity analysis, plus a learned variant.
  - An LLM-inferred effect type could be wrong for novel tools.
  - The benchmarks' share of irreversible actions may be low, so the effect is small. Mitigation:
    report per-domain results and use AgentAbstain/LIMBO, where irreversibility is central.
  - A concurrent paper may appear. Mitigation: move fast and frame the work as decision-theoretic.
- **Difficulty.** M.
- **Novelty and publication strength.** High novelty as a *combination*. A clean decision-theoretic
  story plus strong empirical design suits NeurIPS, ICLR, ICML, or COLM. Novelty risk: medium–high,
  because CATTS and AVA authors could extend to stakes. Speed matters.

---

## Idea 2 — Does Test-Time Compute Buy Reliability? A compute-matched reliability audit of agent strategies

- **Research question.** At matched tokens, do reflection, voting, best-of-N, verifier gating,
  multi-agent debate/orchestration, and extra reasoning effort improve **reliability** (pass^k,
  outcome consistency, robustness) or only pass@1?
- **Motivation and gap.**
  - Rabanser et al. (ICML 2026) define 12 reliability metrics but test no interventions, at
    temperature 0 with one scaffold. They name scaffolds as future work.
  - W1 shows architecture gains often vanish at matched compute, but only on pass@1.
- **Hypothesis.** Strategies that raise pass@k (diversity) can *lower* pass^k (consistency).
  Verification-gated strategies raise pass^k most per token. Failures are correlated across
  trials, so p^k independence predictions overestimate reliability (testable).
- **Proposed method.** A factorial study: 6 strategies × 4 models × 3 benchmarks × 3 budget
  levels × k = 8 trials. We fit mixed-effects models separating task, strategy and seed variance.
- **Architecture.** A unified harness (OpenHands- or τ²-compatible) with a strategy plug-in API
  and a token-accounting layer.
- **Data and infrastructure.** τ²-bench, AppWorld, a SWE-bench Verified mini subset, and GAIA
  validation. API budget is the main cost; this is the costliest empirical design here.
- **Baselines.** Single run at temperature 0 and at temperature 0.7.
- **Metrics.**
  - pass@k and pass^k.
  - Rabanser C_out, R_prompt, R_fault, P_AUROC.
  - The correlation of failures across trials (intra-class correlation).
  - Cost.
- **Ablations.** Temperature; budget level; model family; the open vs closed split.
- **Risks.** A "negative results" framing may get a lukewarm reception. Cost can explode.
  Overlap with Idea 1 (it could be Idea 1's §RQ1).
- **Difficulty.** M (cost-heavy).
- **Novelty and publication strength.** Medium–high. Suits a NeurIPS D&B / E&D track or a main
  track with a strong analysis. Novelty risk: medium.

---

## Idea 3 — Utility-Calibrated Ask-or-Abstain Policies

- **Research question.** Can a lightweight policy decide among *act / ask the user / abstain*
  using black-box signals (behavioural disagreement, effect type, verifier score) to maximise
  expected utility under an explicit interruption cost?
- **Motivation and gap.**
  - AgentAbstain shows abstention is largely independent of task skill (best 59.5% paired accuracy).
  - Agent uncertainty work stops at AUROC (SAUP, UProp; W7 in L5).
  - The ICML'25 UQ position paper argues the current framing does not fit interactive agents.
  - Interactive clarification raised pass^3 from 0.357 to 0.634 for one model in a computer-use
    study (2604.17849, search-level only).
- **Hypothesis.** A calibrated utility policy dominates the following on utility-vs-interruption
  curves:
  - always-act;
  - prompt-instructed abstention;
  - threshold-on-confidence policies.
- **Method.** Features feed a small calibrated classifier (logistic regression or GBDT), trained
  on AgentGen-style synthetic pairs. Decisions follow a decision-theoretic threshold with a cost
  of asking λ, and conformal risk control bounds the harmful-act rate.
- **Architecture.** Policy middleware before each state-changing tool call, plus a user-simulator
  hook (τ²).
- **Data and infrastructure.** AgentAbstain (if code and data are public; to verify), τ²-bench
  dual-control, and our own perturbation generator.
- **Baselines.**
  - Always-act.
  - Prompted "ask if unsure".
  - Self-reported confidence threshold.
  - Consistency threshold (2602.11619).
  - Split-conformal baseline.
- **Metrics.**
  - Paired accuracy.
  - Harmful-act rate.
  - Interruption rate.
  - Utility at λ ∈ {0.05, 0.1, 0.3}.
  - The risk–coverage curve.
- **Ablations.** Feature groups; calibration method; λ sensitivity; cross-benchmark transfer.
- **Risks.** Dependence on the AgentAbstain release. The user simulator is itself an LLM (W3).
- **Difficulty.** S–M.
- **Novelty and publication strength.** Medium–high. Suits ACL, EMNLP, or COLM. Novelty risk:
  medium. It complements Idea 1 and could be its "ask" rung.

---

## Idea 4 — Points of No Return: estimating when an agent trajectory becomes unrecoverable

- **Research question.** Can we predict, from a trajectory prefix, whether the task is still
  recoverable? Can that prediction drive *restart-vs-continue* decisions that save compute and
  raise success?
- **Motivation and gap.**
  - Divergence concentrates early, around step 2 (2602.11619).
  - Drift precedes action collapse in 49% of spatial episodes (EnvProbe, search-level).
  - Causal Agent Replay estimates per-step causal effect, but not prefix *recoverability* as a
    control signal.
- **Hypothesis.** A recoverability estimator trained on Monte-Carlo continuations from prefixes
  achieves useful AUROC (≥ 0.75; a target, not a claim). Restarting at predicted points of no
  return beats continuing at equal compute.
- **Method.** For each prefix, run M continuations. The recoverability label is the fraction that
  succeed. Train a probe on prefix features (text embedding, disagreement, effect ledger), then
  run a restart policy.
- **Data and infrastructure.** τ²-bench or AppWorld rollouts. Cost is high, because labels need
  M × prefixes continuations. Feasible with an open model on one GPU.
- **Baselines.** Never restart; restart on fixed step count; restart on a self-assessed failure flag.
- **Metrics.** Recoverability AUROC and calibration; success at matched compute; wasted tokens.
- **Ablations.** Feature sets; M; prefix depth; cross-model transfer of the probe.
- **Risks.** Label noise; expensive labelling; restart is impossible after irreversible effects
  (a nice tie-in to Idea 1).
- **Difficulty.** M.
- **Novelty and publication strength.** Medium–high. Novelty risk: medium (close to CAR, AgenTracer).

---

## Idea 5 — Context Engineering Under Prompt-Cache Economics

- **Research question.** Under real provider prompt-cache pricing (cached vs uncached input
  tokens), which context-management strategy minimises USD per solved task? Can a "cache-stable"
  compaction rule beat masking and summarisation?
- **Motivation and gap.**
  - Masking ≈ summarisation at about half the token cost (H18).
  - ACON and ACE optimise tokens, not dollars under caching.
  - Compression breaks prefix reuse (W6).
  - Serving-side work (CommitKV, SparseRead) is self-hosted, not at the API-economics level.
- **Hypothesis.** Once cache pricing is included, aggressive summarisation loses its advantage.
  Append-only, block-boundary compaction gives the best USD per success.
- **Method.**
  - Strategies: full history; masking; LLM summarisation; ACE playbook; and our cache-stable
    compaction (compact only at fixed block boundaries, keeping a stable system prefix and moving
    volatile state to the tail).
  - Measure cached-token fractions from provider usage fields.
- **Data and infrastructure.** SWE-bench Verified mini and AppWorld; 2–3 providers with cache
  pricing.
- **Baselines.** The four strategies above.
- **Metrics.** USD per success; cache-hit fraction; latency; pass@1; pass^k.
- **Ablations.** Block size; position of volatile state; provider.
- **Risks.**
  - Provider pricing changes, so results age quickly. Mitigation: parametrise the cost model.
  - Reviewers may see the work as engineering.
- **Difficulty.** S.
- **Novelty and publication strength.** Medium. Suits an EMNLP or COLM short paper, or an MLSys
  workshop. Novelty risk: medium.

---

## Idea 6 — Harness Overfitting: do scaffold improvements transfer across models?

- **Research question.** How much of a harness's benchmark gain is model-specific? Can we measure
  "harness overfitting" and design robust harnesses?
- **Motivation and gap.**
  - HAL (H6) shows scaffold effects.
  - SWE-agent shows interface effects of 3–8 points.
  - Rabanser et al. list scaffolds as future work.
  - Nobody measures the harness × model interaction explicitly.
- **Hypothesis.** A large share of reported scaffold gains is an interaction effect. Harness
  components tuned on model A lose much of their gain on model B.
- **Method.** One-factor-at-a-time component swaps (prompt template, action format, observation
  formatting, retry rule) across 5 models, with a variance decomposition.
- **Data and infrastructure.** SWE-bench Verified mini, τ²-bench, GAIA. High API cost.
- **Baselines.** Default harnesses (OpenHands, SWE-agent, ReAct).
- **Metrics.** Interaction variance share; the transfer gap.
- **Ablations.** Component granularity; model size.
- **Risks.** Combinatorial cost. HAL's authors are well placed to scoop it.
- **Difficulty.** M–L.
- **Novelty and publication strength.** Medium. Novelty risk: high.

---

## Idea 7 — From Failure Attribution to Automatic Harness Repair

- **Research question.** Can attributed failures automatically produce harness patches (prompt
  rules, tool-description edits, guard checks) that improve held-out performance without
  overfitting?
- **Motivation and gap.** Attribution methods (Who&When, AgenTracer, EMFA) report *accuracy*.
  Whether attributions lead to *repairs* that improve held-out performance is untested (W7).
- **Hypothesis.** Attribution-guided patches outperform unguided self-improvement (ACE-style
  playbooks, DSPy prompt optimisation) at equal optimisation budget on held-out tasks.
- **Method.** Run → attribute (a replay-based attributor) → propose a patch → validate on a
  dev split → keep or discard → test on a held-out split.
- **Data and infrastructure.** τ²-bench and AppWorld splits; Who&When for the attribution sanity check.
- **Baselines.** ACE; DSPy MIPRO-style optimisation; random-step attribution with the same patching.
- **Metrics.** Held-out pass^k; the patch acceptance rate; the overfitting gap.
- **Ablations.** Attributor quality, from oracle to noisy; patch type.
- **Risks.** Small gains; the overfitting debate.
- **Difficulty.** M.
- **Novelty and publication strength.** Medium–high. Novelty risk: medium.

---

## Idea 8 — Effect-Evidence Contracts Against False Success

- **Research question.** If a harness requires an agent's completion claims to cite environment
  read-back evidence, does false success drop in single-control domains, and at what cost?
- **Motivation and gap.**
  - False success makes up 44–52% of failures in single-control τ² domains, and dual control cuts
    it about 10× (2606.09863, search-level).
  - Idempotency keys cut duplicate effects (LIMBO).
  - Claim-evidence ledgers are mentioned in 2609.20812.
- **Hypothesis.** A harness-enforced evidence contract recovers most of the dual-control
  reduction without needing a second actor.
- **Method.** A claim parser, a required read-back tool call per claim, and a verifier that
  checks claim against read-back.
- **Data, infrastructure and baselines.** τ²-bench airline and retail. Baselines: plain harness;
  a self-check prompt.
- **Metrics.** False-success rate; pass^k; tokens.
- **Ablations.** Strictness of the evidence requirement.
- **Risks.** Low novelty (close to 2609.20812); the result may be obvious.
- **Difficulty.** S.
- **Novelty and publication strength.** Low–medium (a workshop or short paper).

---

## Idea 9 — Dependency-Aware Invalidation for Multi-Hop Memory Updates

- **Research question.** When a stored fact changes, can propagating invalidation along derived
  memories fix the multi-hop staleness failures that MemoryAgentBench exposes (≤ 28%)?
- **Motivation and gap.** Zep's bi-temporal invalidation is single-hop. Drift persists even with
  perfect retrieval (2608.19652, search-level).
- **Hypothesis.** Provenance-linked invalidation raises multi-hop update accuracy substantially,
  at modest write cost.
- **Method.** A provenance graph on memory writes. On update, mark descendants stale and lazily
  re-derive them.
- **Data and infrastructure.** MemoryAgentBench FactConsolidation; LongMemEval knowledge-update
  questions.
- **Baselines.** Mem0, A-MEM, Zep, long context.
- **Metrics.** Multi-hop update accuracy; write tokens.
- **Ablations.** Eager vs lazy re-derivation; provenance granularity.
- **Risks.** Crowded memory space; benchmark narrowness.
- **Difficulty.** S–M.
- **Novelty and publication strength.** Medium. Novelty risk: medium–high.

---

## Idea 10 — Reliability-Aware Routing Between Single- and Multi-Agent Execution

- **Research question.** Can pre-execution task features predict whether a MAS will beat a single
  agent *at matched compute*, and route accordingly, measured on pass^k?
- **Motivation and gap.** Kim et al. (M11) find a predictor and gains that swing by task;
  MasRouter routes for accuracy; nobody routes for reliability at matched compute.
- **Hypothesis.** A cheap router recovers most of the oracle-routing gain.
- **Method.** Features feed a router choosing single or MAS (orchestrator–worker) under a budget.
- **Data and infrastructure.** Mixed benchmark pool.
- **Baselines.** Always single; always MAS; MasRouter.
- **Metrics.** pass^k; cost; regret vs oracle.
- **Ablations.** Feature sets.
- **Risks.** Small effect; dependence on M11's predictor.
- **Difficulty.** M.
- **Novelty and publication strength.** Medium.

---

## Idea 11 — Mid-Trajectory Tool Re-Exposure at MCP Scale

- **Research question.** Does re-retrieving and rewriting the exposed tool set *during* a
  trajectory beat retrieving it once upfront, when hundreds of MCP tools are available?
- **Motivation and gap.** MCPGauge (P20) reports a 9.5% accuracy drop and 3–236× more tokens.
  ToolRet (H21) shows retrievers fail. RAG-MCP retrieves once.
- **Hypothesis.** Stage-aware re-exposure improves selection accuracy and cuts tokens.
- **Method.** A retriever conditioned on the current sub-goal, plus description compression.
- **Data and infrastructure.** MCP benchmarks (to verify which are public).
- **Baselines.** Expose all tools; retrieve once.
- **Metrics.** Selection accuracy; success; tokens.
- **Ablations.** Retrieval frequency.
- **Risks.** A crowded engineering space.
- **Difficulty.** S–M.
- **Novelty and publication strength.** Low–medium.

---

## Idea 12 — Compact Learned State Plus a Queryable Archive for Small Agents

- **Research question.** Does a hybrid of a MEM1-style RL-trained constant state and a retrieval
  archive beat either one alone, at the 3–7B scale, on both conversational recall and task suites?
- **Motivation and gap.** Parametric and learned-state memory (R16, R17) is never compared with
  external memory (L3 W8).
- **Hypothesis.** The hybrid dominates both on mixed suites.
- **Method.** RL fine-tuning (GRPO) with a retrieval tool.
- **Data and infrastructure.** LongMemEval, WebShop-style tasks. Needs multi-GPU RL.
- **Baselines.** MEM1, Mem0, long context.
- **Metrics.** Accuracy; memory footprint; tokens.
- **Ablations.** State size; archive access policy.
- **Risks.** Training instability (the Echo Trap, P23); compute.
- **Difficulty.** L.
- **Novelty and publication strength.** Medium–high, but the infrastructure is heavy.

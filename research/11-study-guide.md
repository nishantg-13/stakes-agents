# 11 — Study Guide: Every Prerequisite Concept

Each concept has four parts: **what it is**, **why it matters here**, **how to learn it** (pointing
to papers in `10-reading-order.md` or standard material), and a **self-check** question. If you can
answer every self-check without notes, you are ready to defend the paper.

Several of these overlap with your ML interview prep. Calibration, AUROC, bootstrap and hypothesis
testing are the ROC/AUC/metrics topics you deferred to Nov 10. The order below runs from
foundations to project-specific.

---

## Part A — LLM agents and harnesses

### A1. The agent loop and tool calling
- **What it is.** An LLM repeatedly reads its history and emits either text or a structured tool
  call (name + JSON arguments). The harness executes the call and appends the observation. ReAct
  (H1) is the canonical form.
- **Why it matters here.** STAKES is middleware *between* "propose tool call" and "execute". You
  must know exactly where that seam is in τ²-bench.
- **How to learn it.** ReAct (H1), the τ²-bench code, and the Gemini function-calling docs.
- **Self-check.** In τ²-bench, which component decides whether a turn goes to the user or to a
  tool?

### A2. Harness and scaffold effects
- **What it is.** Prompt templates, action formats and observation formatting change scores
  substantially, independent of the model.
- **Why it matters here.** It is why every baseline must share identical plumbing (all baselines
  are allocator modes).
- **How to learn it.** SWE-agent (H2) ablations; HAL (H6).
- **Self-check.** Why would comparing your STAKES harness to a published τ² leaderboard number be
  invalid?

### A3. User simulators and dual control
- **What it is.**
  - τ-bench uses an LLM to role-play the user.
  - τ²'s dual control means the user also acts on shared state (e.g. in telecom).
- **Why it matters here.** The ask operator (o₄) talks to this simulator, and its noise enters
  your results.
- **How to learn it.** τ-bench (E5), τ²-bench (E6).
- **Self-check.** Why does the user simulator need to be identical across conditions, and what
  failure class does it add?

---

## Part B — Test-time compute

### B1. Sampling, temperature, and self-consistency
- **What it is.** Sample several outputs at temperature > 0 and take the majority answer.
- **Why it matters here.** This is the o₁ vote operator and the source of your p̂ signal.
- **How to learn it.** Self-consistency (Wang et al., ICLR 2023; verify the citation); More Agents
  Is All You Need (M6).
- **Self-check.** Why does majority voting fail when errors are correlated across samples? Connect
  this to the Six Sigma Agent's independence assumption.

### B2. Test-time compute scaling and saturation
- **What it is.** More inference compute (samples, reasoning tokens, search) raises accuracy up to
  a point.
- **Why it matters here.** CATTS shows uniform per-step scaling saturates for agents; your thesis
  is that *where* compute is spent matters more than how much.
- **How to learn it.** CATTS (2602.12276), AVA, 2602.11619.
- **Self-check.** Why does voting late in a trajectory not fix an error made at step 2?

### B3. Matched-compute evaluation
- **What it is.** Compare methods at equal token cost, using full cost–performance curves.
- **Why it matters here.** It is the single most important methodological guard in the paper (W1).
- **How to learn it.** M8, M9, M12; AI Agents That Matter (E10).
- **Self-check.** Two methods have equal pass@1, but one uses 3× the tokens. How do you present
  this, and what is the "budget-to-target" metric?

### B4. Verification and self-correction
- **What it is.** Checking an output, either with the same model (intrinsic) or with external
  signals (tools, environment state).
- **Why it matters here.** o₂ is environment-grounded and o₃ is model-based. The literature says
  intrinsic self-checks are weak.
- **How to learn it.** P12, P8, P13 (Kamoi checklist), CRITIC (P11), LLM-Modulo (P7).
- **Self-check.** What makes a self-correction experiment unfair, per Kamoi et al.?

---

## Part C — Decision theory (the heart of your method)

### C1. Expected utility and loss
- **What it is.** Choose actions to maximise E[utility], or equivalently minimise E[loss] =
  Σ P(outcome) × cost(outcome).
- **Why it matters here.** The VOC formula is an expected-loss reduction.
- **How to learn it.** Any decision-theory chapter, e.g. Russell & Norvig, *AIMA*, the chapters on
  utility and decisions.
- **Self-check.** Why is "minimise error rate" the wrong objective when errors have unequal costs?

### C2. Value of information and value of computation
- **What it is.**
  - Value of information (VOI) = the expected improvement in decision quality from observing
    something before acting.
  - Value of computation (VOC) applies the same idea to *thinking*. Compute is worth spending iff
    the expected loss reduction exceeds its cost.
- **Why it matters here.** STAKES's allocator is a myopic VOC rule: p̂ · C(τ) · φ_o − λ · κ_o.
- **How to learn it.** Russell & Wefald, *Principles of Metareasoning* (1991); the VOI sections of
  *AIMA*.
- **Self-check.** Derive why the VOC of deliberating on a READ action is ≈ 0, even when p̂ is high.

### C3. Lagrangian relaxation and budget prices
- **What it is.** You can turn "maximise reward subject to cost ≤ B" into "maximise reward −
  λ·cost". Sweeping λ traces the Pareto frontier.
- **Why it matters here.** It is how STAKES respects budgets and draws frontiers (Algorithms 1 and 2).
- **How to learn it.** Any convex-optimisation intro (Boyd & Vandenberghe, the duality chapter).
- **Self-check.** If spending runs over budget mid-episode, which direction should λ move, and why?

### C4. Myopic vs non-myopic decisions
- **What it is.** A myopic rule considers only the immediate effect of a choice, ignoring its
  downstream consequences.
- **Why it matters here.** It is a known limitation: an early READ error can propagate (failure
  class a).
- **How to learn it.** The metareasoning literature; reinforcement learning basics on credit
  assignment.
- **Self-check.** Construct a case where myopic VOC under-deliberates.

---

## Part D — Uncertainty, calibration and selective prediction

### D1. Calibration (ECE, Brier score)
- **What it is.** Predicted probabilities match observed frequencies.
  - ECE bins predictions and averages |accuracy − confidence|.
  - The Brier score is the mean squared error of the probabilities.
- **Why it matters here.** STAKES's VOC needs p̂ to be roughly calibrated, at least in rank order.
- **How to learn it.** Rabanser et al. (P_cal, P_brier); your interview metrics notes.
- **Self-check.** Can a predictor have perfect AUROC and terrible calibration? Give an example.

### D2. AUROC and discrimination
- **What it is.** AUROC is the probability that a random positive scores higher than a random
  negative.
- **Why it matters here.** It measures whether p̂ separates erroneous writes from correct ones.
- **How to learn it.** Your interview prep; Rabanser et al. (P_AUROC).
- **Self-check.** Why is AUROC insensitive to the base rate, and when is that a problem?

### D3. Behavioural-consistency uncertainty
- **What it is.** Disagreement among repeated samples serves as a black-box uncertainty signal.
- **Why it matters here.** It is your p̂.
- **How to learn it.** 2602.11619; SAUP (E22).
- **Self-check.** Why canonicalise tool calls before counting disagreement?

### D4. Selective prediction and conformal risk control
- **What it is.**
  - Selective prediction: abstain when uncertain, which trades coverage for accuracy.
  - Conformal methods give distribution-free guarantees on error rates.
- **Why it matters here.** The ask/abstain rung (o₄) and Idea #3.
- **How to learn it.** KnowNo (L5 supplementary); an intro to conformal prediction (Angelopoulos &
  Bates' gentle introduction; verify the citation).
- **Self-check.** What does a risk–coverage curve show?

---

## Part E — Reliability metrics and statistics

### E1. pass@k vs pass^k
- **What they are.**
  - pass@k = P(at least one of k trials succeeds), which measures discovery.
  - pass^k = P(all k succeed), which measures consistency.
  - Unbiased estimators from n ≥ k trials use binomial coefficients.
- **Why it matters here.** pass^k is your primary metric.
- **How to learn it.** τ-bench (E5).
- **Self-check.** With per-task success p = 0.75 and independent trials, compute pass@3 and
  pass^3. Then explain why correlated failures change pass^3.

### E2. Bootstrap confidence intervals
- **What it is.** Resample tasks with replacement, recompute the metric, and take percentiles.
- **Why it matters here.** All of your CIs.
- **How to learn it.** Efron & Tibshirani, or any stats text.
- **Self-check.** Why resample *tasks* rather than episodes?

### E3. Paired permutation tests and multiple comparisons
- **What it is.**
  - A paired permutation test randomly swaps condition labels within each task to build a null
    distribution.
  - Holm correction controls the family-wise error rate.
- **Why it matters here.** Significance at B* across environments.
- **Self-check.** Why paired, and why Holm rather than Bonferroni?

### E4. Variance decomposition and mixed-effects models
- **What it is.** A model that separates the variance due to task, strategy, model and seed.
- **Why it matters here.** RQ1's failure-correlation analysis (ICC), and LIMBO-style attribution
  of variance.
- **Self-check.** What does a high intra-class correlation of failures within a task imply for
  pass^k?

---

## Part F — Side effects and systems concepts

### F1. Idempotency, reversibility, compensation
- **What they are.**
  - Idempotent: repeating the action has no extra effect.
  - Reversible: an inverse exists.
  - Compensable: the effect can be undone only at a residual cost (sagas).
  - Irreversible: cannot be undone.
- **Why it matters here.** Your effect types and cost table.
- **How to learn it.** Revisable by Design (2604.23283); Garcia-Molina & Salem, *Sagas* (1987).
- **Self-check.** Classify "cancel a non-refundable booking" and "send an email" relative to an
  agent whose tools include `rebook` but no `unsend`.

### F2. Exactly-once semantics and duplicate effects
- **What it is.** Each effect happens exactly once, even with retries and lost acknowledgements.
- **Why it matters here.** It is a failure class your ledger must catch, and it is LIMBO's main
  finding.
- **How to learn it.** LIMBO (2609.29095); ACRFence.
- **Self-check.** Why do idempotency keys work, and why can't verification alone guarantee
  exactly-once under late commits?

### F3. Checkpoint / restore, and why it's not enough
- **What it is.** Snapshotting state and rolling back. External effects escape the snapshot.
- **Why it matters here.** It is your motivating argument: in irreversible settings, *prevention*
  (deliberating before the act) beats *recovery*.
- **How to learn it.** DeltaBox (H22), ACRFence, DART, GA-Rollback (E25).
- **Self-check.** What is a "semantic rollback attack"?

---

## Part G — Practical infrastructure

### G1. vLLM serving with tool calling
- **What it is.** A high-throughput open-model server with an OpenAI-compatible API, supporting
  tool calls and logprobs.
- **Why it matters here.** Your open-model runs and the logprob variant of p̂.
- **Self-check.** How do you get per-token logprobs for the tool-call arguments?

### G2. Token accounting and prompt caching
- **What it is.** Providers report input, output and cached tokens separately, and price them
  differently.
- **Why it matters here.** Matched-compute claims live or die on correct accounting.
- **Self-check.** Should cached tokens count toward the "compute" budget, the "cost" budget, or
  both? Decide, and justify it in the paper.

### G3. Experimental hygiene
- **What it is.**
  - Pre-registration of the primary metric.
  - Dev/test splits.
  - Frozen prompts.
  - Seeds generated after freeze.
  - Every reported number produced by a script.
- **Why it matters here.** It is what makes the paper credible, and it is what ABC (E12) checks.
- **Self-check.** List three ways you could accidentally tune on the test set in this project.

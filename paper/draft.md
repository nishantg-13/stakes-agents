# Think Where It Matters: Stakes-Weighted Test-Time Deliberation for Reliable Tool-Using Agents

*Workshop draft v0, 2026-11-09.*

- Values in **[brackets]** are placeholders until the method comparison runs.
- Everything in §5 is measured.
- Citation keys refer to the verified literature dossier (`~/agent-studio/research/literature/`).
  Check every reference against the paper itself before submission.

---

## Abstract

Tool-using LLM agents increasingly take actions that are expensive or impossible to undo, such
as cancelling bookings, issuing refunds or changing orders. Test-time compute (sampling, voting,
verification) is the main lever for making them more reliable. Current adaptive methods spend
it wherever the model is *uncertain*.

We argue that this signal is mis-specified for side-effecting agents. The value of deliberating
at a step is the product of three terms:

- the probability the proposed action is wrong;
- the cost of it being wrong, which depends on whether the action is read-only, reversible,
  compensable or irreversible;
- the chance that deliberation fixes it.

A baseline study on τ²-bench airline (120 episodes, Gemini 2.5 Flash) supports the premise:

- **Inconsistency, not capability, is the main gap.** The agent solves 80% of tasks at least
  once in four tries (pass@4) but only 47% on every try (pass^4).
- **Confident errors are common.** 20% of failures stem from a wrong database write made while
  the re-sampled actions agreed with the proposal (behavioural disagreement p̂ ≤ 1/3).
  Uncertainty-only allocation would not have flagged these steps.
- **Agreement does not imply correctness.** 17% of irreversible writes made with full sampling
  agreement were wrong.

We introduce **STAKES**, a training-free harness controller:

- it types every tool call by reversibility;
- it calibrates error probability per effect type from disagreement among re-sampled actions;
- it spends verification only where the value of computation is positive, under a price λ that
  traces a cost–reliability frontier.

Against uniform, uncertainty-only and verify-every-write allocation, STAKES
**[RESULT: pass^k, irreversible-error rate, cost]**.

---

## 1. Introduction

**Reliability decides deployment.** Agents now execute actions with lasting side effects through
tool APIs. For such systems, the question is not whether an agent *can* solve a task, but
whether it does so *every time*.

- τ-bench introduced pass^k, the probability that all k independent trials succeed, for this
  reason (E5).
- Rabanser et al. (ICML 2026, 2602.16666) find that reliability lags accuracy across agent
  benchmarks.

**Test-time compute is the main lever, but spending it uniformly saturates.**

- Uniform per-step scaling saturates in multi-step agents (CATTS, 2602.12276).
- Majority voting adds little when early errors lock in (2602.11619).
- Several "architectural" gains vanish at matched compute (M8, M9, M12).
- Adaptive allocation helps, but existing methods are driven by uncertainty (CATTS; AVA,
  TMLR 2026).

**A separate 2026 line of work identifies irreversibility as a dominant failure source.**

- AgentAbstain studies abstention before irreversible actions.
- LIMBO (2609.29095) documents duplicated side effects.
- ACRFence, DART and Revisable by Design (2604.23283) address rollback and recoverability.
- The Irreversibility Budget proposes fleet-level risk limits.
- LPS-Bench evaluates unsafe planning.

These works measure, restrict or roll back harmful actions. **None decides where an agent should
spend its thinking.**

**Insight.** Classical metareasoning prescribes deliberating where the *value of computation*
(VOC) is highest: expected error cost averted, minus compute cost (Russell & Wefald).

- **In agents, error cost is highly skewed.** 72% of tool steps in our baseline are reads, where
  a mistake costs a few tokens. A few steps commit irreversible state.
- **Uncertainty-only allocation therefore misallocates in both directions.** It spends on
  uncertain-but-harmless reads and starves confident-but-wrong commits.

**Contributions.**

1. A formulation of stakes-weighted test-time deliberation for side-effecting agents (§3). It
   recovers uniform, uncertainty-only and rule-based verification as special cases.
2. STAKES, a training-free controller with an effect registry, a per-effect calibrated error
   model, and a VOC allocator with a budget price λ (§4).
3. A judge-free reliability protocol (§5.1):
   - success graded from database state;
   - pass^k with bootstrap CIs;
   - an effect ledger that attributes each failure to a wrong write or a missed write.
4. A pre-registered baseline study showing that confident wrong writes account for a substantial
   share of agent failures (§5.2).
5. **[A compute-matched comparison on τ²-bench airline and retail (§6).]**

---

## 2. Related work

- **Test-time compute for LLMs and agents.**
  - Self-consistency and voting (M6).
  - Debate, with critiques at matched compute (M8, M9, M11, M12).
  - Adaptive allocation: CATTS (2602.12276); AVA (TMLR 2026); selective verification
    (2602.03975, *snippet-only, verify*).
  - **Positioning:** we change the allocation *signal* (expected error cost instead of
    uncertainty) and the *setting* (tasks with lasting side effects).
- **Verification and self-correction.**
  - Reflection and self-critique (P9–P14), CRITIC (P11), LLM-Modulo (P7).
  - STAKES uses a policy verifier as one operator. Our contribution is *when* to call it, not the
    verifier itself.
- **Irreversibility and recovery.**
  - AgentAbstain, LIMBO, ACRFence, DART, DeltaBox (H22), GA-Rollback (E25), Revisable by Design,
    the Irreversibility Budget, LPS-Bench, ToolEmu (E14).
  - We adopt the reversibility taxonomy of Revisable by Design and add READ.
- **Uncertainty for agents.**
  - SAUP (E22), behavioural consistency (2602.11619), KnowNo.
  - Our pilot shows that behavioural agreement is a weak correctness signal at irreversible steps
    (§5.2), which motivates calibrating error probability per effect type.
- **Reliability evaluation.**
  - τ/τ²-bench (E5, E6), HAL (H6), AI Agents That Matter (E10), ABC (E12), Rabanser et al.

---

## 3. Problem formulation

**Episode.** An agent with policy π interacts with environment E.

- At step t it proposes a tool call a_t ~ π(·|h_t).
- Executing a_t changes state σ_t → σ_{t+1}.
- Success S(σ_T) is checked programmatically from final state, never by an LLM judge.

**Effect type.** τ(a) ∈ {READ, IDEMPOTENT, REVERSIBLE, COMPENSABLE, IRREVERSIBLE}.

- Reversibility is **policy-compliant and agent-relative**: an action is REVERSIBLE only if the
  agent's own tools can undo it while following the domain policy.
- Labels are fixed per environment in a registry, with a written rationale for each tool.

**Value of computation.** For an operator o with fix rate φ_o and cost κ_o (in LLM calls):

  VOC_t(o) = p_err(τ_t, p̂_t) · C(τ_t) · φ_o − λ · κ_o

- p̂_t is the share of k₀ re-sampled actions that disagree with the proposal.
- p_err is the *calibrated* error probability of a write of type τ given agreement or
  disagreement.
- C is the harm of an uncorrected error of type τ.
- Operator o runs iff VOC_t(o) > 0. Sweeping λ traces a frontier.

**Special cases.**

| Setting | Recovers |
|---|---|
| C constant | Uncertainty-only allocation |
| p_err constant | Stakes-only allocation |
| λ = 0 | Verify every write |
| Both constant | Uniform deliberation |

**Why calibrate p̂?** Raw disagreement assigns zero error probability to unanimous proposals.
But the pilot shows that unanimous irreversible writes are wrong 17% of the time (§5.2). So
p_err maps (τ, agree/disagree) to an empirical error rate fitted on the development split.

---

## 4. Method: STAKES

1. **Effect registry.**
   - A YAML table per domain maps each tool to its effect type, with a rationale.
     - *Airline:* `cancel_reservation`, `send_certificate` and `update_reservation_baggages` are
       IRREVERSIBLE; `book_reservation` and `update_reservation_flights` are COMPENSABLE;
       `update_reservation_passengers` is REVERSIBLE.
   - Any state-changing tool left unlabelled stops the run.
2. **Disagreement estimate.**
   - At each write, sample k₀ = 2 alternative actions at temperature 1 from the same context.
   - Canonicalise calls, ignoring key order, case, whitespace, int/float and free-text summaries.
   - Compute p̂.
3. **Vote (o₁).** Execute the majority action if it strictly beats the proposal. The samples are
   already paid for, so κ = 0.
4. **Policy verifier (o₃).**
   - An LLM reviewer sees the policy, the conversation, the proposed action and its effect type.
   - It answers APPROVE or REVISE with a specific violated rule.
   - On REVISE, the agent regenerates once with the reviewer's note appended, which often makes
     it ask the customer instead of acting.
   - The verifier runs iff VOC > 0.
5. **Calibration (offline, development split only).**
   - p_err(τ, bucket) is estimated from baseline rollouts as Beta-smoothed error rates, shrunk
     toward the pooled rate of each bucket.
   - C is an ordinal table: REVERSIBLE 0.25, COMPENSABLE 0.6, IRREVERSIBLE 1.0. τ²-bench fails
     a task on any wrong write, so an empirical C would be flat; we report a sensitivity
     analysis.

READ steps execute directly with no deliberation.

**Not yet implemented** (planned operators): state read-back (o₂) and ask/abstain (o₄).

---

## 5. Baseline study: where do agent failures come from?

### 5.1 Setup

- **Benchmark.** τ²-bench (sierra-research, pinned commit `033bf08`), airline domain.
  - We use the official `train` split (30 tasks) for development and hold out `test` (20 tasks).
  - Retail (74 / 40) is labelled and ready.
- **Model.** Gemini 2.5 Flash serves as agent (temperature 0), user simulator (temperature 0)
  and probe sampler (temperature 1).
- **Grading.** τ²-bench `ENV` evaluation only: final database state plus environment assertions.
  We exclude the LLM-judged components, so our numbers are not comparable to the public
  leaderboard.
- **Measurement.**
  - At every write we draw k₀ = 3 probe samples and log p̂, but never execute them. The agent's
    behaviour is unchanged.
  - An effect ledger matches each executed write to the reference trajectory. Arguments are
    matched by containment: the agent may add informational fields.
  - Each failed episode is classified by its first unmatched write (*wrong write*) or, failing
    that, by a reference write never performed (*missed write*).
  - The matcher flagged 0% of writes in successful episodes, after fixing an initial 14% rate
    caused by exact matching.
- **Pre-registration.** Before any data, we fixed this decision rule on the share of failures
  whose decisive error is a wrong write with p̂ ≤ 1/3:
  - ≥ 0.30 → GO;
  - 0.15–0.30 → GO, lead with the test-time-compute reliability question;
  - < 0.15 → pivot.

### 5.2 Results (30 tasks × 4 trials = 120 episodes, $2.07 total)

**Table 1. Baseline reliability** (95% bootstrap CIs over tasks).

| k | pass^k | pass@k |
|---|---|---|
| 1 | 0.63 [0.48, 0.77] | 0.63 [0.48, 0.77] |
| 2 | 0.54 [0.38, 0.70] | 0.72 [0.57, 0.86] |
| 4 | 0.47 [0.30, 0.63] | 0.80 [0.63, 0.93] |

Per-task consistency is bimodal:

- 14 tasks succeed on all four trials and 6 fail on all four;
- the other 10 are inconsistent.

**Table 2. Failure attribution** (44 failed episodes).

| Decisive error | Count | of which p̂ ≤ 1/3 |
|---|---|---|
| Wrong write, IRREVERSIBLE | 6 | 4 |
| Wrong write, COMPENSABLE | 9 | 5 |
| Missed write | 29 | n/a |

- **Confident wrong-write share:** 9/44 = **0.205**, so the pre-registered outcome is **GO, lead
  with the RQ1 framing**.

**Table 3. Error rate of executed writes by effect type and sampling agreement.**

| Effect | Agree (p̂ = 0): wrong / n | Disagree (p̂ > 0): wrong / n |
|---|---|---|
| IRREVERSIBLE | 5 / 29 (17%) | 3 / 6 (50%) |
| COMPENSABLE | 3 / 8 (38%) | 6 / 14 (43%) |
| REVERSIBLE | 0 / 4 | – |

**Findings.**

1. **Reliability, not capability, is the gap.** pass@4 − pass^4 = 0.33: the agent could solve a
   third of the tasks but does not do so consistently.
2. **Disagreement is informative but insufficient.** Disagreement roughly triples the error rate
   at irreversible steps (17% → 50%). But most irreversible writes are unanimous, so most wrong
   irreversible writes (5 of 8) occur *with full agreement*. Any allocator that uses uncertainty
   alone skips them.
3. **Omissions dominate failures.** 29 of 44 failures are missed writes, where the agent stopped
   short or chose not to act. Deliberating before an action cannot fix omissions. This motivates
   the ask/abstain operator and a separate analysis of completion behaviour.
4. **Reads dominate steps.** 72% of tool steps are reads, so skipping deliberation there is where
   the compute savings come from.

---

## 6. Method comparison [TO RUN]

**Conditions.** All conditions are paired on the same tasks, trials and seeds:

- baseline;
- uncertainty-only (sample at every tool step, verify when p̂ > 0);
- verify every write;
- STAKES fixed rule (v0);
- STAKES-VOC at λ ∈ {0.03, 0.1, 0.2}.

All verifier calls use one shared, effect-aware prompt.

**Metrics.** pass^1, pass^4, irreversible-error rate (wrong COMPENSABLE/IRREVERSIBLE writes per
episode), and USD and tokens per episode. The headline is the frontier of pass^4 against
cost.

**Table 4. [Method comparison, airline dev.]**

**Figure 1. [pass^4 vs cost per episode, one point per condition, with the λ-sweep as a curve.]**

**Preliminary demo** (15 tasks × 2 trials, verifier prompt v1, not budget-matched; CIs overlap
everywhere):

| Method | Success | pass^2 | Wrong irreversible / ep | Cost / ep |
|---|---|---|---|---|
| Baseline | 0.50 | 0.40 | 0.27 | $0.011 |
| Uncertainty-only | 0.57 | 0.40 | 0.13 | $0.028 |
| Verify every write | 0.60 | 0.47 | 0.13 | $0.018 |
| STAKES v0 | 0.60 | 0.60 | 0.13 | $0.022 |

---

## 7. Limitations

- **Small samples.** With 30 development tasks, CIs are wide. Final claims require the held-out
  test split, retail, and more models.
- **Single model family so far.** Open-weight models via vLLM are planned.
- **Partly hand-set parameters.** C is ordinal and hand-set; φ and κ are placeholders. We will
  report sensitivity to each.
- **Calibration and evaluation share tasks.** On the development split, p_err is fitted on the
  same tasks used for evaluation, so development numbers for STAKES-VOC are optimistic. Final
  numbers use parameters frozen before touching the test split.
- **Reference-trajectory matching can mislabel valid alternative paths.** We attribute errors
  only in failed episodes and report the false-flag rate on successful ones (0%).
- **Omissions are out of scope** for pre-action deliberation and remain the largest failure
  class.

---

## Appendix A. Reproducing §5

```bash
uv run python -m stakes.pilot run --domain airline --split train \
  --agent-llm gemini/gemini-2.5-flash --user-llm gemini/gemini-2.5-flash \
  --mode measure --k0 3 --trials 4 --workers 6 --out results/pilot_airline_measure
uv run python -m stakes.pilot analyze results/pilot_airline_measure
uv run python -m stakes.voc results/pilot_airline_measure --out params/tau2_airline.yaml
```

# 13 — What to Build First

The single most important early step is a **cheap go/no-go pilot**. It tests whether the core
premise is even true *before* you build the allocator.

> **Premise to test.** In real agent failures, a meaningful share of decisive errors are *writes
> that the model was confident about* (low disagreement). If almost all decisive errors happen at
> high-disagreement steps, uncertainty-only allocation already targets them, and STAKES has
> little room to win.

## Step 1 — Run τ²-bench as-is (day 1–2)
1. Clone τ²-bench and record the commit hash.
2. Configure your Gemini key through an environment variable. Never commit it.
3. Run 10 airline tasks with a Gemini Flash-tier model as both agent and user simulator.
4. Write down three things:
   - tokens and USD per episode;
   - where gold actions and the DB-state checks live in the code;
   - how tools are defined (to plan the effect registry).

## Step 2 — Effect registry and ledger (day 3–6)
1. List every airline and retail tool. For each, decide its type: READ / IDEMPOTENT / REV / COMP /
   IRR. Use the agent-relative rule: is there an inverse tool in the agent's tool set?
2. Wrap tool execution: log type, arguments, and the DB snapshot diff around each write.
3. Implement the pass^k / pass@k estimators and IER, with unit tests against hand-computed
   examples.

## Step 3 — Pilot data (day 7–10)
1. Run 50 airline tasks × k = 4 trials at a moderate temperature (≈ 200 episodes).
2. At every **write** step, sample k₀ = 3 extra candidate actions *without executing them*.
   Compute p̂ by canonical-action disagreement.
3. For each failed episode, locate the decisive error: the first action inconsistent with the
   gold action set or the final DB diff. Record its effect type and p̂.

## Step 4 — Decide (day 10)
Write the rule down **before** looking at the results (also in `07-experiment-checklist.md` §D).

| Finding | Decision |
|---|---|
| ≥ 30% of decisive errors are writes with low p̂ | **GO**: build STAKES as planned |
| 15–30% | GO, but lead the paper with RQ1 (the compute–reliability audit) and treat STAKES as the method contribution |
| < 15% | **PIVOT**: flagship becomes Idea #2 ("Does test-time compute buy reliability?"); the instrumentation is fully reused |

Also record:
- the share of steps that are READ (H3b needs this to be large);
- whether verify-before-write would have caught the low-p̂ write errors. This is an early read on
  RQ6.

## Step 5 — Only then build the allocator
Build in this order, testing each stage before the next:
1. Canonicalizer.
2. Operators o₁–o₃.
3. VOC allocator modes.
4. Offline fitting.
5. λ-sweeps.

## Concrete first-week shopping list
- [ ] Decide the repo location (suggest `~/stakes-agents/`, separate from agent-studio).
- [ ] Confirm your GPU: model, memory, and how you access it. This decides the open-model size
      (assumption A-1).
- [ ] Set a spending cap and alert on the Gemini key.
- [ ] Read Tier-1 papers 1–4 (`10-reading-order.md`).
- [ ] Run Step 1.

## What NOT to do first
- Don't build LedgerWorld, the ask operator, or the LLM effect typer before the pilot says GO.
- Don't tune prompts on tasks that will become the test split. Fix the dev/test split on day 3.
- Don't scale runs before the metric and ledger unit tests pass. Paid runs with a metric bug are
  wasted money.

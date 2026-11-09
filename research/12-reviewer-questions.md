# 12 — Likely Reviewer Questions and Strong Responses

Each response is a plan: it says what evidence to *have ready*. If the evidence doesn't
materialise, change the claim rather than the answer.

**Q1. "Isn't this just CATTS/AVA with a weight?"**
Prepare three pieces of evidence:
- (a) A formal account (§3): uncertainty-only allocation is the special case C ≡ const, and is
  sub-optimal exactly when error costs are skewed. Back this with the proposition, or at least a
  worked example.
- (b) RQ3, Table 3: the gains come from high-stakes / *low*-uncertainty steps, where
  uncertainty-only allocation spends nothing by construction.
- (c) A different setting: side-effecting environments with state-grounded metrics (IER, pass^k).
  CATTS and AVA did not evaluate there.

**Q2. "A simple verify-before-every-write rule would do the same."**
- This is RQ6, and the baseline is included at every budget.
- Expect STAKES to win at low and medium budgets, because it skips confident writes and adds
  read-back where p̂ is high.
- If it doesn't win, say so. The contribution becomes the evaluation protocol plus the finding
  that the simple rule is near-optimal, which is still useful to practitioners.

**Q3. "Your cost table is hand-picked."**
- Three stylised tables, plus an *empirically estimated* C(τ) from dev-split failure rates.
- A sensitivity sweep from ×0.5 to ×2 (Table 5).
- Show that rankings are stable across the sweep.

**Q4. "Effect typing requires manual labels — not scalable."**
- About 1–2 hours per domain, using a published protocol with agreement scores.
- The LLM typer is evaluated, and mislabel-injection robustness is measured (RQ5).
- Typing is a one-off cost per tool, in contrast to per-episode human oversight.

**Q5. "τ²-bench writes aren't truly irreversible — it's a simulator."**
- Irreversibility is defined *relative to the agent's tool set* (§3). A cancelled non-refundable
  booking cannot be restored with the tools available, which is the relevant notion for an
  autonomous agent.
- LedgerWorld makes irreversibility explicit and controllable.

**Q6. "The user simulator is an LLM, so your results inherit its noise."**
- The simulator is identical across conditions, so its noise is common-mode.
- Report simulator-attributed failures in the taxonomy (class g).
- LedgerWorld uses a scripted user, as a judge-free control.

**Q7. "Is the comparison really compute-matched?"**
- Every strategy is a mode of the same allocator.
- Tokens are counted from provider usage fields, including the k₀ estimation samples and the
  operator calls.
- Comparisons are made at interpolated equal budgets along full frontiers, not at single points.

**Q8. "Only Gemini plus small open models — does it generalise?"**
- Two model families (Gemini API, open-weight), plus a Pro-tier subset and a larger open model in
  the main track.
- State the limitation plainly.
- The method is model-agnostic middleware, and the code makes it cheap for others to test on
  other models.

**Q9. "Isn't best-of-N trajectories the real baseline?"**
- It is reported as a *reset-oracle reference*.
- It needs environment resets, which are impossible after irreversible actions in deployment.
  That is the motivating constraint of the paper.

**Q10. "How do you know the 'decisive error' step?"**
- Use gold action sets where available (τ-bench-style annotations).
- In LedgerWorld, use the exact final-state diff.
- The counterfactual-continuation check is used only for analysis, with its known confounds
  acknowledged (Causal Agent Replay).

**Q11. "Statistical significance?"**
- Bootstrap over tasks, paired permutation tests at a pre-registered budget point, and Holm
  correction across environments.
- k = 8 trials per task in the main track.
- Report the effect sizes alongside the p-values.

**Q12. "Benchmark contamination?"**
- τ² and AppWorld are public, but contamination affects all strategies equally (common-mode).
- LedgerWorld test seeds are generated after freeze.
- The relative comparison is the claim, not absolute scores.

**Q13. "Over-asking just shifts work to users."**
- Interruption rate is reported, along with utility at several costs of asking (λ).
- An ask-free STAKES variant is included in the ablations.

**Q14. "Why not train a policy (RL) instead of hand tables?"**
- Training-free is a feature: interpretable, cheap, and portable across models.
- A learned allocator is natural future work. Mention that φ and C could be learned, and show
  that fitted φ beats constant φ (ablation).

**Q15. "Concurrent work X does the same."**
- Keep the novelty log (`checklists/novelty-recheck.md`) and cite fairly.
- Differentiate on the signal (expected cost), the setting (side effects), and the metrics
  (reliability at matched compute).

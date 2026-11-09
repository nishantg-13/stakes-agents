# 10 — Reading Order

The **why** column says what to extract from each paper for *this* project. IDs refer to
`01-literature-matrix.md`, and full records are in `literature/`. Papers marked [S] in the novelty
audit should be verified on their abstract page before you cite them.

Reading strategy:
- **Tier 1:** read fully, including the appendix.
- **Tier 2:** read the method and experiments.
- **Tier 3:** read the abstract, figures and conclusion.

## Tier 1 — Must read in week 1 (the core of your related work)

| # | Paper | Why |
|---|---|---|
| 1 | τ-bench (E5) | pass^k definition and estimator; the user-simulator design; how DB grading works |
| 2 | τ²-bench (E6) | Your main environment; dual control; the domain policies your verifier will check against |
| 3 | Towards a Science of AI Agent Reliability (Rabanser et al., ICML 2026, arXiv 2602.16666) | Reliability metrics you will reuse; note that they test no interventions, which is your gap |
| 4 | CATTS, Agentic Test-Time Scaling for WebAgents (arXiv 2602.12276) | **Closest prior art.** Vote-entropy allocation; uniform scaling saturates. You must beat its allocation as a baseline. |
| 5 | AVA, Anytime Verified Agents (TMLR 2026) | Second-closest prior art; budget split across search, sampling and verification |
| 6 | AgentAbstain (arXiv 2607.10059) | "Post-hoc abstention"; paired-task design; possible environment |
| 7 | Where Does Exactly-Once Live? / LIMBO (arXiv 2609.29095) | Effect ledgers; false success at 90%; model vs harness vs contract variance decomposition |
| 8 | Behavioral Consistency as an Uncertainty Signal (arXiv 2602.11619) | Your p̂ signal; voting adds 0–2 pp; divergence at step 2 |

## Tier 2 — Weeks 2–4

| # | Paper | Why |
|---|---|---|
| 9 | Revisable by Design (arXiv 2604.23283) | The reversibility taxonomy you adopt; cite precisely |
| 10 | The Irreversibility Budget (arXiv 2609.00275) | Effect pricing; admission control vs your deliberation allocation |
| 11 | Should we be going MAD? (M8) + Debate or Vote (M9) | Why matched-compute baselines are mandatory |
| 12 | LLMs Cannot Self-Correct Reasoning Yet (P12) + Self-Verification Limitations (P8) | Why your operators prefer state-grounded checks |
| 13 | Kamoi et al. survey (P13) | The checklist for fair self-correction experiments; apply it to your verifier operator |
| 14 | LLM-Modulo (P7) | The external-verifier philosophy; framing for o₂ read-back |
| 15 | AI Agents That Matter (E10) + ABC (E12) | Cost reporting and benchmark-hygiene rules reviewers will check |
| 16 | HAL (H6) | Scaffold effects; logging and cost practice |

## Tier 3 — As needed

| # | Paper | Why |
|---|---|---|
| 17 | ACRFence, DART, DeltaBox (H22), GA-Rollback (E25) | Related work on recovery; how you differ |
| 18 | LPS-Bench (arXiv 2602.03255), ToolEmu (E14), AgentDojo (E15) | Safety-evaluation context |
| 19 | SAUP (E22), MAST (M20), Who&When (M21) | Uncertainty propagation; failure taxonomies for your error analysis |
| 20 | ReAct (H1), SWE-agent (H2), CodeAct (H3), OpenHands (H4) | Harness basics, if any are unfamiliar |
| 21 | Six Sigma Agent (arXiv 2601.22290) | A counterpoint: per-action consensus under an independence assumption. Be ready to explain why correlated errors break it. |
| 22 | Classical: Russell & Wefald, *Principles of Metareasoning* (1991); Garcia-Molina & Salem, *Sagas* (1987) | The value-of-computation and compensation foundations. Verify the bibliographic details. |

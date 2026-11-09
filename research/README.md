# Research Dossier — LLM Agents: Stakes-Weighted Test-Time Deliberation

Prepared 2026-11-08. This folder contains the literature, research design and study plan only.
**Nothing has been implemented, and no experiments have been run.** Every number in this folder
that looks like a result is either cited from a paper or explicitly labelled as expected or
estimated.

## Decision so far
- **Flagship idea:** #1 Stakes-Weighted Deliberation (STAKES). The decision record is at the top
  of `06-proposal.md`.
- **Resources:** one paid Gemini API key, plus GPU access (GPU size still to confirm).
- **Venue strategy:** a workshop paper (~Feb 2027), then a main-track paper (NeurIPS 2027,
  ~May). Both deadlines are approximate.

## Files (read in this order)
| File | Contents |
|---|---|
| `literature/01–05-*.md` | Five slice reviews, ~115 papers. Full per-paper records: exact title, authors, venue, year, link, contribution, method, datasets, metrics, tagged limitations, code, gaps. |
| `01-literature-matrix.md` | One-row-per-paper index, with cross-cutting weakness tags W1–W10 |
| `02-recurring-weaknesses.md` | Synthesis of W1–W10 (established vs hypothesis), and the gap we exploit |
| `03-novelty-audit-2026.md` | 2026 work that closed or narrowed candidate ideas. **Read this before trusting any novelty claim.** |
| `04-research-ideas.md` | 12 ideas, each with RQ, gap, hypothesis, method, architecture, data, baselines, metrics, ablations, risks, difficulty, novelty |
| `05-ranking-and-shortlist.md` | Scores, top-3 decision table, recommendation |
| `06-proposal.md` | Full proposal and paper plan: formulation, RQs, method, Mermaid architecture, algorithms, protocol, metrics, ablations, expected-result templates, limitations, ethics, reproducibility, timeline, venues |
| `07-experiment-checklist.md` | Gated checklist, from setup to release |
| `08-repo-structure.md` | Suggested code layout |
| `09-week-by-week-plan.md` | W1 (Nov 16) → W26 (main-track submission) |
| `10-reading-order.md` | Tiered reading list, with what to extract from each paper |
| `11-study-guide.md` | Every prerequisite concept, with self-check questions |
| `12-reviewer-questions.md` | 15 likely reviewer objections, and the evidence to prepare |
| `13-what-to-build-first.md` | Go/no-go pilot and first-week steps |
| `checklists/novelty-recheck.md` | Monthly re-check queries and log |

## Verification notes
- **[V] vs [S]:**
  - Slice-review papers were each confirmed on a primary page.
  - 2026 audit papers are marked [V] (abstract page read) or [S] (search snippet only). **Verify
    every [S] paper before citing it.**
- **Venue caveats** are recorded per paper in the slice files. Examples:
  - AutoGen's COLM venue comes from the authors' Microsoft Research page.
  - MemoryOS's EMNLP venue comes from the authors' README.
  - Generative Agents' UIST venue comes from the ACM reference block in the PDF.
- **Classical references** (Russell & Wefald 1991; Garcia-Molina & Salem 1987; self-consistency;
  the conformal-prediction intro) are cited from memory and flagged "verify" where they appear.

## Open assumptions
- **A-1:** GPU size is unknown. It determines whether an open model in the ~30B class is feasible.
- **A-2:** AgentAbstain code and data are public. Not yet verified.
- **A-3:** τ²-bench exposes gold action sets programmatically, enough to locate decisive errors.
  Verify in W1.

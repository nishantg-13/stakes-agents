# 02 — Recurring Weaknesses Across the Literature

> **Epistemic status.** These are cross-cutting patterns synthesised from the five slice reviews
> and the 2026 novelty audit. Each **Evidence** line cites papers whose own results support the
> claim (*established*). Each **Our reading** line is interpretation (*hypothesis*), and nothing in
> it has been tested yet.

---

## W1 — Gains that vanish under a compute-matched baseline

- **Pattern.** Multi-agent debate, mixture-of-agents, reflection loops and tree search usually
  compare against one cheap single-agent call. When the baseline instead gets the *same token
  budget* (self-consistency, voting, best-of-N, a single agent with more thinking), much of the
  gain disappears.
- **Evidence (established).**
  - M8 (*Should we be going MAD?*): debate does not reliably beat self-consistency.
  - M9 (*Debate or Vote*): voting accounts for most of debate's gain.
  - M12: a single agent matches a MAS at equal thinking tokens.
  - M11: MAS returns diminish once single agents are strong, and swing from +80.8% to −70% by task.
  - P8 and P12: intrinsic self-correction and self-verification often add nothing, or hurt,
    against resampling.
- **Our reading (hypothesis).** Much of the published "architecture" gain is test-time compute
  wearing a costume. Any new method must be reported on a cost–performance curve against plain
  sampling baselines, or reviewers will rightly reject it.

## W2 — Single-run success as the only number

- **Pattern.** Most agent benchmarks report pass@1 from one run (E1–E4, E7, E9).
- **Evidence (established).**
  - E5 (τ-bench) introduced pass^k and showed it falls steeply with k.
  - *Towards a Science of AI Agent Reliability* (Rabanser et al., ICML 2026; see `03-novelty-audit-2026.md`)
    proposes 12 reliability metrics over 15 models. It finds that reliability improves far more
    slowly than accuracy.
  - The behavioural-consistency paper (arXiv 2602.11619, ICML'26 workshop) finds that single-run
    evaluation misranks models 29.3% of the time under bootstrap.
- **Gap that remains (established, from the Rabanser paper's own text).** It evaluates one
  scaffold per benchmark at temperature 0. It tests **no test-time intervention** (voting,
  reflection, verification, multi-agent, retries) for its effect on reliability, and has no
  matched-compute comparison. It lists scaffolds and stateful long-horizon reliability as future
  work.

## W3 — Self-evaluation and LLM judges at every layer

- **Pattern.** Planning methods use the LLM as its own value function (P2, P4, P5, P9, P10, P24).
  The LLM is also used as the evaluation instrument throughout:
  - simulated users (E5, E6);
  - emulated tools (E14);
  - safety scorers (E17);
  - hallucination judges (E20, E21);
  - failure annotators (M20);
  - and judges for evaluating agents (E18).
- **Evidence (established).**
  - P8 and P12 show self-critique failing on reasoning and planning.
  - The 2026 false-success work (arXiv 2606.09863; search-level verification only) reports that
    agents claim completion while the environment state says otherwise. On the LIMBO testbed,
    agents reported success in 90% of episodes where they had duplicated an effect (arXiv 2609.29095).
- **Our reading.** Evaluation and control signals should come from **environment state**, not from
  an agent's or judge's text, wherever the environment allows it.

## W4 — The reversible-world assumption

- **Pattern.** Tree search (P2–P4), agentic RL (P21–P24), interaction scaling (P24) and rollback
  (E25, H22) assume actions can be undone or the episode reset cheaply.
- **Evidence (established).**
  - ACRFence (2603.20625): restoring a checkpoint can re-issue irreversible external calls.
  - DART (2605.23311): local restore can orphan committed downstream work.
  - LIMBO (2609.29095): duplicate side effects driven by model, harness and tool contract.
  - AgentAbstain (2607.10059): agents take irreversible actions *before* recognising they should
    abstain ("post-hoc abstention").
  - The Irreversibility Budget (2609.00275, SOSP AgenticOS workshop): per-action gates let
    fleet-level risk overdraw by up to 48×.
- **Gap that remains (our assessment, verified against those abstracts).** These papers cover:
  - **runtime** restore semantics (ACRFence, DART);
  - **admission control** (Irreversibility Budget);
  - **contracts** (LIMBO);
  - **measurement** (AgentAbstain, LPS-Bench).

  None of them uses irreversibility to decide **how much the agent should deliberate or verify
  before acting**. The 2026 adaptive-compute papers (CATTS 2602.12276; AVA, TMLR 2026) allocate
  compute by **uncertainty only** and evaluate on side-effect-free tasks (web navigation, math, QA,
  code). The irreversibility papers and the adaptive-compute papers do not cite each other's
  problem.

## W5 — Narrow, saturated, or mis-graded benchmarks

- **Evidence (established).**
  - ABC (E12): grading and setup flaws mis-estimate scores by up to 100% relative.
  - SWE-Bench Illusion (E13): evidence of memorisation.
  - LoCoMo (R12): about 10 conversations, with statistics that differ between versions.
  - MAS topology, routing and pruning (M13–M18) are evaluated mostly on saturated short-answer sets
    (MMLU, GSM8K, HumanEval).
- **Our reading.** Pick benchmarks whose grading reads the **environment state**:
  - τ²-bench, a database-state check;
  - AppWorld, programmatic tests;
  - AgentAbstain, a deterministic commit check;
  - LIMBO, an effect ledger.

  This has two benefits. It sidesteps W3, and it gives ground truth about *which actions changed
  the world*, which W4-style research needs.

## W6 — Components optimised in isolation

- **Evidence (established).**
  - Compression, masking and playbook edits (H17–H20) break the exact-prefix reuse that serving
    systems (H8, H11, H13) depend on. No L1 paper measures the two together.
  - 2026 serving preprints (CommitKV, SparseRead, IntentKV; search-level only) are starting to
    close this gap from the systems side.
- **Our reading.** Cross-layer studies are publishable, but the systems community is moving
  quickly here.

## W7 — Diagnosis without remedy

- **Evidence (established).**
  - MAST's (M20) proposed fixes give modest gains.
  - Who&When (M21) step-level attribution is about 14% accurate.
  - 2026 work (AgenTracer, Causal Agent Replay, EMFA, DCFA; search-level only) has largely
    claimed the counterfactual-replay angle, but mostly on *attribution accuracy*, not on
    *repairing* the system.

## W8 — Closed and deprecated models

- **Evidence (established).** Many foundational results (P1, P2, P9, P10, P12) rest on models
  that are no longer served, so they cannot be reproduced exactly.
- **Our reading.** A new paper should use at least one open-weight model family, so others can
  reproduce it.

## W9 — Proxy workloads in systems papers

- **Evidence (established).**
  - Systems papers (H7, H9, H11–H13) use synthetic workloads and estimated tool latencies.
  - The most realistic workload shows the smallest gain: KVFlow reaches only 1.08–1.12× on PEER.

## W10 — Integrity of persistent state

- **Evidence (established).**
  - Memory writes depend on noisy LLM judgement (R5–R8, R15, R21).
  - Multi-hop overwrite accuracy is at most 28% on MemoryAgentBench (R14).
  - 2026 work has studied poisoning of Mem0 and A-Mem specifically (MemPoison, reported as accepted
    at ACM CCS 2026; GhostWriter). It has also studied state drift ("Can Agent Memory Systems
    Track Evolving State?"). All three are search-level verification only.

---

## The intersection we will exploit (hypothesis)

W1, W2 and W4 together point at one under-studied question:

> **When an agent has extra test-time compute, where should it spend it?** And does spending it
> where *errors are expensive* — at irreversible, state-committing actions — buy more
> **reliability** (pass^k, irreversible-error rate) than spending it where the model is merely
> *uncertain*?

Three facts make this question open (all established, see `03-novelty-audit-2026.md`):

1. Uniform per-step compute saturates. CATTS shows this for web agents. The consistency paper
   finds that uniform voting adds only about 0–2 pp in multi-step settings, because early errors
   lock in.
2. Uncertainty-only adaptive allocation exists (CATTS, AVA), but it ignores the **cost** of an
   error, and it was evaluated where actions have no lasting side effects.
3. Irreversibility is now well characterised as a failure source (AgentAbstain, LIMBO, ACRFence,
   DART, LPS-Bench). Nobody has used it as a *compute-allocation signal*.

This forms the basis for the recommended idea in `05-ranking-and-shortlist.md`. It is presented
as a recommendation pending your input.

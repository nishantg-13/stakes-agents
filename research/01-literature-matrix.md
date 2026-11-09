# 01 — Literature Matrix

> **How to read this.** One row per paper. Every row was checked on a primary source page (arXiv
> abs, OpenReview, ACL Anthology, PMLR, NeurIPS/ICLR proceedings, USENIX, AAAI OJS) by the
> literature-review pass on 2026-11-08. The full per-paper record lives in the slice file:
> **exact title, full authors, methodology, datasets, metrics, tagged limitations, code
> availability, and research gaps.** This matrix is the index plus the cross-cutting weakness tags.
>
> - Venue is stated only where acceptance was confirmed; otherwise it says *preprint*.
> - Caveats on individual venues (e.g. "from the authors' README") are recorded in the slice files.
> - Slice files:
>   - L1 = `literature/01-harnesses-runtimes-context.md`
>   - L2 = `literature/02-multi-agent-orchestration.md`
>   - L3 = `literature/03-memory.md`
>   - L4 = `literature/04-planning-reflection-tools.md`
>   - L5 = `literature/05-evaluation-reliability-verification.md`
> - 2026 frontier papers found during the novelty audit are in `03-novelty-audit-2026.md`.

## Weakness tags (defined in `02-recurring-weaknesses.md`)

| Tag | Weakness |
|---|---|
| **W1** | No compute-matched baseline (vs. self-consistency / best-of-N / single agent at equal tokens) |
| **W2** | Single-run success only — no variance, CIs, or reliability metric (pass^k, consistency) |
| **W3** | Depends on LLM self-evaluation or LLM-as-judge without adversarial validation |
| **W4** | Assumes a resettable / reversible world; side effects not modelled |
| **W5** | Narrow, saturated, toy, or flawed-grader benchmarks |
| **W6** | Components optimised in isolation; cross-layer interactions unmeasured |
| **W7** | Diagnoses failures without a remedy, or the remedy is weak |
| **W8** | Closed / deprecated models or live APIs → weak reproducibility |
| **W9** | Proxy or synthetic workloads standing in for real agent traces |
| **W10** | Integrity of persistent state (memory corruption, poisoning, drift) unaddressed |

---

## L1 — Harnesses, runtimes, context engineering

| ID | Paper | Venue | Year | Core contribution | Tags | Link |
|---|---|---|---|---|---|---|
| H1 | ReAct | ICLR | 2023 | Interleaved thought/action/observation loop; base of most harnesses | W2 W8 | https://arxiv.org/abs/2210.03629 |
| H2 | SWE-agent | NeurIPS | 2024 | Agent-computer interface; interface design alone moves SWE-bench Lite 3–8 pts | W2 W5 | https://arxiv.org/abs/2405.15793 |
| H3 | CodeAct | ICML | 2024 | Executable Python as unified action space beats JSON/text tool calls | W2 W4 | https://arxiv.org/abs/2402.01030 |
| H4 | OpenHands | ICLR | 2025 | Open runtime: event stream, Docker sandbox, delegation, 15-benchmark harness | W2 W4 | https://arxiv.org/abs/2407.16741 |
| H5 | Agentless | FSE | 2025 | Fixed localise→repair→validate pipeline rivals agents at ~$0.70/issue | W2 W5 | https://arxiv.org/abs/2407.01489 |
| H6 | HAL (Holistic Agent Leaderboard) | ICLR | 2026 | 21.7k rollouts over model × scaffold × benchmark; scaffold effects, up to 9× cost gaps | W2 | https://arxiv.org/abs/2510.11977 |
| H7 | AIOS | COLM | 2025 | OS kernel for agents: scheduling, context snapshot/restore, access control | W9 W4 | https://arxiv.org/abs/2403.16971 |
| H8 | SGLang | NeurIPS | 2024 | LM-program DSL + RadixAttention prefix KV reuse | W9 W6 | https://arxiv.org/abs/2312.07104 |
| H9 | Parrot | OSDI | 2024 | Semantic Variables expose app data-flow to the server for end-to-end optimisation | W9 | https://www.usenix.org/conference/osdi24/presentation/lin-chaofan |
| H10 | LLMCompiler | ICML | 2024 | Planner DAG + parallel function calling; up to 3.7× latency, 6.7× cost vs ReAct | W4 W5 | https://arxiv.org/abs/2312.04511 |
| H11 | InferCept | ICML | 2024 | Preserve/swap KV during tool-call interception instead of recompute | W9 | https://proceedings.mlr.press/v235/abhyankar24a.html |
| H12 | Autellix | preprint | 2025 | Program-level scheduling (PLAS/ATLAS); 4–15× throughput vs vLLM | W9 | https://arxiv.org/abs/2502.13965 |
| H13 | KVFlow | NeurIPS | 2025 | Workflow-aware KV eviction + prefetch for multi-agent workflows | W9 W6 | https://arxiv.org/abs/2507.07400 |
| H14 | DSPy | ICLR | 2024 | Declarative LM modules + compiler optimising prompts/demos to a metric | W5 | https://arxiv.org/abs/2310.03714 |
| H15 | Lost in the Middle | TACL | 2024 | U-shaped positional use of long context | W5 | https://aclanthology.org/2024.tacl-1.9/ |
| H16 | Context Length Alone Hurts | Findings EMNLP | 2025 | Length per se degrades accuracy 13.9–85% even with perfect retrieval | W5 | https://arxiv.org/abs/2510.05381 |
| H17 | LLMLingua | EMNLP | 2023 | Small-LM perplexity-based prompt compression, up to 20× | W6 | https://aclanthology.org/2023.emnlp-main.825/ |
| H18 | The Complexity Trap | NeurIPS'25 DL4C *workshop* | 2025 | Observation masking ≈ LLM summarisation at ~½ cost (SWE-agent) | W2 W6 | https://arxiv.org/abs/2508.21433 |
| H19 | ACON | ICML | 2026 | Gradient-free optimisation of compression guidelines; 26–54% lower peak tokens | W2 W6 | https://arxiv.org/abs/2510.00615 |
| H20 | ACE (Agentic Context Engineering) | ICLR | 2026 | Evolving itemised "playbook" context with delta updates | W2 W6 W10 | https://arxiv.org/abs/2510.04618 |
| H21 | ToolRet | Findings ACL | 2025 | Tool-retrieval benchmark (43k tools); general IR retrievers fail | W5 | https://aclanthology.org/2025.findings-acl.1258/ |
| H22 | DeltaBox | preprint | 2026 | Millisecond incremental sandbox checkpoint/rollback | W4 | https://arxiv.org/abs/2605.22781 |

## L2 — Multi-agent systems and orchestration

| ID | Paper | Venue | Year | Core contribution | Tags | Link |
|---|---|---|---|---|---|---|
| M1 | CAMEL | NeurIPS | 2023 | Role-playing agents via inception prompting; MAS as data engine | W1 W3 | https://arxiv.org/abs/2303.17760 |
| M2 | AutoGen | COLM | 2024 | Conversable-agent framework; conversation patterns as programs | W1 W2 | https://arxiv.org/abs/2308.08155 |
| M3 | MetaGPT | ICLR (oral) | 2024 | SOPs as role pipelines; structured docs via publish–subscribe pool | W1 W5 | https://arxiv.org/abs/2308.00352 |
| M4 | Multiagent Debate (Du et al.) | ICML | 2024 | Multi-round debate improves reasoning/factuality | W1 W8 | https://arxiv.org/abs/2305.14325 |
| M5 | MAD / Divergent Thinking (Liang et al.) | EMNLP | 2024 | Affirmative/negative debaters + judge vs "degeneration of thought" | W1 W3 | https://arxiv.org/abs/2305.19118 |
| M6 | More Agents Is All You Need | TMLR | 2024 | Sampling-and-voting scales with agent count — the equal-compute baseline | W5 | https://arxiv.org/abs/2402.05120 |
| M7 | Mixture-of-Agents | ICLR | 2025 | Layered proposers + aggregator; 65.1% LC win rate AlpacaEval 2.0 | W1 W3 | https://arxiv.org/abs/2406.04692 |
| M8 | Should we be going MAD? | ICML | 2024 | Debate doesn't reliably beat self-consistency; hyperparameter-sensitive | — (critique) | https://arxiv.org/abs/2311.17371 |
| M9 | Debate or Vote | NeurIPS (spotlight) | 2025 | Voting explains most debate gains; debate is a martingale | — (critique) | https://arxiv.org/abs/2508.17536 |
| M10 | MacNet | ICLR | 2025 | DAG of 1000+ agents; logistic "collaborative scaling" | W1 W5 | https://arxiv.org/abs/2406.07155 |
| M11 | Towards a Science of Scaling Agent Systems | preprint | 2025 | 260 controlled configs; MAS returns diminish as single agents strengthen | W5 | https://arxiv.org/abs/2512.08296 |
| M12 | Single-agent ≥ MAS at equal thinking budget | preprint | 2026 | Information-theoretic + empirical: single agent matches MAS at equal tokens | W5 | https://arxiv.org/abs/2604.02460 |
| M13 | GPTSwarm | ICML | 2024 | Agents as optimisable computation graphs | W1 W5 | https://arxiv.org/abs/2402.16823 |
| M14 | ADAS / Meta Agent Search | ICLR | 2025 | Meta agent writes new agent programs in code | W1 W5 | https://arxiv.org/abs/2408.08435 |
| M15 | AFlow | ICLR (oral) | 2025 | MCTS over code-represented workflows | W1 W5 | https://arxiv.org/abs/2410.10762 |
| M16 | G-Designer | ICML (spotlight) | 2025 | GNN auto-encoder generates per-query communication topology | W5 | https://arxiv.org/abs/2410.11782 |
| M17 | AgentPrune | ICLR | 2025 | One-shot pruning of redundant inter-agent messages; 28–73% fewer tokens | W5 | https://arxiv.org/abs/2410.02506 |
| M18 | MasRouter | ACL | 2025 | Joint routing of collaboration mode, roles, and LLM per agent | W5 | https://arxiv.org/abs/2502.11133 |
| M19 | Puppeteer (Evolving Orchestration) | NeurIPS | 2025 | RL-trained orchestrator sequences agents dynamically | W1 W3 | https://arxiv.org/abs/2505.19591 |
| M20 | MAST (Why Do MAS Fail?) | NeurIPS (spotlight) | 2025 | 14-mode failure taxonomy, 1,642 annotated traces, LLM annotator | W3 W7 | https://arxiv.org/abs/2503.13657 |
| M21 | Who&When | ICML | 2025 | Failure-attribution benchmark; ≤53.5% agent-level, ≤14.2% step-level | W7 | https://arxiv.org/abs/2505.00212 |
| M22 | Symbolic Guidance for Distributed Coordination | preprint (AAMAS'26 ext. abstract per authors) | 2026 | Partial guidance from classical distributed algorithms beats free-form LLM agents | W5 | https://arxiv.org/abs/2609.31963 |
| G1 | Anthropic multi-agent research system | *engineering blog, not peer-reviewed* | 2025 | Orchestrator–worker; token use explains ~80% of performance variance | W1 W3 | https://www.anthropic.com/engineering/multi-agent-research-system |

Also verified and cited in L2 but not profiled: ChatDev (ACL'24), AgentVerse (ICLR'24), "Rethinking the Bounds…" (ACL'24), MaAS (ICML'25), GovSim (NeurIPS'24).

## L3 — Memory

| ID | Paper | Venue | Year | Core contribution | Tags | Link |
|---|---|---|---|---|---|---|
| R1 | Generative Agents | UIST | 2023 | Memory stream + recency/importance/relevance retrieval + reflection | W3 W10 | https://arxiv.org/abs/2304.03442 |
| R2 | MemGPT | preprint | 2023 | OS-style virtual context paging via function calls | W5 W8 | https://arxiv.org/abs/2310.08560 |
| R3 | MemoryBank | AAAI | 2024 | Ebbinghaus-curve forgetting for companion chatbots | W3 W5 | https://ojs.aaai.org/index.php/AAAI/article/view/29946 |
| R4 | Voyager | TMLR | 2024 | Executable skill library as procedural memory | W4 W10 | https://arxiv.org/abs/2305.16291 |
| R5 | ExpeL | AAAI | 2024 | Cross-task insight extraction + trajectory retrieval | W3 W10 | https://arxiv.org/abs/2308.10144 |
| R6 | A-MEM | NeurIPS | 2025 | Zettelkasten-style linked, evolving notes | W3 W5 W10 | https://arxiv.org/abs/2502.12110 |
| R7 | Mem0 | preprint | 2025 | Fact extraction with ADD/UPDATE/DELETE/NOOP consolidation; graph variant | W3 W5 W10 | https://arxiv.org/abs/2504.19413 |
| R8 | Zep / Graphiti | preprint | 2025 | Bi-temporal KG memory invalidating superseded facts | W3 W5 | https://arxiv.org/abs/2501.13956 |
| R9 | HippoRAG | NeurIPS | 2024 | Hippocampal-indexing KG + Personalized PageRank retrieval | W5 | https://arxiv.org/abs/2405.14831 |
| R10 | HippoRAG 2 | ICML | 2025 | RAG as non-parametric continual learning | W5 | https://arxiv.org/abs/2502.14802 |
| R11 | MemoryOS | EMNLP (per authors' README) | 2025 | Three-tier short/mid/long-term memory with OS-style promotion | W3 W5 | https://arxiv.org/abs/2506.06326 |
| R12 | LoCoMo | ACL | 2024 | Very-long multi-session dialogue memory benchmark | W5 | https://aclanthology.org/2024.acl-long.747 |
| R13 | LongMemEval | ICLR | 2025 | 500-question benchmark of five memory abilities | W3 | https://arxiv.org/abs/2410.10813 |
| R14 | MemoryAgentBench | ICLR | 2026 | Retrieval, test-time learning, long-range understanding, selective forgetting | — | https://arxiv.org/abs/2507.05257 |
| R15 | Agent Workflow Memory | ICML | 2025 | Reusable workflows induced from web-agent trajectories | W10 | https://proceedings.mlr.press/v267/wang25bx.html |
| R16 | MemoryLLM | ICML | 2024 | ~1B-param latent memory pool, self-updatable | W5 | https://arxiv.org/abs/2402.04624 |
| R17 | MEM1 | ICLR | 2026 | RL-trained constant-size state merging memory and reasoning | W5 | https://arxiv.org/abs/2506.15841 |
| R18 | AgentPoison | NeurIPS | 2024 | Memory/KB backdoor via optimised triggers | W5 | https://arxiv.org/abs/2407.12784 |
| R19 | MINJA | NeurIPS | 2025 | Memory injection via queries only, no write access | W5 | https://arxiv.org/abs/2503.03704 |
| R20 | Memory-R1 | ACL | 2026 | RL-learned memory ops + answering from 152 QA pairs | W3 W5 | https://aclanthology.org/2026.acl-long.583 |
| R21 | ReasoningBank | ICLR | 2026 | Strategy memory from successes and failures; memory-aware test-time scaling | W3 W10 | https://arxiv.org/abs/2509.25140 |
| RS1 | Zhang et al., agent-memory survey | ACM TOIS (per authors; DOI not verified) | 2024/25 | Survey | — | https://arxiv.org/abs/2404.13501 |
| RS2 | Hu et al., Memory in the Age of AI Agents | preprint | 2025 | Survey taxonomy (forms, functions, dynamics) | — | https://arxiv.org/abs/2512.13564 |

## L4 — Planning, reflection, tool use

| ID | Paper | Venue | Year | Core contribution | Tags | Link |
|---|---|---|---|---|---|---|
| P1 | ReAct | ICLR | 2023 | (= H1) | W2 W8 | https://arxiv.org/abs/2210.03629 |
| P2 | Tree of Thoughts | NeurIPS | 2023 | BFS/DFS over thoughts, LM as evaluator | W1 W3 W4 | https://arxiv.org/abs/2305.10601 |
| P3 | RAP | EMNLP | 2023 | LLM as world model + MCTS | W1 W4 | https://arxiv.org/abs/2305.14992 |
| P4 | LATS | ICML | 2024 | MCTS unifying acting, value, reflection | W1 W3 W4 | https://proceedings.mlr.press/v235/zhou24r.html |
| P5 | ADaPT | Findings NAACL | 2024 | Decompose only when the executor fails | W3 | https://arxiv.org/abs/2311.05772 |
| P6 | PlanBench | NeurIPS D&B | 2023 | IPC-domain planning benchmark with validator + obfuscated variants | — | https://arxiv.org/abs/2206.10498 |
| P7 | LLM-Modulo | ICML (position) | 2024 | LLMs can't plan alone; pair with sound external verifiers | — (position) | https://arxiv.org/abs/2402.01817 |
| P8 | On the Self-Verification Limitations… (Stechly et al.) | ICLR | 2025 | Self-critique collapses; sound verifier helps; resampling keeps most gain | — (critique) | https://arxiv.org/abs/2402.08115 |
| P9 | Reflexion | NeurIPS | 2023 | Verbal self-reflection stored in episodic memory | W1 W3 | https://arxiv.org/abs/2303.11366 |
| P10 | Self-Refine | NeurIPS | 2023 | Generate–critique–refine with one LLM | W1 W3 | https://arxiv.org/abs/2303.17651 |
| P11 | CRITIC | ICLR | 2024 | Tool-grounded self-correction | W1 | https://arxiv.org/abs/2305.11738 |
| P12 | LLMs Cannot Self-Correct Reasoning Yet | ICLR | 2024 | Intrinsic self-correction hurts; earlier gains used oracle labels | — (critique) | https://arxiv.org/abs/2310.01798 |
| P13 | When Can LLMs Actually Correct Their Own Mistakes? (Kamoi et al.) | TACL | 2024 | Survey + checklist for fair self-correction experiments | — | https://arxiv.org/abs/2406.01297 |
| P14 | SCoRe | ICLR | 2025 | Multi-turn RL to train self-correction | W5 | https://arxiv.org/abs/2409.12917 |
| P15 | Toolformer | NeurIPS | 2023 | Self-supervised learning of API calls | W5 | https://arxiv.org/abs/2302.04761 |
| P16 | Gorilla | NeurIPS | 2024 | Retriever-aware fine-tuning for API calls; APIBench | W5 W8 | https://arxiv.org/abs/2305.15334 |
| P17 | API-Bank | EMNLP | 2023 | Runnable tool benchmark at three levels | W5 | https://arxiv.org/abs/2304.08244 |
| P18 | ToolLLM / ToolBench | ICLR | 2024 | 16k real APIs, DFSDT, ToolEval | W3 W8 | https://arxiv.org/abs/2307.16789 |
| P19 | Tool Learning with LLMs: A Survey (Qu et al.) | Frontiers of CS (per arXiv) | 2024 | Survey | — | https://arxiv.org/abs/2405.17935 |
| P20 | MCPGauge ("Help or Hurdle?") | preprint | 2025 | MCP access cuts accuracy 9.5% avg; 3–236× input tokens | W5 | https://arxiv.org/abs/2508.12566 |
| P21 | Search-R1 | COLM | 2025 | Outcome-reward RL for interleaved search + reasoning | W4 W5 | https://arxiv.org/abs/2503.09516 |
| P22 | ReTool | ICLR | 2026 | RL with code-interpreter calls in reasoning | W4 W5 | https://arxiv.org/abs/2504.11536 |
| P23 | RAGEN / StarPO | preprint | 2025 | Trajectory-level multi-turn agent RL; "Echo Trap" | W4 W5 | https://arxiv.org/abs/2504.20073 |
| P24 | Thinking vs. Doing (TTI) | preprint (NeurIPS'25 workshop) | 2025 | Scaling interaction steps at test time via curriculum RL | W3 W4 | https://arxiv.org/abs/2506.07976 |

## L5 — Evaluation, reliability, verification

| ID | Paper | Venue | Year | Core contribution | Tags | Link |
|---|---|---|---|---|---|---|
| E1 | AgentBench | ICLR | 2024 | 8-environment LLM-as-agent benchmark | W2 | https://arxiv.org/abs/2308.03688 |
| E2 | WebArena | ICLR | 2024 | Self-hosted realistic websites, functional-correctness grading | W2 W5 | https://arxiv.org/abs/2307.13854 |
| E3 | SWE-bench | ICLR | 2024 | 2,294 real GitHub issues, test-verified | W2 W5 | https://arxiv.org/abs/2310.06770 |
| E4 | GAIA | ICLR | 2024 | 466 human-easy assistant questions, exact match | W2 | https://arxiv.org/abs/2311.12983 |
| E5 | τ-bench | ICLR | 2025 | Simulated-user tool benchmark; introduces **pass^k** | W3 W5 | https://arxiv.org/abs/2406.12045 |
| E6 | τ²-bench | ICML (per OpenReview) | 2026 | Dual control: user and agent both act on shared state | W3 | https://arxiv.org/abs/2506.07982 |
| E7 | OSWorld | NeurIPS D&B | 2024 | Real-OS VMs, 369 execution-graded tasks | W2 | https://arxiv.org/abs/2404.07972 |
| E8 | AgentBoard | NeurIPS (oral) | 2024 | Progress-rate metric for partial progress | W2 | https://arxiv.org/abs/2401.13178 |
| E9 | TheAgentCompany | NeurIPS D&B | 2025 | Simulated software company, 175 tasks, checkpoint grading | W2 W3 | https://arxiv.org/abs/2412.14161 |
| E10 | AI Agents That Matter | TMLR | 2025 | Cost–accuracy Pareto, holdouts, reproducibility | — | https://arxiv.org/abs/2407.01502 |
| E11 | HAL | ICLR | 2026 | (= H6) | W2 | https://arxiv.org/abs/2510.11977 |
| E12 | Agentic Benchmark Checklist (ABC) | NeurIPS D&B | 2025 | Grading flaws mis-estimate by up to 100% relative; checklist | — | https://arxiv.org/abs/2507.02825 |
| E13 | SWE-Bench Illusion | preprint | 2025 | Memorisation evidence on SWE-bench Verified | — | https://arxiv.org/abs/2506.12286 |
| E14 | ToolEmu | ICLR (spotlight) | 2024 | LM-emulated tools + LM safety evaluator | W3 | https://arxiv.org/abs/2309.15817 |
| E15 | AgentDojo | NeurIPS D&B | 2024 | Prompt-injection attack/defence environment | W5 | https://arxiv.org/abs/2406.13352 |
| E16 | InjecAgent | Findings ACL | 2024 | 1,054-case indirect prompt-injection benchmark | W5 | https://arxiv.org/abs/2403.02691 |
| E17 | Agent-SafetyBench | preprint | 2024 | 2,000 cases, 8 risk types; no agent >60% safe | W3 | https://arxiv.org/abs/2412.14470 |
| E18 | Agent-as-a-Judge | ICML | 2025 | Agentic judge + DevAI benchmark | W3 | https://arxiv.org/abs/2410.10934 |
| E19 | AgentPRM | preprint | 2025 | Step-level process reward (promise + progress) | W5 | https://arxiv.org/abs/2511.08325 |
| E20 | MIRAGE-Bench | preprint | 2025 | Taxonomy + benchmark of agent action hallucination | W3 | https://arxiv.org/abs/2507.21017 |
| E21 | The Reasoning Trap | ACL | 2026 | Stronger reasoning increases tool hallucination | W3 | https://arxiv.org/abs/2510.22977 |
| E22 | SAUP | ACL | 2025 | Situational uncertainty propagation across agent steps | W5 W7 | https://aclanthology.org/2025.acl-long.302 |
| E23 | MAST | NeurIPS | 2025 | (= M20) | W3 W7 | https://arxiv.org/abs/2503.13657 |
| E24 | Who&When | ICML | 2025 | (= M21) | W7 | https://arxiv.org/abs/2505.00212 |
| E25 | GA-Rollback | EMNLP | 2025 | Assistant-verifier-triggered rollback | W4 W5 | https://arxiv.org/abs/2503.02519 |

Supplementary, verified in L5: VisualWebArena (ACL'24), R-Judge (Findings EMNLP'24), SWE-Gym (ICML'25), ToolBeHonest (EMNLP'24), KnowNo (CoRL'23), Chain-of-Verification (Findings ACL'24), SelfCheckGPT (EMNLP'23), ACRFence (workshop'26), DART (preprint'26), AgentOps (preprint), AgentSight (workshop'25).

---

## Tag frequency (rough count of tagged rows; profiled rows only)

| Tag | Approx. rows | Comment |
|---|---|---|
| W5 narrow / flawed benchmarks | ~50 | Near universal |
| W3 LLM self-eval / judge dependence | ~30 | Reaches every layer of the evaluation stack |
| W1 no compute-matched baseline | ~20 | Concentrated in MAS and reflection/search |
| W2 single-run, no reliability metric | ~20 | Even HAL ranks mainly on accuracy and cost |
| W4 reversible-world assumption | ~15 | Search, RL, rollback, runtimes |
| W6 isolated optimisation | ~10 | Context compression vs KV caching |
| W9 proxy workloads | ~7 | Systems papers |
| W10 persistent-state integrity | ~10 | Memory and playbook systems |
| W7 diagnosis without remedy | ~4 | Failure-taxonomy and attribution papers |
| W8 closed / deprecated models | ~6 | Older foundational papers |

These counts are my assessment from the tags above, not a systematic coding study. Treat them as
indicative only.

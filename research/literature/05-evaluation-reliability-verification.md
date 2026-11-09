# Slice 05: Agent Evaluation, Reliability, Observability, Failure Recovery, Verification, and Hallucination Reduction

*Compiled 2026-11-08. Each entry was checked against a primary source: the arXiv abstract page or arXiv API metadata, plus OpenReview, ACL Anthology or neurips.cc for venues. A venue is given only when acceptance was confirmed. Otherwise the entry says "arXiv preprint". Limitations are tagged **(stated)** when the authors say so in the paper and **(assessment)** when they are my reading.*

## Scope

This slice covers how LLM agents are **measured** and how they are made **dependable**. It includes:

- interactive capability benchmarks (AgentBench, WebArena, SWE-bench, GAIA, OSWorld, τ-bench/τ²-bench, AgentBoard, TheAgentCompany);
- critiques of evaluation practice itself (cost-aware and reproducible evaluation, benchmark-validity checklists, contamination);
- safety and robustness evaluation (ToolEmu, AgentDojo, InjecAgent, Agent-SafetyBench);
- trajectory-level judging and step-level verifiers (Agent-as-a-Judge, AgentPRM);
- agent and tool-call hallucination (MIRAGE-Bench, the "Reasoning Trap");
- multi-step uncertainty estimation (SAUP);
- failure analysis and attribution (MAST, Who&When);
- rollback-based recovery (GA-Rollback).

Observability and tracing have almost no peer-reviewed literature. The verified preprints are listed in the supplementary section, and the gap is discussed at the end. There are 25 main entries. A further 16 verified works are listed briefly at the end because they are foundational, adjacent, or too new or thin for a full entry.

---

## A. Capability benchmarks

### 1. AgentBench
- **Title:** AgentBench: Evaluating LLMs as Agents
- **Authors:** Xiao Liu, Hao Yu, Hanchen Zhang, et al.
- **Venue:** ICLR 2024 (arXiv comment: "Published in ICLR 2024")
- **Year:** 2024 (arXiv 2023)
- **Link:** https://arxiv.org/abs/2308.03688
- **Core contribution:** One of the first multi-environment benchmarks that treats the LLM itself as the agent. It exposes a large gap between top API models and open models of 70B parameters or fewer.
- **Methodology:** Eight interactive environments covering code-, game- and web-grounded tasks. Many API and open-weight LLMs are run under a common multi-turn protocol. Failures are categorised, for example as invalid format, invalid action, or exceeding the task limit.
- **Datasets/benchmarks:** Eight environments: OS, DB, knowledge graph, digital card game, lateral-thinking puzzles, house-holding (ALFWorld-derived), web shopping, and web browsing.
- **Evaluation metrics:** Per-environment success rate or F1/reward, combined into a weighted overall score. Failure-reason distribution.
- **Limitations:** The authors' failure analysis attributes weak performance to "poor long-term reasoning, decision-making, and instruction following" (stated). The fixed, simple prompting scaffold means scores conflate model ability with harness design (assessment). Single-run success rates, with no variance or reliability across repeated runs (assessment). The static environments are now partly saturated and exposed to contamination (assessment).
- **Code availability:** https://github.com/THUDM/AgentBench (linked in abstract)
- **Unresolved research gaps:** How to separate model capability from scaffold effects. How to measure consistency (pass^k) rather than single-shot success. How to keep a multi-environment suite fresh.

### 2. WebArena
- **Title:** WebArena: A Realistic Web Environment for Building Autonomous Agents
- **Authors:** Shuyan Zhou, Frank F. Xu, Hao Zhu, et al.
- **Venue:** ICLR 2024 (OpenReview: ICLR 2024 poster)
- **Year:** 2024 (arXiv 2023)
- **Link:** https://arxiv.org/abs/2307.13854
- **Core contribution:** A self-hostable, reproducible web environment with fully functional websites, plus long-horizon tasks graded on functional correctness rather than action matching.
- **Methodology:** Docker-hosted sites in four domains (e-commerce, forum, collaborative software development, CMS) plus tools such as a map and knowledge bases such as manuals. Task outcomes are checked by programmatic validators on answers or site state.
- **Datasets/benchmarks:** The WebArena task set, introduced here.
- **Evaluation metrics:** End-to-end task success rate. Best GPT-4 agent: 14.41%. Humans: 78.24%.
- **Limitations:** Later audits found that substring matching and LLM-judged "N/A" tasks can accept wrong or empty answers (Zhu et al. 2025, entry 12) (assessment, from independent work). The snapshot websites drift from the live web (assessment). The text-centric observation design motivated the multimodal follow-up VisualWebArena (see supplementary) (assessment).
- **Code availability:** https://webarena.dev/ (linked in arXiv comment)
- **Unresolved research gaps:** Robust outcome validators. Evaluation of side effects and safety in web tasks. Reliability across repeated runs.

### 3. SWE-bench
- **Title:** SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
- **Authors:** Carlos E. Jimenez, John Yang, Alexander Wettig, et al.
- **Venue:** ICLR 2024 (arXiv comment cites the OpenReview forum)
- **Year:** 2024 (arXiv 2023)
- **Link:** https://arxiv.org/abs/2310.06770
- **Core contribution:** Turned real GitHub issues and their merged PRs into an execution-verified repository-level coding benchmark. It became the de facto evaluation for coding agents.
- **Methodology:** 2,294 issue–PR pairs from 12 Python repositories. The model edits the codebase. Success means the PR's fail-to-pass tests pass and the pass-to-pass tests still pass. Also releases the fine-tuned SWE-Llama.
- **Datasets/benchmarks:** SWE-bench, introduced here. SWE-bench Verified, the human-validated subset used widely since, was released as an OpenAI blog post, not a paper (see dropped seeds).
- **Evaluation metrics:** % of issues resolved. Claude 2 resolved 1.96% at release.
- **Limitations:** Python only, drawn from 12 popular repositories (assessment). The unit tests can be insufficient, so a passing patch may still be wrong (assessment, documented by Zhu et al. 2025). Popular repositories invite memorisation (assessment, documented by Liang et al. 2025, entry 13).
- **Code availability:** https://www.swebench.com (data, code and leaderboard, linked in arXiv comment)
- **Unresolved research gaps:** Contamination-resistant and continuously refreshed task sources. Patch-correctness oracles stronger than the repository's own tests. Non-Python and non-library software.

### 4. GAIA
- **Title:** GAIA: a benchmark for General AI Assistants
- **Authors:** Grégoire Mialon, Clémentine Fourrier, Craig Swift, Thomas Wolf, Yann LeCun, Thomas Scialom
- **Venue:** ICLR 2024 (OpenReview: ICLR 2024 poster)
- **Year:** 2024 (arXiv 2023)
- **Link:** https://arxiv.org/abs/2311.12983
- **Core contribution:** Questions that are conceptually simple for humans but need multi-step tool use (browsing, multimodality, file handling) and have short, unambiguous answers. This allows exact-match grading of open-ended assistants.
- **Methodology:** 466 human-written questions in three difficulty levels. Answers to 300 are withheld for a hosted leaderboard.
- **Datasets/benchmarks:** GAIA, introduced here.
- **Evaluation metrics:** Exact-match accuracy per level. Humans: 92%. GPT-4 with plugins: 15%.
- **Limitations:** Grading by final answer only ignores how the answer was reached, including unsafe or wasteful trajectories (assessment). Static web-dependent questions decay as web content changes, and the public validation split invites overfitting (assessment). HAL's log analysis (entry 11) found agents searching for benchmark answers online (assessment, from independent work).
- **Code availability:** Leaderboard and data at https://huggingface.co/gaia-benchmark (linked in abstract). Code: not verified.
- **Unresolved research gaps:** Process-level scoring. Protection against answer lookup and leakage. Renewal as the web drifts.

### 5. τ-bench
- **Title:** τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains
- **Authors:** Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan
- **Venue:** ICLR 2025 (OpenReview: ICLR 2025 poster)
- **Year:** 2025 (arXiv 2024)
- **Link:** https://arxiv.org/abs/2406.12045
- **Core contribution:** A conversational tool-use benchmark with an LLM-simulated user and domain policy documents. Introduces **pass^k**, the probability that all *k* independent trials of a task succeed, as a reliability metric.
- **Methodology:** The agent gets domain APIs and a policy. An LM simulates the user. Grading compares the final database state with an annotated goal state. The unbiased pass^k estimator is E_task[C(c,k)/C(n,k)].
- **Datasets/benchmarks:** τ-retail (115 tasks) and τ-airline (50 tasks).
- **Evaluation metrics:** pass^1 and pass^k. GPT-4o: under 50% pass^1 and pass^8 under 25% in retail.
- **Limitations:** User instructions "might contain typos or ambiguities" (stated). The user-simulator LM "might have limited capacity at reasoning, calculation, long-context memorization" (stated). Reward "might be a necessary but not sufficient condition" for success (stated). "Implicit bias during the task curation process" (stated). Zhu et al. (entry 12) later report that roughly 38% of airline tasks can be passed by doing nothing, and that a database-dumping agent can pass substring checks (assessment, from independent work).
- **Code availability:** https://github.com/sierra-research/tau-bench (linked in paper)
- **Unresolved research gaps:** Validity of the user simulator. Reliability metrics beyond pass^k, such as consistency under paraphrase or perturbation. Grading policy compliance separately from end state.

### 6. τ²-bench
- **Title:** τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment
- **Authors:** Victor Barres, Honghua Dong, Soham Ray, Xujie Si, Karthik Narasimhan
- **Venue:** ICML 2026 (OpenReview venue field: "ICML 2026 spotlight". The first author's CV also lists acceptance at ICML 2026.)
- **Year:** 2026 (arXiv 2025)
- **Link:** https://arxiv.org/abs/2506.07982
- **Core contribution:** Extends τ-bench to **dual control**: both user and agent act on a shared world state, as in technical support. This tests whether agents can guide users, not just call tools themselves.
- **Methodology:** A Telecom domain modelled as a Dec-POMDP. A compositional task generator builds verifiable tasks from atomic components. A user simulator is constrained by tools and observable state. Ablations separate reasoning errors from communication and coordination errors.
- **Datasets/benchmarks:** New Telecom dual-control domain, plus τ-bench domains.
- **Evaluation metrics:** Task success / pass^k, compared across no-user and dual-control conditions.
- **Limitations:** Performance drops sharply from no-user to dual-control (stated, as a finding). Only one new dual-control domain (assessment). Simulator fidelity is improved but still LM-based, so measured "user guidance" ability is bounded by simulator realism (assessment).
- **Code availability:** not verified (not seen on the paper page)
- **Unresolved research gaps:** Validated human-in-the-loop baselines. More dual-control domains. Metrics for communication quality.

### 7. OSWorld
- **Title:** OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments
- **Authors:** Tianbao Xie, Danyang Zhang, Jixuan Chen, et al.
- **Venue:** NeurIPS 2024 Datasets and Benchmarks Track (OpenReview: poster)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2404.07972
- **Core contribution:** A real-OS virtual-machine environment (Ubuntu, Windows, macOS) with execution-based evaluation scripts for open-ended computer-use tasks.
- **Methodology:** 369 tasks drawn from real use cases. Each has an initial-state configuration and a custom evaluation script. LLM/VLM agents are tested under several observation modalities.
- **Datasets/benchmarks:** OSWorld, introduced here.
- **Evaluation metrics:** Task success rate. Humans: 72.36%. Best model at release: 12.24%.
- **Limitations:** The authors identify GUI grounding and operational knowledge as the main failure sources (stated, as a finding). Tasks that depend on live websites break over time: Zhu et al. (entry 12) report that 13 of 46 Chrome tasks were broken, underestimating one agent by 28% (assessment, from independent work). The VM setup is costly to run at scale (assessment).
- **Code availability:** https://os-world.github.io (code, environment and data, linked in abstract)
- **Unresolved research gaps:** Keeping task validity stable over time. Efficiency and latency metrics. Safe evaluation of irreversible OS actions.

### 8. AgentBoard
- **Title:** AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents
- **Authors:** Chang Ma, Junlei Zhang, Zhihao Zhu, et al.
- **Venue:** NeurIPS 2024 (oral). Confirmed by the arXiv comment and the neurips.cc oral page. Which track it appeared in was not verified.
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2401.13178
- **Core contribution:** Introduces a fine-grained **progress rate** metric for partial progress in multi-turn, partially observable tasks, plus an analytical toolkit that goes beyond final success.
- **Methodology:** Nine tasks reformulated in a unified multi-turn framework, with annotated subgoals for computing progress. The toolkit breaks results down by ability dimension, such as grounding, planning, and world modelling.
- **Datasets/benchmarks:** AlfWorld, ScienceWorld, BabyAI, Jericho, PDDL, WebShop, WebArena, Tool-Query, Tool-Operation (unified versions).
- **Evaluation metrics:** Success rate, progress rate, per-ability scores.
- **Limitations:** Progress rate depends on hand-annotated subgoals, which assume one canonical decomposition (assessment). The tasks are all text-based (assessment).
- **Code availability:** not verified (repository not seen on a primary page)
- **Unresolved research gaps:** Automatic, decomposition-agnostic progress estimation, which links to PRMs (entry 19). Checking whether progress rate predicts eventual success.

### 9. TheAgentCompany
- **Title:** TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks
- **Authors:** Frank F. Xu, Yufan Song, Boxuan Li, et al.
- **Venue:** NeurIPS 2025 Datasets and Benchmarks Track (OpenReview: poster)
- **Year:** 2025 (arXiv 2024)
- **Link:** https://arxiv.org/abs/2412.14161
- **Core contribution:** A self-contained simulated software company in which agents browse, code, run programs and message LLM-simulated colleagues to complete realistic professional tasks.
- **Methodology:** 175 tasks on self-hosted GitLab, OwnCloud, Plane and RocketChat. Checkpoint-based grading, with simulated coworkers backed by Claude 3.5 Sonnet.
- **Datasets/benchmarks:** TheAgentCompany, introduced here.
- **Evaluation metrics:** Full-completion rate, and a partial score of 0.5·(checkpoint points / total) + 0.5·(full completion). Best model, Gemini 2.5 Pro: 30.3% full and 39.3% partial.
- **Limitations:** Tasks are "generally on the more straightforward side" and automatically checkable (stated). Only two agent scaffolds tested (stated). No human professional baseline (stated). Tasks were chosen largely by author judgment (stated). No creative work (stated). An LLM also acts as judge for some deliverables, adding judge variance (assessment).
- **Code availability:** https://the-agent-company.com (code, data and environment, linked in abstract)
- **Unresolved research gaps:** Human baselines. Measuring the cost and consequences of partial or erroneous work in workplace settings.

---

## B. Evaluation methodology, reproducibility, and benchmark validity

### 10. AI Agents That Matter
- **Title:** AI Agents That Matter
- **Authors:** Sayash Kapoor, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, Arvind Narayanan
- **Venue:** TMLR. The OpenReview record reads "Accepted by TMLR". The year 2025 comes from the first author's CV and mlanthology. The TMLR page itself was not opened.
- **Year:** 2025 (TMLR); arXiv 2024
- **Link:** https://arxiv.org/abs/2407.01502
- **Core contribution:** A critique of agent benchmarking. It argues for joint cost–accuracy evaluation (Pareto frontiers), separate model-developer and downstream-developer benchmarks, proper holdout sets, and standardised, reproducible evaluation.
- **Methodology:** Re-evaluation of published agents, for example on HumanEval, showing that simple, cheap baselines match complex agents. A demonstration of joint cost/accuracy optimisation. A taxonomy of holdout levels to prevent shortcuts.
- **Datasets/benchmarks:** Analysis across existing agent benchmarks, centred on HumanEval-based coding agents. The full list of benchmarks analysed was not verified.
- **Evaluation metrics:** Accuracy against dollar cost (Pareto frontier). Reproducibility checks.
- **Limitations:** Mostly a position paper with case studies. The proposed practices were not tested at scale until HAL (entry 11) (assessment). Dollar cost is unstable because API prices change (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:** Cost metrics that do not change with price; reporting latency and energy. Community enforcement of holdout practice.

### 11. Holistic Agent Leaderboard (HAL)
- **Title:** Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation
- **Authors:** Sayash Kapoor, Benedikt Stroebl, Peter Kirgis, et al.
- **Venue:** ICLR 2026 (OpenReview: ICLR 2026 poster)
- **Year:** 2026 (arXiv 2025)
- **Link:** https://arxiv.org/abs/2510.11977
- **Core contribution:** A standardised, parallelised evaluation harness and leaderboard that evaluates across models, scaffolds and benchmarks, with LLM-aided inspection of logs to find hidden agent behaviours.
- **Methodology:** 21,730 rollouts covering 9 models × 9 benchmarks, at about $40k, run in parallel across hundreds of VMs. Three-way analysis of model × scaffold × benchmark. LLM-assisted log rubrics cover tool-use failures, self-correction, verification, environmental barriers, shortcuts and instruction violations. 2.5B tokens of logs are released.
- **Datasets/benchmarks:** Online Mind2Web, AssistantBench, GAIA, CORE-Bench Hard, ScienceAgentBench, SciCode, SWE-bench Verified Mini, TAU-bench Airline, USACO.
- **Evaluation metrics:** Accuracy, dollar cost, tokens, cost–accuracy Pareto frontiers, effect of reasoning effort, and behaviour rates from log analysis.
- **Limitations:** HAL is "an ongoing project" (stated). Parallel runs add latency variance "due to issues such as rate-limit errors" (stated). One scaffold was excluded after log analysis revealed data leakage (stated, as a finding). Findings depend on the chosen scaffolds and on an LLM log inspector whose own error rate limits how much the behaviour findings can be trusted (assessment).
- **Code availability:** https://github.com/princeton-pli/hal-harness. Logs at https://huggingface.co/datasets/agent-evals/hal_traces (linked in paper).
- **Unresolved research gaps:** Validated automatic log auditing. Reliability metrics (pass^k-style) on the leaderboard. Keeping cross-benchmark comparisons current as models change.

### 12. Agentic Benchmark Checklist (ABC)
- **Title:** Establishing Best Practices for Building Rigorous Agentic Benchmarks
- **Authors:** Yuxuan Zhu, Tengjun Jin, Yada Pruksachatkun, et al.
- **Venue:** NeurIPS 2025 Datasets and Benchmarks Track (OpenReview: poster; the OpenReview title reads "…Best Practices *in* Building…")
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2507.02825
- **Core contribution:** Shows that common agentic benchmarks have task-setup and reward-design flaws that can mis-estimate performance by up to 100% in relative terms. Proposes the Agentic Benchmark Checklist.
- **Methodology:** The checklist has three parts: task validity (T.1–T.10), outcome validity (organised by outcome type) and reporting (R.1–R.13). It was applied to ten open benchmarks and used to repair CVE-Bench.
- **Datasets/benchmarks:** Audited SWE-bench (Verified), SWE-Lancer, KernelBench, BIRD, Cybench, MLE-bench, GAIA, τ-bench, WebArena and OSWorld. CVE-Bench case study.
- **Evaluation metrics:** Checklist compliance scores, and estimated over- or under-estimation of agent performance. ABC reduced CVE-Bench overestimation by 33%.
- **Limitations:** The checklist may not be exhaustive (stated). Findings "only reflect the state" of each benchmark at the time of writing (stated). The appendix says the analysis "covered only 17 agentic benchmarks" (stated). Compliance scoring is manual and partly subjective (assessment).
- **Code availability:** https://github.com/uiuc-kang-lab/agentic-benchmarks (linked in paper)
- **Unresolved research gaps:** Automated benchmark auditing, for example adversarial "null agents" that probe shortcuts. Continuous validity monitoring.

### 13. The SWE-Bench Illusion
- **Title:** The SWE-Bench Illusion: When State-of-the-Art LLMs Remember Instead of Reason
- **Authors:** Shanchao Liang, Spandan Garg, Roshanak Zilouchian Moghaddam
- **Venue:** arXiv preprint
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2506.12286
- **Core contribution:** Diagnostic evidence that SWE-bench Verified scores may be partly inflated by memorisation or contamination.
- **Methodology:** Two probes. (i) Identify the buggy file path from the issue text alone, with no repository access. (ii) Reproduce the ground-truth function from the issue and the current file only, measuring verbatim n-gram overlap. Results are compared with control tasks from repositories outside SWE-bench.
- **Datasets/benchmarks:** SWE-bench Verified and Full. Controls: 245 tasks from seven repositories outside SWE-bench, RefactorBench, an internal SWE-bench C# set, and SWE-bench-Extra (fresh issues).
- **Evaluation metrics:** File-path accuracy (up to 76% on Verified vs. up to 53% on outside repositories). Consecutive 5-gram accuracy (up to 35% vs. 18%).
- **Limitations:** Only one OpenAI reasoning model was used for function reproduction because of resources (stated). The RefactorBench comparison has confounders (stated). N-gram similarity is "a noisy indicator" (stated). The evidence is correlational: it does not prove that end-to-end resolve rates are inflated (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:** Causal contamination tests for agentic, as opposed to single-shot, benchmarks. Live or held-out task streams.

---

## C. Safety and robustness evaluation

### 14. ToolEmu
- **Title:** Identifying the Risks of LM Agents with an LM-Emulated Sandbox
- **Authors:** Yangjun Ruan, Honghua Dong, Andrew Wang, et al.
- **Venue:** ICLR 2024 (OpenReview: ICLR 2024 spotlight)
- **Year:** 2024 (arXiv 2023)
- **Link:** https://arxiv.org/abs/2309.15817
- **Core contribution:** Uses an LM to emulate tool execution, including adversarial emulation, so that agent risks can be tested without implementing the tools. Adds an LM-based automatic safety evaluator.
- **Methodology:** An emulator LM generates tool outputs, and a red-teaming variant steers toward risky states. An evaluator LM scores the risk and helpfulness of trajectories. Both are validated by human evaluation.
- **Datasets/benchmarks:** 36 high-stakes toolkits and 144 test cases, curated here.
- **Evaluation metrics:** Failure incidence and safety/helpfulness scores. 68.8% of ToolEmu-identified failures were judged valid real-world failures. The safest agent still failed 23.9% of the time.
- **Limitations:** 68.8% validity means about a third of flagged failures may be artefacts of emulation (stated, as a finding). Both emulator and evaluator are LMs, so they can share blind spots with the agents under test (assessment). Small test set (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:** Measuring how faithful emulators are. Transfer of emulated risk findings to real tool deployments.

### 15. AgentDojo
- **Title:** AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents
- **Authors:** Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr
- **Venue:** NeurIPS 2024 Datasets and Benchmarks Track (OpenReview: poster)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2406.13352
- **Core contribution:** An extensible environment, rather than a static suite, for co-evaluating agent utility and prompt-injection robustness under adaptive attacks and defenses.
- **Methodology:** Stateful tool environments with user tasks and injection tasks. Attacks are injected into tool outputs. Defenses evaluated: data delimiters, injection detector, prompt sandwiching, and tool filter.
- **Datasets/benchmarks:** 97 tasks and 629 security cases across Workspace, Slack, Banking and Travel suites.
- **Evaluation metrics:** Benign utility, utility under attack, targeted attack success rate.
- **Limitations:** The tool filter "fails when the list of tools… cannot be planned in advance" (stated). The detector "has too many false positives" and hurts utility (stated). Growing the benchmark may require automating task specification (stated). English-only, text-only tool environments (assessment).
- **Code availability:** https://github.com/ethz-spylab/agentdojo (linked in abstract)
- **Unresolved research gaps:** Defenses with provable guarantees. Measuring the security–utility trade-off in multimodal and computer-use agents.

### 16. InjecAgent
- **Title:** InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents
- **Authors:** Qiusi Zhan, Zhixiang Liang, Zifan Ying, Daniel Kang
- **Venue:** Findings of ACL 2024 (arXiv comment: "ACL 2024 Findings")
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2403.02691
- **Core contribution:** An early dedicated benchmark for indirect prompt injection (IPI) in tool-using agents. Attack intents are split into direct harm and data exfiltration.
- **Methodology:** 1,054 test cases combining 17 user tools and 62 attacker tools, run in base and "enhanced" settings where the injected instruction is reinforced with a hacking prompt.
- **Datasets/benchmarks:** InjecAgent, introduced here.
- **Evaluation metrics:** Attack success rate. ReAct-prompted GPT-4: 24%, nearly doubling in the enhanced setting.
- **Limitations:** Tool responses are simulated and single-turn, so it does not test multi-step stateful exploitation (assessment). AgentDojo (entry 15) later moved to dynamic environments (assessment).
- **Code availability:** https://github.com/uiuc-kang-lab/InjecAgent (linked in abstract)
- **Unresolved research gaps:** Multi-turn and adaptive IPI. Joint measurement of defense cost and utility.

### 17. Agent-SafetyBench
- **Title:** Agent-SafetyBench: Evaluating the Safety of LLM Agents
- **Authors:** Zhexin Zhang, Shiyao Cui, Yida Lu, et al.
- **Venue:** arXiv preprint. OpenReview also lists it as an AAAI 2026 TrustAgent *workshop* poster. No main-conference acceptance was found.
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2412.14470
- **Core contribution:** A broad safety benchmark covering 8 risk categories and 10 failure modes across hundreds of interaction environments. It finds that no tested agent exceeds a 60% safety score.
- **Methodology:** 349 environments and 2,000 test cases. Interaction records are labelled safe or unsafe by a fine-tuned Qwen-2.5-7B scorer trained on 4,000 manually labelled records (91.5% accuracy on a held-out check vs. 75.5% for GPT-4o). Helpfulness is judged separately.
- **Datasets/benchmarks:** Agent-SafetyBench, introduced here.
- **Evaluation metrics:** Safety score (% safe), broken down by category and failure mode. Helpfulness rate.
- **Limitations:** Most cases need only commonsense, and "advanced domain-specific knowledge is left for future work" (stated). Many auto-generated cases needed substantial revision (stated). The AI tools used in construction and scoring could introduce bias (stated, partly checked). The scorer is a learned model, so safety scores inherit its errors (assessment).
- **Code availability:** https://github.com/thu-coai/Agent-SafetyBench/ (linked in abstract)
- **Unresolved research gaps:** Domain-expert risk scenarios. Validating safety scorers under distribution shift.

---

## D. Trajectory-level judging and process verification

### 18. Agent-as-a-Judge
- **Title:** Agent-as-a-Judge: Evaluate Agents with Agents
- **Authors:** Mingchen Zhuge, Changsheng Zhao, Dylan Ashley, et al.
- **Venue:** ICML 2025 (OpenReview: ICML 2025 poster)
- **Year:** 2025 (arXiv 2024)
- **Link:** https://arxiv.org/abs/2410.10934
- **Core contribution:** Uses an *agentic* judge, one that can navigate a workspace, read files and retrieve trajectory segments, to give requirement-level intermediate feedback on agent outputs. It aligns with human consensus better than LLM-as-a-Judge.
- **Methodology:** Judge modules: graph, locate, read, search, retrieve, ask, memory, planning. The best subset is graph, locate, read, retrieve, ask. Black-box (outputs only) and gray-box (with trajectories) settings are compared with a 3-human panel.
- **Datasets/benchmarks:** DevAI, 55 AI-development tasks with 365 hierarchical requirements, introduced here. Systems judged: MetaGPT, GPT-Pilot, OpenHands.
- **Evaluation metrics:** Alignment rate with human majority vote. Agent-as-a-Judge: about 84–92%. LLM-as-a-Judge: about 60–84%. Humans vs. majority: about 76–93%.
- **Limitations:** The memory module propagated errors (stated). Planning was unstable, and a perfect judge is "not the focus of this proof of concept" (stated). Gray-box trajectories are "nearly inaccessible in practical situations" (stated). Human evaluators disagree 10–30% of the time (stated). One domain (code generation) and small workspaces (assessment).
- **Code availability:** https://github.com/metauto-ai/agent-as-a-judge. Data at https://huggingface.co/DEVAI-benchmark (linked in arXiv comment).
- **Unresolved research gaps:** Judge robustness to adversarial or reward-hacking agents. Calibration of judges. Domains beyond code.

### 19. AgentPRM
- **Title:** AgentPRM: Process Reward Models for LLM Agents via Step-Wise Promise and Progress
- **Authors:** Zhiheng Xi, Chenyang Liao, Guanyu Li, et al.
- **Venue:** arXiv preprint. An earlier version appears as an ACL ARR Feb 2025 submission on OpenReview, with no acceptance found.
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2511.08325
- **Core contribution:** Redefines process rewards for agent tasks. Steps have no clear correctness, so each step is scored by its *promise* (proximity to the goal) and *progress* (contribution relative to prior steps). Labels are estimated with TD learning plus GAE for sample efficiency.
- **Methodology:** Train PRMs on TD/GAE-estimated step labels. Use them for Best-of-N and step-level beam search at test time. Explore use in agent RL.
- **Datasets/benchmarks:** WebShop, BabyAI, TextCraft (plus GSM8K for transfer). Policies: Qwen2.5 0.5B/3B/7B-Instruct and Llama-3.1-8B-Instruct.
- **Evaluation metrics:** Success rate or reward under Best-of-N and beam search. Compute efficiency: over 8× more efficient than baselines.
- **Limitations:** RL integration and coding or logic tasks are left to future work (stated). Text-game and web-shopping environments with dense, automatically computable outcomes. Transfer to open-ended, long-horizon or real-world agents is untested (assessment). Small policy models only (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:** PRMs for sparse-reward, long-horizon, real-tool environments. PRM robustness to reward hacking. Whether PRMs can drive abstention or rollback decisions.

---

## E. Agent and tool-call hallucination

### 20. MIRAGE-Bench
- **Title:** MIRAGE-Bench: LLM Agent is Hallucinating and Where to Find Them
- **Authors:** Weichen Zhang, Yiyou Sun, Pohao Huang, Jiayue Pu, Heyue Lin, Dawn Song
- **Venue:** arXiv preprint. OpenReview lists it as an ICLR 2026 *rejected* submission.
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2507.21017
- **Core contribution:** A unified benchmark for *agentic* hallucination, meaning actions unfaithful to (i) task instructions, (ii) execution history, or (iii) environment observations.
- **Methodology:** Audits existing agent benchmarks for hallucination-prone settings. Freezes decision points as deterministic "snapshots". Six risk settings: out-of-scope queries, unexpected transitions, unachievable goals, ill-specified instructions, flawed history, pop-up distractions. Scored by an LLM judge with risk-aware prompts.
- **Datasets/benchmarks:** Snapshots built from WebArena, TheAgentCompany, SWE-bench, OSWorld, WorkArena and τ-bench. Twelve to thirteen open and proprietary models evaluated.
- **Evaluation metrics:** Utility score (faithful = 1, incomplete = 0.5, hallucinated = 0) and hallucination rate.
- **Limitations:** The static snapshot evaluation calls for future "dynamic, rollout-based assessments" (stated). Some proactive actions "cannot be executed or observed" (stated). Pop-ups are text-only (stated). Embodied and multimodal settings are out of scope (stated). Hallucination labels rely on an LLM judge (assessment).
- **Code availability:** https://github.com/sunblaze-ucb/mirage-bench.git (linked in arXiv comment)
- **Unresolved research gaps:** Detecting hallucinated actions during rollouts and their downstream cost. Mitigation that does not reduce task completion.

### 21. The Reasoning Trap
- **Title:** The Reasoning Trap: How Enhancing LLM Reasoning Amplifies Tool Hallucination
- **Authors:** Chenlong Yin, Zeyang Sha, Shiwen Cui, Changhua Meng, Zechao Li
- **Venue:** ACL 2026 Main (arXiv comment: "Accepted to ACL 2026 Main")
- **Year:** 2026 (arXiv 2025)
- **Link:** https://arxiv.org/abs/2510.22977
- **Core contribution:** Controlled evidence that reasoning enhancement increases tool hallucination roughly in proportion to task gains, whether reasoning comes from RL, SFT, or inference-time CoT. Also found when RL is on non-tool tasks such as math.
- **Methodology:** SimpleToolHalluBench (296 tools × 2 settings: no tool available, distractor tools only). GRPO training of Qwen2.5-7B-Instruct on tool data (ReCall/SynTool) and on GSM8K. Mitigations tested: prompting and DPO. Mechanistic analysis of representations and late-layer residual streams.
- **Datasets/benchmarks:** SimpleToolHalluBench, introduced here.
- **Evaluation metrics:** Hallucination rates R_NTA and R_DT, judged by an LLM (DeepSeek-R1) and spot-checked by humans. Task utility.
- **Limitations:** "Focuses on single-step tool invocation" (stated). "Does not yet provide a complete causal account" (stated). Mitigations "limited to prompt engineering and DPO" (stated). Mitigations show a reliability–capability trade-off (stated, as a finding).
- **Code availability:** https://github.com/albert-y1n/Reasoning_Trap (linked in paper)
- **Unresolved research gaps:** Training objectives that jointly optimise capability and tool reliability. Multi-step tool hallucination. Abstention when no suitable tool exists.

---

## F. Uncertainty estimation for agents

### 22. SAUP
- **Title:** Uncertainty Propagation on LLM Agent. The ACL Anthology title is used here. The arXiv title is "SAUP: Situation Awareness Uncertainty Propagation on LLM Agent".
- **Authors:** ACL version: Qiwei Zhao, Dong Li, Yanchi Liu, et al. The arXiv v1 author list differs slightly (e.g., Xujiang Zhao is second author there).
- **Venue:** ACL 2025 (Long Papers), pp. 6064–6073 (ACL Anthology 2025.acl-long.302)
- **Year:** 2025 (arXiv 2024)
- **Link:** https://aclanthology.org/2025.acl-long.302/ (arXiv: https://arxiv.org/abs/2412.01033)
- **Core contribution:** Propagates per-step uncertainty through a multi-step agent trajectory with *situational weights*, instead of estimating uncertainty only at the final step.
- **Methodology:** ReAct agents. Step uncertainty is normalised entropy. Weights come from surrogate distances (question-to-trajectory and observation-to-thought/action, via a RoBERTa-SQuAD2 scorer) or from a 3-state HMM trained with Baum–Welch. Steps are aggregated by weighted RMS.
- **Datasets/benchmarks:** HotpotQA, StrategyQA, MMLU. LLaMA3 8B/70B and GPT-4o.
- **Evaluation metrics:** AUROC for separating correct from incorrect outcomes. Up to 20% improvement.
- **Limitations:** The learned variant "relies on manually annotated datasets" (stated). Errors in single-step estimates "can compromise the propagation" (stated). Evaluated on QA-style tasks wrapped in ReAct, not on tool-heavy or environment-changing tasks (assessment). AUROC does not show whether the uncertainty triggers useful actions such as asking for help (assessment).
- **Code availability:** not verified (none linked on the ACL Anthology page or arXiv HTML)
- **Unresolved research gaps:** Uncertainty-triggered abstention, clarification or escalation, evaluated on real agent benchmarks. Calibration under environment stochasticity.

---

## G. Failure analysis, attribution, and recovery

### 23. MAST
- **Title:** Why Do Multi-Agent LLM Systems Fail?
- **Authors:** Mert Cemri, Melissa Z. Pan, Shuyi Yang, et al.
- **Venue:** NeurIPS 2025 Datasets and Benchmarks Track (OpenReview: spotlight)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2503.13657
- **Core contribution:** An empirically grounded taxonomy of failures in multi-agent systems (MAST): 14 modes in 3 categories (system design, inter-agent misalignment, task verification). Released with 1,600+ annotated traces and an LLM annotator.
- **Methodology:** Grounded-theory analysis of 150 traces (human κ = 0.88), then scaled with an LLM-as-judge annotator (o1, few-shot; κ = 0.77 vs. experts; 0.79 out of domain). Case-study interventions on ChatDev, such as role clarification and a task-objective verification step, gave up to +15.6%.
- **Datasets/benchmarks:** MAST-Data, from 7 frameworks: MetaGPT, ChatDev, HyperAgent, AppWorld, AG2/MathChat, Magentic-One, OpenManus.
- **Evaluation metrics:** Failure-mode frequencies, inter-annotator agreement, task-success change after intervention.
- **Limitations:** "We do not claim MAST is exhaustive" (stated). Interventions leave "task completion rates still… low" (stated). Closed systems were excluded for lack of traces (stated). Agreement is reported as κ, but the judge is not tested against adversarial or ambiguous traces (assessment).
- **Code availability:** https://github.com/multi-agent-systems-failure-taxonomy/MAST. Data at https://huggingface.co/datasets/mcemri/MAST-Data (linked in paper).
- **Unresolved research gaps:** Linking failure modes to automatic repair. Single-agent analogues. A causal rather than descriptive taxonomy.

### 24. Who&When (automated failure attribution)
- **Title:** Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems
- **Authors:** Shaokun Zhang, Ming Yin, Jieyu Zhang, et al.
- **Venue:** ICML 2025 (OpenReview: spotlight poster)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2505.00212
- **Core contribution:** Defines *automated failure attribution*, identifying the responsible agent and the decisive error step, as a research problem. Introduces the Who&When dataset.
- **Methodology:** Failure logs from 127 multi-agent systems: algorithm-generated CaptainAgent systems and hand-crafted Magentic-One on GAIA and AssistantBench. Experts annotated the agent, step and rationale. Three LLM attribution strategies were compared: all-at-once, step-by-step, binary search.
- **Datasets/benchmarks:** Who&When (184 annotated failure tasks), introduced here.
- **Evaluation metrics:** Agent-level accuracy (best 53.5%). Step-level accuracy (best 14.2%; 8.77% on hand-crafted systems). Step accuracy with tolerance.
- **Limitations:** Step-level attribution is very poor, and "stronger reasoning models do not necessarily outperform standard models" (stated). Accuracy degrades with log length (stated). Ground truth assumes one decisive step even when failures may have several causes (assessment).
- **Code availability:** https://github.com/mingyin1/Agents_Failure_Attribution (linked in abstract)
- **Unresolved research gaps:** Counterfactual or replay-based attribution, for example re-running from a checkpoint with the step corrected. Attribution for single agents with long tool traces.

### 25. GA-Rollback
- **Title:** Generator-Assistant Stepwise Rollback Framework for Large Language Model Agent
- **Authors:** Xingzuo Li, Kehai Chen, Yunfei Long, Xuefeng Bai, Yong Xu, Min Zhang
- **Venue:** EMNLP 2025 Main (arXiv comment: "EMNLP 2025 Main")
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2503.02519
- **Core contribution:** Targets the "one-pass" problem, where every generated thought or action is committed regardless of correctness. An assistant model checks each generator action and triggers a rollback when it finds an error.
- **Methodology:** A generator–assistant loop with stepwise rollback. Two add-ons: probability-based feedback filtering (feedback with low mean token probability is discarded) and Wait-Info (the assistant intervenes only after a set number of actions).
- **Datasets/benchmarks:** Game of 24, ALFWorld, WebShop. LLaMA-3.1-8B, GLM4-9B, Qwen2.5 (3B–32B), GPT-4o on WebShop.
- **Evaluation metrics:** Success rate, WebShop reward, token and runtime overhead.
- **Limitations:** "Certain environments may not support full rollback to previous states" (stated). Not optimal on ALFWorld (stated). Thresholds need empirical tuning (stated). Rollback here is rollback of the agent's trajectory in simulators; it does not undo real external side effects (assessment; see ACRFence and DART in supplementary).
- **Code availability:** https://github.com/wisper12933/GA-Rollback (linked in paper)
- **Unresolved research gaps:** Rollback when external effects are irreversible. Calibrating the assistant verifier. Interaction between rollback and safety evaluation.

---

## Supplementary verified works (brief)

The fields are condensed because each item is foundational, adjacent, or too thin for a full entry. Every item was confirmed on arXiv or a venue page.

| Work | Authors | Venue (confirmed) | Link | Relevance |
|---|---|---|---|---|
| VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks | Jing Yu Koh, Robert Lo, Lawrence Jang, et al. | ACL 2024 (arXiv comment) | https://arxiv.org/abs/2401.13649 | Multimodal extension of WebArena. Project page https://jykoh.com/vwa |
| R-Judge: Benchmarking Safety Risk Awareness for LLM Agents | Tongxin Yuan, Zhiwei He, Lingzhong Dong, et al. | Findings of EMNLP 2024 (arXiv comment) | https://arxiv.org/abs/2401.10019 | Tests whether LLMs can *judge* risk in agent interaction records, i.e. LLM-as-safety-monitor |
| Training Software Engineering Agents and Verifiers with SWE-Gym | Jiayi Pan, Xingyao Wang, Graham Neubig, et al. | ICML 2025 (arXiv comment) | https://arxiv.org/abs/2412.21139 | Trains outcome verifiers for inference-time scaling of SWE agents. Code https://github.com/SWE-Gym/SWE-Gym |
| Process Reward Models for LLM Agents: Practical Framework and Directions | Sanjiban Choudhury | arXiv preprint | https://arxiv.org/abs/2502.10325 | Single-author framework for agent PRMs, a precursor to entry 19 |
| ToolBeHonest: A Multi-level Hallucination Diagnostic Benchmark for Tool-Augmented LLMs | Yuxiang Zhang, Jing Chen, Junjie Wang, et al. | EMNLP 2024 Main (ACL Anthology 2024.emnlp-main.637) | https://arxiv.org/abs/2406.20015 | Tool hallucination under missing, potential or limited tools. Most errors trace to judging solvability |
| AgentHallu: Benchmarking Automated Hallucination Attribution of LLM-based Agents | Xuannan Liu, Xiao Yang, Zekun Li, Peipei Li, Ran He | arXiv preprint (2026) | https://arxiv.org/abs/2601.06818 | Step-level attribution of agent hallucinations |
| Position: Uncertainty Quantification Needs Reassessment for Large-language Model Agents | Michael Kirchhof, Gjergji Kasneci, Enkelejda Kasneci | ICML 2025 position track (arXiv comment: "Accepted at ICML 2025") | https://arxiv.org/abs/2505.22655 | Argues the aleatoric/epistemic split breaks down for interactive agents |
| UProp: Investigating the Uncertainty Propagation of LLMs in Multi-Step Agentic Decision-Making | Jinhao Duan, James Diffenderfer, Sandeep Madireddy, et al. | arXiv preprint | https://arxiv.org/abs/2506.17419 | Information-theoretic intrinsic/extrinsic decomposition of step uncertainty |
| Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners (KnowNo) | Allen Z. Ren, Anushri Dixit, Alexandra Bodrova, et al. | CoRL 2023, oral (arXiv comment) | https://arxiv.org/abs/2307.01928 | Conformal prediction to decide when an LLM planner should ask for help. The main statistically grounded "ask for help" result, though in robotics |
| ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore | Yusheng Zheng, Yiwei Yang, Wei Zhang, Andi Quinn | arXiv; journal-ref "CoDAIM workshop 2026" (workshop) | https://arxiv.org/abs/2603.20625 | Restoring an agent checkpoint can replay irreversible external effects. Proposes tool-boundary effect logging |
| DART: Semantic Recoverability for Structured Tool Agents | Ke Yang, Panpan Li, Zonghan Wu, et al. | arXiv preprint (2026) | https://arxiv.org/abs/2605.23311 | Admissible rollback that respects committed downstream effects |
| AgentOps: Enabling Observability of LLM Agents | Liming Dong, Qinghua Lu, Liming Zhu | arXiv preprint | https://arxiv.org/abs/2411.05285 | Taxonomy of traceable artefacts for agent observability. Conceptual, with no empirical evaluation (assessment) |
| A Survey on AgentOps: Categorization, Challenges, and Future Directions | Zexin Wang, Jingjing Li, Quan Zhou, et al. | arXiv preprint | https://arxiv.org/abs/2508.02121 | Survey of agent operations: monitoring, anomaly detection, root-cause analysis |
| AgentSight: System-Level Observability for AI Agents Using eBPF | Yusheng Zheng, Yanpeng Hu, Tong Yu, Andi Quinn | arXiv; journal-ref "PACMI'2025" (workshop) | https://arxiv.org/abs/2508.02736 | "Boundary tracing": correlates intercepted LLM traffic with kernel events |
| Chain-of-Verification Reduces Hallucination in Large Language Models | Shehzaad Dhuliawala, Mojtaba Komeili, Jing Xu, et al. | Findings of ACL 2024 (ACL Anthology 2024.findings-acl.212) | https://arxiv.org/abs/2309.11495 | Draft → plan verification questions → answer them independently → revise. A foundation for self-verification |
| SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative LLMs | Potsawee Manakul, Adian Liusie, Mark J. F. Gales | EMNLP 2023 Main (arXiv comment) | https://arxiv.org/abs/2303.08896 | Sampling-consistency hallucination detection. A foundation for black-box agent self-checks |
| Survey on Evaluation of LLM-based Agents | Asaf Yehudai, Lilach Eden, Alan Li, et al. | arXiv comment says "ACL Findings". The year and proceedings entry were not verified. | https://arxiv.org/abs/2503.16416 | Broad survey of agent evaluation, useful for positioning |

---

## Recurring weaknesses in this slice *(my assessment)*

1. **Single-run success is still the default metric.** Most benchmarks report one-shot success with no variance, confidence intervals or repeated-trial reliability (AgentBench, WebArena, GAIA, OSWorld, SWE-bench, TheAgentCompany). τ-bench's pass^k (entry 5) is the main exception, and HAL (entry 11) still reports mostly accuracy and cost rather than consistency.
2. **The grading code is itself unreliable.** Outcome checks often accept wrong or empty answers or miss incorrect patches: substring matching in WebArena and τ-bench, insufficient tests in SWE-bench, null-action passes in τ-bench. ABC (entry 12) quantifies errors of up to 100% relative, and HAL found leakage in a scaffold. Few benchmarks publish a validity audit at release.
3. **Contamination and shortcuts are acknowledged but rarely measured causally.** The evidence is correlational (SWE-Bench Illusion, entry 13) or anecdotal (HAL's "searching HuggingFace for the benchmark"). Static public splits (GAIA, SWE-bench, WebArena) remain the norm despite the holdout prescriptions of entry 10.
4. **The evaluation chain is LLM-judged at every level.** Simulated users (τ-bench, τ²-bench, TheAgentCompany), emulated tools (ToolEmu), safety scorers (Agent-SafetyBench, R-Judge), hallucination judges (MIRAGE-Bench, Reasoning Trap), failure annotators (MAST, HAL) and trajectory judges (Agent-as-a-Judge) are all LLMs. Judge validation is usually a small human-agreement study, with no adversarial or out-of-distribution stress test.
5. **Process and verifier methods are tested on toy, dense-reward environments.** AgentPRM (WebShop, BabyAI, TextCraft), GA-Rollback (Game of 24, ALFWorld, WebShop) and SAUP (QA under ReAct) are not evaluated on the realistic benchmarks in Section A, so it is unclear whether they transfer.
6. **Recovery work assumes the world can be reset.** Rollback papers roll back the agent's trajectory in resettable simulators (GA-Rollback). The irreversible external side effects that matter in deployment are addressed only by thin 2026 workshop or preprint work (ACRFence, DART).
7. **Uncertainty work stops at AUROC.** Agent UQ (SAUP, UProp) measures how well uncertainty separates successes from failures. It does not close the loop to decisions such as abstaining, asking, or escalating, or measure their utility cost. The ICML 2025 position paper argues the current UQ framing does not fit interactive agents.
8. **Reliability trades off against capability, and benchmarks reward capability.** The Reasoning Trap (entry 21) shows reasoning gains raise tool hallucination, and AgentDojo shows defenses cut utility. Yet leaderboards (HAL, SWE-bench, OSWorld) rank by task success, with no joint reliability–capability score.

## Open problems that a small team could attack *(my assessment)*

1. **A reliability addendum for existing benchmarks.** Re-run a few cheap, existing suites (τ-bench subsets, SWE-bench Verified Mini, WebArena-lite) with *k* trials and perturbed prompts. Report pass^k, variance and confidence intervals alongside cost. Show how leaderboard rankings change. Needs compute, not new infrastructure. Builds on entries 5, 10, 11 and 12.
2. **Null-agent and adversarial-agent audits as a release gate.** Package ABC-style shortcut probes as a reusable harness: a do-nothing agent, a database-dump agent, a test-file-overwrite agent, and an agent that searches for the benchmark answer online. Run it against many open benchmarks. Validating outcomes automatically would directly address weakness 2.
3. **Uncertainty-to-action evaluation.** Take an agent UQ signal (SAUP-style propagation, verbalised confidence, or a PRM score from entry 19). Use it to trigger abstain or ask-user actions inside τ²-bench or a MIRAGE-Bench setting. Measure the risk–coverage trade-off, i.e. success vs. intervention rate. The evaluation protocol is itself a contribution.
4. **Stress-testing LLM judges for agents.** Build a small adversarial set of agent trajectories, for example ones that claim success falsely, have plausible but wrong final states, or contain prompt-injected logs. Measure how Agent-as-a-Judge, MAST's annotator and safety scorers fail. Cheap, high-leverage, and addresses weakness 4.
5. **Effect-aware checkpoint and rollback for tool agents on real benchmarks.** Combine tool-boundary effect logging (ACRFence or DART ideas) with a verifier-triggered rollback (GA-Rollback). Evaluate on AgentDojo or TheAgentCompany tasks that have side effects. Report success, duplicated or irreversible effects, and overhead.
6. **Replay-based failure attribution.** Who&When step attribution is about 14% accurate. Test counterfactual replay instead: re-run from the checkpoint before a candidate step with that step corrected. Compare it with LLM-reading attribution on Who&When and MAST-Data traces.

## Seeds dropped or downgraded

- **SWE-bench Verified:** an OpenAI blog/dataset release (2024), not a peer-reviewed or arXiv paper. It is covered in entries 3, 12 and 13 but not cited as a paper.
- **"Agent hallucination survey":** I could not confirm a dedicated agent-hallucination survey on a primary page, so none was included. MIRAGE-Bench, ToolBeHonest, AgentHallu and Reasoning Trap cover the topic instead.
- **Observability and tracing:** no peer-reviewed main-venue paper found. Only preprints and workshop papers (AgentOps, AgentOps survey, AgentSight) are listed, as a noted gap.

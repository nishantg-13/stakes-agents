# 04 — Planning, Reflection/Self-Correction, and Tool Use in LLM Agents

*Slice compiled 2026-11-08. Every entry below was checked against a primary source page (arxiv.org/abs, an arXiv HTML/ar5iv render of the paper, proceedings.neurips.cc, proceedings.iclr.cc / iclr.cc, or the PMLR/TACL journal reference on the arXiv record). Venues are given only where acceptance was confirmed. Otherwise the entry says "arXiv preprint". "not verified" marks fields that could not be confirmed.*

## Scope

This slice covers three linked capabilities of LLM agents. (1) **Planning**: interleaving reasoning with actions, tree/graph search over thoughts or actions, adaptive decomposition, and the critique that LLMs cannot plan autonomously. (2) **Reflection and self-correction**: verbal self-feedback, tool-grounded critique, the negative results on intrinsic self-correction, and RL-trained self-correction. (3) **Tool use**: self-supervised and fine-tuned API calling, large tool corpora, tool-use evaluation, MCP-era tool integration, and 2025-era agentic RL with search engines and code interpreters, including test-time interaction scaling. Multi-agent coordination, memory systems, and benchmarks as such belong to other slices. Benchmarks appear here only when the paper is mainly about tool use or planning (API-Bank, PlanBench).

Background works were verified but not given full entries, to keep the list within budget:
- Chain-of-Thought prompting (Wei et al., NeurIPS 2022; https://arxiv.org/abs/2201.11903) is the reasoning baseline nearly every paper below builds on.
- Plan-and-Solve prompting (Wang et al., ACL 2023 per arXiv comments; https://arxiv.org/abs/2305.04091) is a zero-shot "plan first, then execute" prompt. ADaPT (entry 5) is the more agentic successor.
- Voyager (Wang et al., TMLR 2024 per the mlanthology/UT-RPL listing; https://arxiv.org/abs/2305.16291) is a Minecraft agent with a code skill library and self-verification. Memory/skill-library aspects belong to the memory slice.

Entries are grouped: **A. Reasoning-acting and search-based planning** (1–5); **B. The planning critique** (6–8); **C. Reflection and self-correction** (9–14); **D. Tool learning** (15–20); **E. Agentic RL and test-time scaling for tool use** (21–24).

---

## A. Reasoning-acting and search-based planning

### 1. ReAct

- **Title:** ReAct: Synergizing Reasoning and Acting in Language Models
- **Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, et al.
- **Venue:** ICLR 2023 (arXiv v3 comment: "ICLR camera ready version")
- **Year:** 2023 (arXiv v1 Oct 2022)
- **Link:** https://arxiv.org/abs/2210.03629
- **Core contribution:** Prompts an LLM to interleave free-form reasoning traces ("thoughts") with environment actions, so that reasoning guides action selection and observations ground reasoning.
- **Methodology:** Few-shot prompting of frozen PaLM-540B with Thought/Action/Observation trajectories. Additional GPT-3 (text-davinci-002) prompting runs. Fine-tuning of PaLM-8B/62B on about 3,000 successful ReAct trajectories. Compared against CoT, Act-only, and imitation/RL baselines, plus CoT-SC↔ReAct fallback hybrids.
- **Datasets/benchmarks:** HotpotQA and FEVER (with a Wikipedia API); ALFWorld; WebShop.
- **Evaluation metrics:** Exact match (HotpotQA), accuracy (FEVER), success rate (ALFWorld, WebShop), WebShop score.
- **Limitations:**
  - (stated) Large action spaces need more demonstrations than fit in context.
  - (stated) Prompted ReAct is weak with small models.
  - (stated) ReAct makes more reasoning errors than CoT on HotpotQA failure cases (47% vs 16%). Uninformative search results cause 23% of errors.
  - (stated) ReAct gets stuck in repetitive thought/action loops.
  - (assessment) It has no mechanism to recover from earlier mistakes within an episode. Later reflection and search work (Reflexion, LATS) exists largely to patch this.
- **Code availability:** https://react-lm.github.io (project site with code, linked in the arXiv comments)
- **Unresolved research gaps:** When should an agent think versus act? (revisited by entry 24.) The format is hand-designed; it is not established whether learned interleavings beat it on long horizons.

### 2. Tree of Thoughts (ToT)

- **Title:** Tree of Thoughts: Deliberate Problem Solving with Large Language Models
- **Authors:** Shunyu Yao, Dian Yu, Jeffrey Zhao, et al.
- **Venue:** NeurIPS 2023 (arXiv comment: "NeurIPS 2023 camera ready version")
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2305.10601
- **Core contribution:** Generalizes CoT into search over a tree of intermediate "thoughts", using the LM itself to propose and evaluate them. This allows lookahead and backtracking.
- **Methodology:** The LM is the thought generator and also the state evaluator, either scoring states ("sure/maybe/impossible", 1–10) or voting among them. Search uses BFS (beam b=5 for Game of 24) or DFS with pruning (Mini Crosswords). GPT-4 is the main model.
- **Datasets/benchmarks:** Game of 24, Creative Writing, Mini Crosswords (all new task setups).
- **Evaluation metrics:** Success rate (Game of 24: 74% for ToT vs 4% for CoT); GPT-4 coherence score and human preference (writing); letter, word, and game success rates (crosswords).
- **Limitations:**
  - (stated) It generates 5–100× more tokens than CoT.
  - (stated) Gains are small on tasks GPT-4 already does well (GSM8K, StrategyQA).
  - (stated) Only three relatively simple tasks were studied.
  - (stated) Weaker models (GPT-3.5: 19% on Game of 24) are bottlenecked by thought generation.
  - (assessment) The LM-as-evaluator heuristic is uncalibrated and task-specific prompts are hand-written. Entries 7, 8, and 13 later show that LM self-evaluation is unreliable.
- **Code availability:** https://github.com/princeton-nlp/tree-of-thought-llm
- **Unresolved research gaps:** Compute-optimal allocation between breadth, depth, and evaluation; learned rather than prompted value functions; the extension from puzzles to stateful environments where actions cannot be undone.

### 3. RAP (Reasoning via Planning)

- **Title:** Reasoning with Language Model is Planning with World Model
- **Authors:** Shibo Hao, Yi Gu, Haodi Ma, et al.
- **Venue:** EMNLP 2023 (arXiv comment: "EMNLP 2023")
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2305.14992
- **Core contribution:** Uses the same LLM as a world model that predicts next states and as a reasoning agent, with Monte Carlo Tree Search over reasoning steps guided by task-specific rewards.
- **Methodology:** MCTS with LLM-predicted state transitions and rewards (action likelihood, self-evaluation, task heuristics). The default base model is LLaMA-33B; Llama-2-70B is used for the full Blocksworld runs; GPT-4 CoT serves as a comparison.
- **Datasets/benchmarks:** Blocksworld plan generation (2/4/6-step subsets, plus the full 602 cases); GSM8K; PrOntoQA.
- **Evaluation metrics:** Plan success rate; answer accuracy; PrOntoQA prediction and proof accuracy.
- **Limitations:**
  - (stated) It uses frozen LLMs, so it is capped by pre-training.
  - (stated) Fine-tuning LLMs as world models and adding tools are left as future work.
  - (assessment) Blocksworld success depends on the LLM's imperfect simulation of state. The paper does not test obfuscated domains, where entries 6 and 8 report collapse.
  - (assessment) MCTS cost is large relative to CoT.
- **Code availability:** https://github.com/Ber666/llm-reasoners (linked in arXiv comments)
- **Unresolved research gaps:** How faithful are LLM world models, and how do their errors compound in rollouts? Training world models jointly with policies; using verifiers instead of self-reward.

### 4. LATS (Language Agent Tree Search)

- **Title:** Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models (PMLR title; the arXiv title omits the commas)
- **Authors:** Andy Zhou, Kai Yan, Michal Shlapentokh-Rothman, Haohan Wang, Yu-Xiong Wang
- **Venue:** ICML 2024 (Proceedings of the 41st ICML, PMLR 235:62138–62160; confirmed on proceedings.mlr.press)
- **Year:** 2024 (arXiv v1 Oct 2023)
- **Link:** https://arxiv.org/abs/2310.04406 ; https://proceedings.mlr.press/v235/zhou24r.html
- **Core contribution:** Unifies ReAct-style acting, ToT/RAP-style search, and Reflexion-style self-reflection in a single MCTS framework over agent trajectories, using real environment feedback.
- **Methodology:** MCTS in which the LM proposes actions, an LM-powered value function combines a self-generated score with self-consistency, and reflections on failed trajectories are added to context. Mostly GPT-3.5; GPT-4 for HumanEval.
- **Datasets/benchmarks:** HotpotQA (100 questions); HumanEval (164) and MBPP (397-problem subset); WebShop (50 instructions); Game of 24 (50).
- **Evaluation metrics:** EM; pass@1 (HumanEval 92.7% with GPT-4); WebShop score (75.9 with GPT-3.5) and success rate; success rate.
- **Limitations:**
  - (stated) It costs more than ReAct or Reflexion.
  - (stated) It assumes the environment can be reverted to earlier states, which many real environments do not allow.
  - (stated) The benchmarks are simpler than real-world environments.
  - (assessment) Small evaluation subsets (50–100 items) give wide confidence intervals.
  - (assessment) The compute-matched comparison against sampling baselines is limited.
- **Code availability:** https://github.com/lapisrocks/LanguageAgentTreeSearch
- **Unresolved research gaps:** Search when environments are irreversible (needs simulators or learned world models); cost-aware search; whether search gains survive against compute-matched best-of-n.

### 5. ADaPT

- **Title:** ADaPT: As-Needed Decomposition and Planning with Language Models
- **Authors:** Archiki Prasad, Alexander Koller, Mareike Hartmann, et al.
- **Venue:** Findings of NAACL 2024 (arXiv comment: "NAACL 2024 (findings) camera-ready")
- **Year:** 2024 (arXiv v1 Nov 2023)
- **Link:** https://arxiv.org/abs/2311.05772
- **Core contribution:** Recursively decomposes a task only when the executor LLM fails a sub-task, so decomposition depth adapts to both task complexity and executor capability.
- **Methodology:** An executor LLM attempts a task and self-reports success or failure. On failure, a planner LLM decomposes the task (with AND/OR logic) and recurses. Mostly GPT-3.5 variants, plus GPT-4, LLaMA-2-70B, and Lemur-70B, including mixed planner/executor pairs.
- **Datasets/benchmarks:** ALFWorld, WebShop, and TextCraft (new, Minecraft-inspired crafting).
- **Evaluation metrics:** Success rate (gains of up to +28.3% ALFWorld, +27% WebShop, +33% TextCraft over baselines); number of LLM calls; decomposition depth.
- **Limitations:**
  - (stated) It relies on the executor's own success judgment. On WebShop this overestimates success by more than 30 points and ends decomposition too early.
  - (stated) There is a single run per LLM because of cost.
  - (stated) Extending it to non-decision tasks needs better self-evaluation.
  - (assessment) It inherits the self-verification problem documented in entries 8, 12, and 13.
- **Code availability:** Project page https://allenai.github.io/adaptllm (code repository not verified)
- **Unresolved research gaps:** Calibrated or external success detectors to trigger decomposition; learning when to decompose; decomposition in open-ended or partially observable settings.

---

## B. The planning critique

### 6. PlanBench

- **Title:** PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change
- **Authors:** Karthik Valmeekam, Matthew Marquez, Alberto Olmo, Sarath Sreedharan, Subbarao Kambhampati
- **Venue:** NeurIPS 2023 Track on Datasets and Benchmarks (arXiv comment)
- **Year:** 2023 (arXiv v1 June 2022)
- **Link:** https://arxiv.org/abs/2206.10498
- **Core contribution:** A planning benchmark built from International Planning Competition domains with mechanically validated outputs. It separates real planning from retrieval of common-sense knowledge, including through name-obfuscated "Mystery" domains.
- **Methodology:** About 26k prompts covering 8 test cases: plan generation, cost-optimal planning, plan verification, reasoning about plan execution, goal reformulation, plan reuse, replanning, and plan generalization. Problems come from the Fast Downward planner and outputs are checked with the VAL validator. One-shot prompting at temperature 0.
- **Datasets/benchmarks:** Blocksworld (600 instances), Logistics (285), and Mystery Blocksworld (deceptive and randomized obfuscations).
- **Evaluation metrics:** Binary per-instance correctness via VAL. GPT-4 Blocksworld plan generation: 34.3%. Mystery Blocksworld: 4.3%.
- **Limitations:**
  - (stated) The main evaluation covers Blocksworld only and two IPC domains overall.
  - (stated) It uses one-shot prompts and binary metrics with no partial credit.
  - (stated) Only two models were evaluated.
  - (assessment) Classical STRIPS domains are far from the open-world, partially specified planning that deployed agents face. Results for 2024–2026 reasoning models are not in this paper.
- **Code availability:** not verified
- **Unresolved research gaps:** Re-evaluation with long-reasoning models; partial-credit and plan-quality metrics; bridging PDDL-style benchmarks and natural-language agent planning.

### 7. LLM-Modulo frameworks

- **Title:** LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks
- **Authors:** Subbarao Kambhampati, Karthik Valmeekam, Lin Guan, et al.
- **Venue:** ICML 2024 (arXiv journal-ref: Proceedings of the 41st ICML, PMLR 235). The abstract describes it as a position paper.
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2402.01817
- **Core contribution:** Argues that autoregressive LLMs cannot plan or self-verify on their own. Proposes "LLM-Modulo" architectures in which LLMs generate candidates and help acquire domain models, while external model-based critics or verifiers guarantee soundness through a bidirectional generate–test loop.
- **Methodology:** Position and argument, with a conceptual architecture: LLM generator, bank of hard and soft critics, meta-controller, and back-prompting. The abstract presents no new experimental study.
- **Datasets/benchmarks:** None as primary contribution (draws on the authors' prior PlanBench and self-critique results).
- **Evaluation metrics:** N/A
- **Limitations:**
  - (assessment) It needs sound verifiers, which exist for PDDL, code tests, and constraint checks but not for most open-ended agent tasks.
  - (assessment) It is a position paper, so its empirical support is indirect.
  - (assessment) The claim "LLMs can't plan" was made before 2024–2025 long-reasoning models and needs re-testing.
- **Code availability:** not verified
- **Unresolved research gaps:** Building verifiers or critics for soft constraints such as preferences, style, and commonsense; LLM-assisted acquisition of verifier models; the cost and latency of generate–test loops.

### 8. Self-verification limitations

- **Title:** On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks
- **Authors:** Kaya Stechly, Karthik Valmeekam, Subbarao Kambhampati
- **Venue:** ICLR 2025 (proceedings PDF header "Published as a conference paper at ICLR 2025", via proceedings.iclr.cc)
- **Year:** 2025 (arXiv v1 Feb 2024)
- **Link:** https://arxiv.org/abs/2402.08115
- **Core contribution:** A controlled test showing that GPT-4 self-critique degrades performance on formally verifiable tasks, while a sound external verifier gives large gains. Most of that gain is kept by simple re-sampling with the verifier.
- **Methodology:** Compares standard prompting, LLM+LLM self-critique, LLM+sound verifier (with varied feedback richness), and sampling plus verifier (k=15). Measures the LLM verifier's own false positive and false negative rates.
- **Datasets/benchmarks:** Game of 24, Graph Coloring, Blocksworld and Mystery Blocksworld (from PlanBench). 100 instances each. Verifiers: SymPy, a custom edge checker, VAL.
- **Evaluation metrics:** Task accuracy; verifier accuracy, FPR, and FNR. Examples: Graph Coloring falls from 16% to 2% under self-critique; GPT-4 verifier FNR is 95.8% on coloring.
- **Limitations:**
  - (stated) Three formal domains, GPT-4 only, and prompt sensitivity.
  - (stated) CoT verification costs about 17× more tokens.
  - (assessment) It does not test reasoning-trained models (o1/R1-class) or fine-tuned verifiers.
  - (assessment) The domains are chosen to have cheap sound verifiers, so the conclusions may not transfer to fuzzy tasks.
- **Code availability:** not verified
- **Unresolved research gaps:** Whether RL-trained reasoning models change the self-verification picture; calibrating LLM verifiers; the value of feedback content versus mere re-sampling.

---

## C. Reflection and self-correction

### 9. Reflexion

- **Title:** Reflexion: Language Agents with Verbal Reinforcement Learning
- **Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao (arXiv v4). The NeurIPS proceedings page lists five authors without Edward Berman.
- **Venue:** NeurIPS 2023 (proceedings.neurips.cc, Main Conference Track)
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2303.11366 ; https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html
- **Core contribution:** Agents improve across trials without weight updates. After a failure they write a verbal self-reflection on the task feedback into an episodic memory buffer and condition the next attempt on it.
- **Methodology:** Actor (ReAct or CoT), evaluator (environment reward, heuristics, LLM judge, or self-generated unit tests), and self-reflection model. Memory is a bounded sliding window. Models: GPT-4, GPT-3.5, text-davinci-003, and others.
- **Datasets/benchmarks:** ALFWorld (134 tasks), HotpotQA (100), HumanEval, MBPP (Python and Rust), LeetcodeHardGym (40, new), and WebShop (negative result).
- **Evaluation metrics:** Task success; EM; pass@1 (HumanEval Python 91.0 vs 80.1 for GPT-4); hallucination rate; learning curves over trials.
- **Limitations:**
  - (stated) It can settle in non-optimal local minima.
  - (stated) Memory is a bounded window.
  - (stated) Test-driven code self-evaluation fails on non-deterministic or impure code.
  - (stated) It depends on self-evaluation quality and has no success guarantee.
  - (stated) No gain on WebShop, which needs creative exploration.
  - (stated) MBPP has a 16.3% false-positive rate for self-tests.
  - (assessment) Many gains rely on a reliable external success signal (environment reward or ground-truth tests), so it is closer to "self-correction with external feedback" in the sense of entry 13.
- **Code availability:** https://github.com/noahshinn024/reflexion (as given in the NeurIPS abstract)
- **Unresolved research gaps:** Reflection without an oracle success signal; memory scaling and retrieval of reflections; transfer of reflections across tasks.

### 10. Self-Refine

- **Title:** Self-Refine: Iterative Refinement with Self-Feedback
- **Authors:** Aman Madaan, Niket Tandon, Prakhar Gupta, et al.
- **Venue:** NeurIPS 2023 (proceedings.neurips.cc, Main Conference Track)
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2303.17651 ; https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract.html
- **Core contribution:** One LLM acts as generator, feedback provider, and refiner in a loop, with no training and no external signal.
- **Methodology:** Few-shot prompts for feedback and refinement, iterated until a stopping condition is met. Models: GPT-3.5 (text-davinci-003), ChatGPT, GPT-4, and Codex for code. Vicuna-13B was tried and failed to follow the prompts.
- **Datasets/benchmarks:** Seven tasks: dialogue response generation, code optimization, code readability, math reasoning, sentiment reversal, acronym generation, and constrained generation.
- **Evaluation metrics:** Human and GPT-4 preference; percent of programs optimized; solve rate; keyword coverage. The paper reports an average gain of about 20% absolute.
- **Limitations:**
  - (stated) It needs a strong instruction-following base model.
  - (stated) It uses closed models only and English only.
  - (stated) Prompting could be misused for harmful outputs.
  - (assessment) Entry 12 shows that its constrained-generation gain largely disappears with a stronger initial prompt, and that math gains are minimal without an oracle.
- **Code availability:** https://selfrefine.info/ (code, data, demo, per arXiv comments)
- **Unresolved research gaps:** Separating gains from refinement versus a weak initial prompt; compute-matched comparisons with sampling; when self-feedback is informative.

### 11. CRITIC

- **Title:** CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing
- **Authors:** Zhibin Gou, Zhihong Shao, Yeyun Gong, et al.
- **Venue:** ICLR 2024 (arXiv comment)
- **Year:** 2024 (arXiv v1 May 2023)
- **Link:** https://arxiv.org/abs/2305.11738
- **Core contribution:** Grounds self-correction in external tools. The LLM verifies parts of its output with a search engine, code interpreter, or toxicity API, then revises.
- **Methodology:** A verify-then-correct loop driven by in-context demonstrations, with tools: Google search (top result, cached), a Python interpreter, and the Perspective API. Models: text-davinci-003, ChatGPT, LLaMA-2 7B/13B/70B. Includes a "CRITIC w/o Tool" ablation.
- **Datasets/benchmarks:** AmbigNQ, TriviaQA, HotpotQA (500 validation examples each); GSM8K, SVAMP, TabMWP; RealToxicityPrompts (1k prompts).
- **Evaluation metrics:** EM and F1; accuracy; max toxicity, toxicity probability, perplexity, dist-2/3. For example, ChatGPT gains +7.7 F1 on QA; ChatGPT toxicity probability falls from 0.192 to 0.040.
- **Limitations:**
  - (stated) Latency grows linearly with correction iterations.
  - (stated) It depends on hand-crafted demonstrations.
  - (stated) It is text-only and its scope is uncertain.
  - (assessment) The ablation shows that removing tools removes most of the gain. The method is better read as tool-based verification than as "self"-correction.
- **Code availability:** not verified
- **Unresolved research gaps:** Choosing which claims to verify; robustness to noisy or adversarial tool outputs; tool cost-awareness.

### 12. LLMs Cannot Self-Correct Reasoning Yet

- **Title:** Large Language Models Cannot Self-Correct Reasoning Yet
- **Authors:** Jie Huang, Xinyun Chen, Swaroop Mishra, et al.
- **Venue:** ICLR 2024 (arXiv comment; iclr.cc poster listing)
- **Year:** 2024 (arXiv v1 Oct 2023)
- **Link:** https://arxiv.org/abs/2310.01798
- **Core contribution:** Shows that intrinsic self-correction, meaning correction with no external feedback, does not improve and often hurts reasoning accuracy. Earlier positive results relied on oracle labels to decide when to stop.
- **Methodology:** Re-runs self-correction with and without oracle stopping. Compares multi-agent debate with compute-matched self-consistency. Re-examines Self-Refine's constrained generation with a stronger initial prompt. Models: GPT-3.5-Turbo, GPT-4, GPT-4-Turbo, Llama-2-70b-chat.
- **Datasets/benchmarks:** GSM8K, CommonSenseQA, HotpotQA (closed-book), CommonGen-Hard.
- **Evaluation metrics:** Accuracy; answer-change rates (correct→incorrect, incorrect→correct); number of model calls. For example, GPT-3.5 on CommonSenseQA falls from 75.8 to 38.1 after one round of intrinsic self-correction; debate scores 83.0 vs self-consistency 88.2 with 9 responses.
- **Limitations:**
  - (stated) The focus is on reasoning; self-correction may still help style or safety.
  - (stated) LLMs may judge inappropriateness better than they detect reasoning errors.
  - (assessment) It predates RL-trained reasoning models whose long CoT contains implicit backtracking. Whether "intrinsic" correction inside a reasoning trace counts is left open.
- **Code availability:** not verified
- **Unresolved research gaps:** Training-time versus inference-time self-correction (addressed by entry 14); self-correction in agentic loops with partial environment feedback.

### 13. Self-correction critical survey

- **Title:** When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs
- **Authors:** Ryo Kamoi, Yusen Zhang, Nan Zhang, Jiawei Han, Rui Zhang
- **Venue:** Transactions of the Association for Computational Linguistics (TACL), vol. 12, pp. 1417–1440 (arXiv journal-ref)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2406.01297
- **Core contribution:** A critical survey that classifies self-correction research questions (RQ1 intrinsic; RQ2 with external information; RQ3 versus strong baselines), separates realistic from unrealistic (oracle-using) frameworks, and proposes a checklist for fair experiments.
- **Methodology:** Literature survey (coverage to May 2024) with a taxonomy and evaluation checklist.
- **Datasets/benchmarks:** N/A (survey)
- **Evaluation metrics:** N/A. The survey recommends measuring feedback quality directly, for example error-detection accuracy, and comparing against compute-matched baselines such as self-consistency.
- **Limitations:**
  - (stated) Coverage runs to May 2024.
  - (stated) Its taxonomy excludes cross-architecture multi-model correction.
  - (stated) It focuses on inference-time methods.
  - (assessment) It does not cover 2025 RL-trained reasoning/agent models, where self-correction behaviors are reported to emerge (entry 22).
- **Code availability:** not verified
- **Unresolved research gaps** (stated as survey conclusions): Successful intrinsic self-correction with prompted LLMs is unshown outside tasks with decomposable or easily verifiable outputs. Feedback generation is the bottleneck. Self-correction with small fine-tuning datasets is unexplored.

### 14. SCoRe

- **Title:** Training Language Models to Self-Correct via Reinforcement Learning
- **Authors:** Aviral Kumar, Vincent Zhuang, Rishabh Agarwal, et al.
- **Venue:** ICLR 2025 (proceedings.iclr.cc)
- **Year:** 2025 (arXiv v1 Sep 2024)
- **Link:** https://arxiv.org/abs/2409.12917 ; https://proceedings.iclr.cc/paper_files/paper/2025/hash/871ac99fdc5282d0301934d23945ebaa-Abstract-Conference.html
- **Core contribution:** Multi-turn online RL on the model's own data teaches intrinsic self-correction. This avoids the distribution shift and "behavior collapse" (minimal edits) seen with SFT on correction traces.
- **Methodology:** Two-stage RL. Stage I optimizes the second attempt while a KL constraint keeps the first attempt near the base model. Stage II optimizes both attempts jointly with a reward bonus for improving from attempt 1 to attempt 2. Baselines: Self-Refine, STaR, Pair-SFT.
- **Datasets/benchmarks:** MATH (MATH500 evaluation) with Gemini 1.5 Flash; MBPP training with HumanEval and MBPP-R evaluation, using Gemini 1.0 Pro.
- **Evaluation metrics:** Accuracy@t1, Accuracy@t2, Δ(t1,t2), Δ(i→c), Δ(c→i). MATH Δ is +4.4% vs −11.2% for the base model. The abstract reports +15.6% (MATH) and +9.1% (HumanEval) self-correction improvement.
- **Limitations:**
  - (stated) Only one round of correction was trained, because of infrastructure limits.
  - (stated) Stages I and II are not unified.
  - (assessment) It is a closed-model study (Gemini) with no open replication in the paper.
  - (assessment) It uses single-turn math and code with ground-truth reward, not agentic multi-step tasks.
- **Code availability:** not verified
- **Unresolved research gaps:** More than two correction attempts; self-correction in tool-using agents where the reward is delayed; open-weight reproduction.

---

## D. Tool learning

### 15. Toolformer

- **Title:** Toolformer: Language Models Can Teach Themselves to Use Tools
- **Authors:** Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, et al. (arXiv lists 8 authors. The NeurIPS proceedings list 9, adding Eric Hambro.)
- **Venue:** NeurIPS 2023 (proceedings.neurips.cc, Main Conference Track)
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2302.04761 ; https://proceedings.neurips.cc/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract.html
- **Core contribution:** Self-supervised learning of when and how to call APIs. The LM annotates its own pre-training text with candidate API calls and keeps those that reduce loss on the following tokens.
- **Methodology:** GPT-J (6.7B) samples API calls in CCNet text, executes them, filters by perplexity reduction, and is fine-tuned on the augmented corpus. Tools: Atlas QA, calculator, BM25 Wikipedia search, NLLB translation, calendar.
- **Datasets/benchmarks:** LAMA (SQuAD, Google-RE, T-REx); ASDiv, SVAMP, MAWPS; WebQS, NQ, TriviaQA; MLQA; TempLAMA, Dateset; WikiText and CCNet perplexity.
- **Evaluation metrics:** Task-specific zero-shot accuracy variants (answer in the first k words, first number correct); perplexity.
- **Limitations:**
  - (stated) No tool chaining.
  - (stated) No interactive tool use (cannot browse or reformulate queries).
  - (stated) Call decisions are sensitive to input wording.
  - (stated) Sample-inefficient: over 1M documents yield a few thousand useful calculator calls.
  - (stated) Ignores tool cost.
  - (assessment) A single call per position makes it unsuitable for multi-step agent loops.
- **Code availability:** not verified (no official link on the arXiv page)
- **Unresolved research gaps:** Self-supervised learning of multi-step, interactive tool use; cost-aware calling; scaling past a handful of tools.

### 16. Gorilla

- **Title:** Gorilla: Large Language Model Connected with Massive APIs
- **Authors:** Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez
- **Venue:** NeurIPS 2024 (proceedings.neurips.cc PDF; NeurIPS 2024 poster)
- **Year:** 2024 (arXiv May 2023)
- **Link:** https://arxiv.org/abs/2305.15334 ; https://proceedings.neurips.cc/paper_files/paper/2024/file/e4c61f578ff07830f5c37378dd3ecb0d-Paper-Conference.pdf
- **Core contribution:** A LLaMA-7B model fine-tuned with Retriever-Aware Training (RAT) to write correct API calls from large ML API hubs and adapt to documentation that changes at test time. Introduces APIBench.
- **Methodology:** Self-instruct generation of about 10 instructions per API (over 11k pairs) with GPT-4. Fine-tuning with and without retrieved documentation in the prompt. Retrievers: zero-shot, BM25, GPT-Index, oracle.
- **Datasets/benchmarks:** APIBench: TorchHub (~94–95), TensorHub (696), HuggingFace (925) APIs.
- **Evaluation metrics:** AST sub-tree matching accuracy; hallucination rate (calls matching no real API); constraint-aware accuracy.
- **Limitations:**
  - (stated) ML APIs only, with possible bias.
  - (stated) Generated code is not execution-tested.
  - (stated) A large gap separates practical retrievers from the oracle; weak retrievers can hurt.
  - (stated) Constraint evaluation uses a TorchHub subset only.
  - (stated) Adaptation to documentation changes is shown only qualitatively.
  - (assessment) It evaluates single calls, not multi-step tool workflows (entry 18 notes Gorilla could not be applied to ToolBench's multi-tool settings).
- **Code availability:** https://gorilla.cs.berkeley.edu (code, model, data, demo, per the abstract)
- **Unresolved research gaps:** Execution-based correctness; robust retrieval over evolving tool catalogs; multi-call composition.

### 17. API-Bank

- **Title:** API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs
- **Authors:** Minghao Li, Yingxiu Zhao, Bowen Yu, et al.
- **Venue:** EMNLP 2023 (arXiv comment)
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2304.08244
- **Core contribution:** A runnable tool-use benchmark (73 APIs, 314 dialogues, 753 calls) that grades three ability levels (Call, Retrieve+Call, Plan+Retrieve+Call), plus a large training set and the fine-tuned Lynx model.
- **Methodology:** Executable API system with annotated dialogues. Training set of 1,888 dialogues covering 2,138 APIs in about 1,000 domains. Lynx-7B is fine-tuned from Alpaca. Includes a per-model error taxonomy.
- **Datasets/benchmarks:** API-Bank (introduced).
- **Evaluation metrics:** API-call accuracy (same database effects and results as gold); ROUGE-L for responses. Overall: GPT-4 60.24%, GPT-3.5-turbo 47.16%, Lynx-7B 39.58%.
- **Limitations:**
  - (stated) English only.
  - (stated) Only a 7B model was fine-tuned.
  - (assessment) Small evaluation set with synthetic APIs.
  - (assessment) Its error analysis finds that GPT-4's dominant failure is API retrieval (67.86%), which points to retrieval rather than call formatting as the bottleneck for strong models.
- **Code availability:** not verified
- **Unresolved research gaps:** Retrieval-centric tool-use evaluation at scale; planning-level metrics beyond call accuracy.

### 18. ToolLLM / ToolBench

- **Title:** ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs
- **Authors:** Yujia Qin, Shihao Liang, Yining Ye, et al.
- **Venue:** ICLR 2024 (proceedings.iclr.cc; OpenReview PDF header "Published as a conference paper at ICLR 2024")
- **Year:** 2024 (arXiv Jul 2023)
- **Link:** https://arxiv.org/abs/2307.16789 ; https://proceedings.iclr.cc/paper_files/paper/2024/hash/28e50ee5b72e90b50e7196fde8ea260e-Abstract-Conference.html
- **Core contribution:** An end-to-end tool-learning framework: the ToolBench dataset (16,464 RapidAPI REST APIs, 49 categories, about 126k instruction–solution pairs, generated by ChatGPT); the DFSDT search-based reasoning strategy; the ToolEval automatic evaluator; and ToolLLaMA (LLaMA-2-7B) with a neural API retriever.
- **Methodology:** ChatGPT generates single- and multi-tool instructions and annotates solution paths with DFSDT, a depth-first decision tree that can "give up" and backtrack. Fine-tuning with context extended to 8k. Dense API retriever.
- **Datasets/benchmarks:** ToolBench (I1/I2/I3 at instruction, tool, and category generalization levels); APIBench for out-of-distribution transfer.
- **Evaluation metrics:** Pass rate and win rate against ChatGPT-ReACT, both judged by ChatGPT; retriever NDCG. Example: ToolLLaMA+DFSDT pass rate 66.7, win rate 60.0.
- **Limitations:**
  - (stated) ChatGPT as judge agrees with humans 87.1% (pass) and 80.3% (win), so it is not equivalent to human evaluation.
  - (stated) Comparing solution paths is subjective.
  - (stated) RapidAPI endpoints change over time, which hurts reproducibility.
  - (assessment) Data and labels come from a proprietary teacher, so the ceiling is the teacher's behavior.
  - (assessment) Live-API drift makes later comparisons hard.
- **Code availability:** https://github.com/OpenBMB/ToolBench (linked from the ICLR/OpenReview PDF)
- **Unresolved research gaps:** Reproducible, stable tool environments (cached or simulated APIs); judge-free, execution-grounded evaluation; learning from environment feedback instead of teacher imitation (taken up by entries 21–22).

### 19. Tool learning survey

- **Title:** Tool Learning with Large Language Models: A Survey
- **Authors:** Changle Qu, Sunhao Dai, Xiaochi Wei, et al.
- **Venue:** Frontiers of Computer Science (accepted per arXiv comments; DOI 10.1007/s11704-024-40678-2). Journal issue year not verified.
- **Year:** 2024 (arXiv v1 May 2024; v3 Nov 2024)
- **Link:** https://arxiv.org/abs/2405.17935
- **Core contribution:** A survey that organizes tool learning by why (benefits) and how. The "how" follows four stages: task planning, tool selection, tool calling, and response generation. Benchmarks and evaluation methods are mapped to each stage. **Cite as a survey.**
- **Methodology:** Literature survey with a maintained paper list.
- **Datasets/benchmarks:** N/A (catalogs benchmarks)
- **Evaluation metrics:** N/A
- **Limitations:**
  - (assessment) Coverage ends in late 2024, before agentic RL for tools (entries 21–24) and MCP-era work (entry 20).
  - (assessment) The stage taxonomy assumes a pipeline view that end-to-end RL-trained agents blur.
- **Code availability:** https://github.com/quchangle1/LLM-Tool-Survey (paper list)
- **Unresolved research gaps** (as framed by the survey's challenges section, summarized): Tool-use safety and robustness, efficiency, and unified evaluation.

### 20. MCPGauge ("Help or Hurdle?")

- **Title:** Help or Hurdle? Rethinking Model Context Protocol-Augmented Large Language Models
- **Authors:** Wei Song, Haonan Zhong, Ziqi Ding, Jingling Xue, Yuekang Li
- **Venue:** arXiv preprint
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2508.12566
- **Core contribution:** Introduces MCPGauge, an empirical framework for how LLMs behave with Model Context Protocol tool access along four axes: proactivity, compliance, effectiveness, and overhead. Finds that MCP access frequently hurts accuracy.
- **Methodology:** Six commercial LLMs, 30 MCP tool suites, a 160-prompt suite, and 25 datasets. One-turn and two-turn settings. About 20k API calls.
- **Datasets/benchmarks:** 25 datasets spanning knowledge comprehension, general reasoning, and code generation (specific list in paper), plus the authors' 160-prompt suite.
- **Evaluation metrics:** Tool Invocation Accuracy (proactivity); Instruction Following Accuracy (compliance); accuracy and pass@k (effectiveness); input-token ratio (overhead). Findings: MCP lowers accuracy by an average of 9.5% (code generation −17.0%); input tokens rise 3.25× to 236.5×.
- **Limitations:**
  - (assessment) Only one- and two-turn dialogues (the authors report marginal gains from more turns in preliminary tests).
  - (assessment) The overhead and effectiveness analyses keep only instances where a tool was called, which risks selection bias.
  - (assessment) Benchmark prompts were modified to insert tool instructions.
  - (assessment) The prompt suite and tool set are author-built.
  - (assessment) It is a non-peer-reviewed preprint.
  - The paper has no dedicated limitations section; these points are drawn from its methodology.
- **Code availability:** not available (the paper says code and data will be released on acceptance)
- **Unresolved research gaps:** When tool context helps versus distracts; tool-description compression and selective exposure; protocol-level evaluation with multi-turn agents.

---

## E. Agentic RL and test-time scaling for tool use

### 21. Search-R1

- **Title:** Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- **Authors:** Bowen Jin, Hansi Zeng, Zhenrui Yue, et al.
- **Venue:** COLM 2025 (arXiv v4 PDF header: "Published as a conference paper at COLM 2025")
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2503.09516
- **Core contribution:** Outcome-reward RL (R1-style) trains an LLM to issue search queries during step-by-step reasoning, with multi-turn retrieval interleaved in the rollout.
- **Methodology:** PPO (default) and GRPO compared. Retrieved tokens are masked from the loss for stability. Rule-based outcome reward. E5 retriever over the 2018 Wikipedia dump (top-3). Qwen2.5-3B/7B base and instruct (14B in appendix). Baselines: direct, CoT, RAG, IRCoT, Search-o1, SFT, R1 without search, rejection sampling.
- **Datasets/benchmarks:** NQ, TriviaQA, PopQA, HotpotQA, 2WikiMultiHopQA, MuSiQue, Bamboogle.
- **Evaluation metrics:** Exact match. Abstract reports relative gains of about 41% (Qwen2.5-7B) and 20% (3B) over RAG baselines; figures differ across arXiv versions.
- **Limitations:**
  - (stated, future work) Richer search strategies and rewards; uncertainty-based retrieval; other tools and multimodality.
  - (assessment) Case studies show answering without enough evidence and being misled by irrelevant passages.
  - (assessment) Static Wikipedia QA with EM reward rewards short-answer matching, not research-quality synthesis.
  - (assessment) Reported percentages changed between versions, so cite the version used.
- **Code availability:** https://github.com/PeterGriffinJin/Search-R1
- **Unresolved research gaps:** Process-level or evidence-grounded rewards; open-web, noisy search; long-horizon research tasks.

### 22. ReTool

- **Title:** ReTool: Reinforcement Learning for Strategic Tool Use in LLMs
- **Authors:** Jiazhan Feng, Shijue Huang, Xingwei Qu, et al.
- **Venue:** ICLR 2026 (iclr.cc poster listing; ICLR 2026 proceedings)
- **Year:** 2026 (arXiv Apr 2025)
- **Link:** https://arxiv.org/abs/2504.11536 ; https://iclr.cc/virtual/2026/poster/10006978
- **Core contribution:** RL with code-interpreter execution interleaved in long-form reasoning. The model learns when and how to call code from outcome rewards, reaching higher math accuracy with far fewer RL steps than text-only RL.
- **Methodology:** Cold-start SFT on code-augmented traces built by rewriting text reasoning (from sources such as Open-Thoughts) to include code and interpreter outputs. Then PPO (VeRL) with sandboxed asynchronous execution, interpreter outputs masked, and a ±1 answer-match reward. No executability reward, to limit reward hacking. Backbones: Qwen2.5-32B-Instruct and DeepSeek-R1-Distill-Qwen-32B.
- **Datasets/benchmarks:** AIME 2024, AIME 2025.
- **Evaluation metrics:** pass@1 averaged over 32 samples. 67.0 (AIME24, Qwen2.5-32B-Instruct, 400 steps) vs 40.0 for text-only RL (1,080 steps). 72.5 with the R1-Distill backbone. Code-usage statistics.
- **Limitations:**
  - (assessment) The paper has no limitations section.
  - (assessment) Evaluated only on competition math with a single tool (Python).
  - (assessment) "Emergent code self-correction" is shown through case studies, not measured systematically.
  - (assessment) AIME sets are small, so variance is high.
- **Code availability:** not verified
- **Unresolved research gaps:** Multi-tool and open-domain agentic RL; reward hacking through tool outputs; measuring whether tool-use policies transfer beyond math.

### 23. RAGEN / StarPO

- **Title:** RAGEN: Understanding Self-Evolution in LLM Agents via Multi-Turn Reinforcement Learning
- **Authors:** Zihan Wang, Kangrui Wang, Qineng Wang, et al.
- **Venue:** arXiv preprint (no acceptance found)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2504.20073
- **Core contribution:** StarPO, a trajectory-level RL framework for multi-turn agents, and the RAGEN system. Identifies the "Echo Trap" instability (reward-variance collapse, entropy drop, gradient spikes) and a stabilized variant, StarPO-S.
- **Methodology:** `<think>`/`<answer>` per-turn format; PPO or GRPO over full trajectories. StarPO-S keeps the highest-uncertainty prompts, removes the KL term, and uses asymmetric/decoupled clipping. Qwen2.5-Instruct 0.5B (symbolic tasks) and 3B (WebShop); 3B–72B in appendix.
- **Datasets/benchmarks:** Bandit, Sokoban, FrozenLake, WebShop.
- **Evaluation metrics:** Success rate; rollout entropy; in-group reward variance; response length; gradient norm.
- **Limitations:**
  - (stated) Small-scale tasks; no replay buffers or other established RL practices; no multimodal tasks.
  - (stated finding) Without reasoning-aware rewards, multi-turn RL rarely yields genuine reasoning; agents learn shallow strategies or hallucinated thoughts.
  - (assessment) Toy environments and small models limit the external validity of the stability findings.
- **Code availability:** https://github.com/RAGEN-AI/RAGEN
- **Unresolved research gaps:** Reasoning-aware or process rewards for agents; whether Echo Trap persists at scale and in tool-rich environments; rollout diversity design.

### 24. Test-Time Interaction (TTI)

- **Title:** Thinking vs. Doing: Agents that Reason by Scaling Test-Time Interaction
- **Authors:** Junhong Shen, Hao Bai, Lunjun Zhang, et al.
- **Venue:** arXiv preprint. Also presented as a workshop poster at the NeurIPS 2025 Workshop on Scaling Environments for Agents (confirmed on nips.cc). Not a main-track paper as far as verified.
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2506.07976
- **Core contribution:** Proposes scaling the interaction horizon (more environment steps per rollout to explore, backtrack, and re-plan) as a test-time compute axis distinct from longer per-step reasoning. Introduces TTI, curriculum online RL over rollout length.
- **Methodology:** First, prompting-only "check again" interaction scaling. Then TTI: online filtered behavior cloning with a multiplicative curriculum on maximum horizon (10→30 steps) using synthetic tasks. Gemma 3 12B. Compared at a fixed token budget against longer reasoning, budget forcing, and best-of-n.
- **Datasets/benchmarks:** WebVoyager (427 tasks, with Bing replacing Google); WebArena (812; 62-task analysis split).
- **Evaluation metrics:** Task success rate. WebVoyager 64.8% vs 55.8% zero-shot; WebArena 26.1% vs 18.3%.
- **Limitations:**
  - (stated) Over-reliance on resetting to search.
  - (stated) Weak self-verification: the agent submits answers it knows are wrong.
  - (stated) Smaller gains on WebArena, partly from environment bugs.
  - (stated) Some domains regress (Amazon, GitHub).
  - (stated) Simple RL; memory and context limits at longer horizons.
  - (stated) The thinking-versus-acting trade-off remains open.
  - (assessment) Single backbone; web-only.
- **Code availability:** not verified
- **Unresolved research gaps:** Principled allocation between thinking and acting tokens; interaction scaling when actions are irreversible or costly; reliable termination and self-verification.

---

## Recurring weaknesses in this slice *(author's assessment)*

- **Self-evaluation is the weak link, and many methods quietly depend on it.** ToT and LATS value functions, ADaPT's success detector, Reflexion's self-tests, and Self-Refine's feedback all assume the LLM can judge its own outputs. Entries 8, 12, and 13 show this assumption fails on reasoning and planning, and ADaPT and TTI document self-report errors directly. *Applies to: 2, 4, 5, 9, 10, 24; evidenced by 8, 12, 13.*
- **Oracle leakage and weak baselines inflate self-correction gains.** Examples include ground-truth stopping, ground-truth unit tests treated as "self" feedback, weak initial prompts, and no compute-matched self-consistency or best-of-n baseline. *Applies to: 9, 10 (as re-analyzed by 12), and partly 2, 4; critique in 12, 13.*
- **Compute is under-reported or not matched.** Search and reflection methods report accuracy without a common token or call budget. ToT reports 5–100× token overhead; LATS and CRITIC report linear or worse cost growth; MCP context inflates input tokens up to 236×. Few papers compare at equal compute (exceptions: 12, 24). *Applies to: 2, 3, 4, 9, 11, 20.*
- **Small, saturated, or toy evaluations.** Many subsets have 50–100 items (LATS, Reflexion HotpotQA), toy RL environments (RAGEN), puzzle tasks (ToT, Stechly), or a single domain (ReTool on AIME). *Applies to: 2, 4, 8, 9, 22, 23.*
- **Reproducibility hazards from closed models and live APIs.** Key results rest on deprecated OpenAI or Gemini models (1, 2, 9, 10, 12, 14), on a proprietary teacher and LLM judge (18), or on live APIs that drift (16, 18).
- **Environments assumed reversible, cheap, and safe.** Tree search assumes rollback (4 states this). Agentic RL assumes cheap, side-effect-free tools (21, 22). Interaction scaling assumes retries are free (24). Real tools (payments, writes, emails) violate all three. *Applies to: 2, 3, 4, 21, 22, 24.*
- **Tool use is evaluated mostly as single-call accuracy.** Gorilla, APIBench, API-Bank, and Toolformer measure whether one call is correct. Multi-step composition, recovery from tool errors, and whether tool context helps or distracts (entry 20) are rarely measured. *Applies to: 15, 16, 17, and partly 18.*
- **Planning claims are not re-tested on newer model classes.** The strong negative results (6, 7, 8, 12) predate RL-trained long-reasoning models. Conversely, the 2025 RL papers (21–23) do not test on PlanBench-style verifiable planning. The two lines of work are rarely compared head to head.

## Open problems that a small team could attack *(author's assessment)*

1. **Compute-matched re-evaluation of reflection and search for agents.** Re-run ReAct, Reflexion, LATS, and ADaPT against best-of-n and self-consistency at equal token or tool-call budgets, on open-weight models, following Kamoi et al.'s checklist (entry 13). This needs inference only, and the cited repos (1, 2, 4, 9) make it feasible.
2. **Calibrated success detectors for agent loops.** Train or calibrate a small verifier that predicts sub-task success from a trajectory, and plug it into ADaPT-style decomposition and Reflexion-style retry. Entry 5 measures more than 30-point overestimation on WebShop, which provides a ready baseline to beat.
3. **When does tool context hurt? A controlled MCP/tool-exposure study.** Extend entry 20's finding (−9.5% average) with ablations over number of tools exposed, description length, and retrieval-filtered exposure, using open models and released code. This addresses a reproducibility gap in the preprint.
4. **Self-verification in RL-trained reasoning models.** Replicate Stechly et al.'s protocol (entry 8: Game of 24, graph coloring, Blocksworld and Mystery Blocksworld with sound verifiers) on open R1-class models. This tests whether the "LLMs can't self-verify" result still holds, which matters for both the planning and the self-correction narratives.
5. **Agentic RL with irreversible or costly actions.** Build a small environment suite where some tool calls carry cost or cannot be undone, and test whether Search-R1, ReTool, or TTI-style policies learn caution. Current agentic-RL environments (21–24) are almost all reset-free and side-effect-free.
6. **Stable, cached tool environments for reproducible tool-learning evaluation.** Snapshot a ToolBench subset into deterministic mocks with execution-based grading (no LLM judge), and re-score published systems. This addresses entry 18's stated API-drift and judge-agreement issues.

## Dropped or downgraded seeds

- **Plan-and-Solve, Chain-of-Thought, Voyager:** verified, but moved to the intro to stay within the 24-entry budget.
- **Unconfirmed venues, kept as arXiv preprints:** RAGEN (entry 23) and MCPGauge (entry 20). TTI (entry 24) has only a confirmed NeurIPS 2025 *workshop* poster.
- **Author-list discrepancies:** the arXiv and proceedings author lists differ for Reflexion (Berman appears on arXiv v4 only) and Toolformer (Hambro appears in the proceedings only). Both lists are recorded in the entries.
- **MCP:** no peer-reviewed MCP paper was confirmed. One substantial preprint (entry 20) is included. MCP benchmark papers (MCP-RADAR, MCPToolBench++, TheMCPCompany) and the MCP security survey (arXiv 2503.23278) appeared in search but were not verified on primary pages. They also fall under the benchmark slice.
- **"Test-time compute for agents":** represented by TTI (entry 24). Non-agent test-time-compute papers (e.g., compute-optimal scaling for single-turn reasoning) were out of scope and not verified.

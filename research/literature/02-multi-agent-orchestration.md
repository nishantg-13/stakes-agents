# 02 — Multi-Agent LLM Systems, Orchestration, and Coordination

*Literature slice compiled 2026-11-08. Every entry below was checked against a primary source page
(arxiv.org/abs or arXiv HTML full text, plus a venue page: proceedings.mlr.press, proceedings.iclr.cc,
iclr.cc / icml.cc / neurips.cc virtual pages, or aclanthology.org). If a venue is given, acceptance was
confirmed on a venue page, in the authors' own arXiv "Comments" field, or on the authors' institutional
publication page; the source is noted in each entry. Anything not confirmed is marked "not verified".*

## Scope

This slice covers systems where **several LLM-driven agents** (role-played personas, debaters, workers
under an orchestrator, or nodes in a graph) work together on one task, and the research question is
*how they are organised, how they communicate, and whether organising them pays off*. It runs from the
2023 framework papers (CAMEL, AutoGen, MetaGPT), through debate and ensembling (multi-agent debate,
sampling-and-voting, Mixture-of-Agents), to automated design of agent systems (GPTSwarm, ADAS, AFlow,
G-Designer, MasRouter, learned orchestrators). It also covers the counter-literature from 2024 to 2026:
work showing that MAS gains are fragile, explained by voting or extra compute, or negative on sequential
tasks; failure taxonomies and failure attribution; and controlled scaling studies. One preprint bridges
to classical distributed coordination (AAMAS community). Single-agent tool use, memory, planning and
self-reflection belong to other slices and are left out here unless a paper's main subject is
multi-agent.

Entries are grouped as: **A. Frameworks** (1–3), **B. Debate and ensembling** (4–7),
**C. Critiques and scaling studies** (8–12), **D. Automated design, topology, routing and
orchestration** (13–19), **E. Failure analysis** (20–21), **F. Bridging to classical MAS** (22).
There is one grey-literature appendix (G1, not peer reviewed).

---

## A. Frameworks

### 1. CAMEL

- **Title:** CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society
- **Authors:** Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, Bernard Ghanem
- **Venue:** NeurIPS 2023 (source: arXiv Comments field, "Accepted at NeurIPS'2023")
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2303.17760
- **Core contribution:** A "role-playing" framework in which two LLM agents (an AI user and an AI
  assistant) work through a task with very little human input. "Inception prompting" keeps them on task.
  The paper also uses the transcripts as a source of synthetic instruction data.
- **Methodology:** Two gpt-3.5-turbo agents are given roles and a task specified by a task-specifier
  agent. They alternate instruction and solution turns. GPT-4 summarises conversations and also serves as
  evaluator. LLaMA-7B is fine-tuned progressively on the generated datasets.
- **Datasets/benchmarks:** Generated AI Society (~25k conversations), Code, Math (50k), Science (20k per
  subject) and Misalignment datasets. HumanEval / HumanEval+ for the fine-tuned model.
- **Evaluation metrics:** Human pairwise preference (453 votes) and GPT-4 pairwise preference against
  single-shot gpt-3.5-turbo; pass@1 / pass@100 on HumanEval(+).
- **Limitations:** (stated) Failure modes such as role flipping, the assistant repeating instructions,
  "flake replies" and infinite message loops, which required hand-written termination rules; cost grows
  quadratically with conversation length. (assessment) The only baseline is single-shot gpt-3.5. No
  equal-compute single-agent baseline is used, such as self-refine or self-consistency with the same
  number of calls. GPT-4 both summarises and judges the outputs, a self-preference risk.
- **Code availability:** https://github.com/camel-ai/camel (linked from the arXiv abstract page)
- **Unresolved research gaps:** Whether role-play adds anything beyond the extra tokens it spends;
  principled termination and anti-looping; measuring the quality of synthetic data produced by agent
  societies.

### 2. AutoGen

- **Title:** AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation
- **Authors:** Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al.
- **Venue:** COLM 2024 (source: Microsoft Research publication page lists "COLM 2024 | August 2024".
  The OpenReview forum could not be loaded because of a bot check, so the COLM acceptance rests on the
  authors' institutional page.)
- **Year:** 2023 (arXiv); 2024 (COLM)
- **Link:** https://arxiv.org/abs/2308.08155
- **Core contribution:** A general programming framework of "conversable agents": LLM-, human- and
  tool-backed agents that are composed through conversation patterns (two-agent chat, group chat with a
  speaker-selection manager) that developers define in natural language and code.
- **Methodology:** Framework paper with six application case studies (A1–A6). Each compares an AutoGen
  multi-agent design with single-model or prior-system baselines.
- **Datasets/benchmarks:** MATH (level-5 subset and full test set), Natural Questions (retrieval-augmented
  QA), ALFWorld (134 unseen tasks), OptiGuide safe/unsafe coding tasks (100), 12 hand-crafted group-chat
  tasks (pilot), conversational chess (qualitative).
- **Evaluation metrics:** Accuracy, F1/recall, task success rate, F1 for unsafe-code detection, LLM call
  count.
- **Limitations:** (stated) Some evaluations are pilot or qualitative only; LLMs do not follow all
  instructions; the best number of agents, roles and interaction pattern is an open question; large
  workflows are hard to debug; autonomy, safety, privacy and accountability risks. (assessment) The
  case-study format means baselines differ across applications and compute is not matched. The paper
  shows the framework is expressive, not that multi-agent structure beats an equally resourced single
  agent.
- **Code availability:** not verified (no repository link on the arXiv abstract page)
- **Unresolved research gaps:** Automatic choice of conversation pattern and agent count (later taken up
  by entries 13–19); observability and debugging of multi-agent traces (taken up by 20–21).

### 3. MetaGPT

- **Title:** MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework
- **Authors:** Sirui Hong, Mingchen Zhuge, Jiaqi Chen, et al.
- **Venue:** ICLR 2024 (oral; source: ICLR 2024 virtual oral page, iclr.cc/virtual/2024/oral/19756)
- **Year:** 2023 (arXiv); 2024 (ICLR)
- **Link:** https://arxiv.org/abs/2308.00352
- **Core contribution:** Encodes human Standardized Operating Procedures (SOPs) into a pipeline of
  role-specialised agents (Product Manager, Architect, Project Manager, Engineer, QA Engineer). The agents
  exchange *structured documents* (PRDs, designs, diagrams) instead of free chat, which reduces
  cascading hallucination.
- **Methodology:** An assembly-line workflow with a shared message pool and publish-subscribe filtering,
  so each agent sees only the messages relevant to its role. Executable feedback (run and debug the
  code) is added on top.
- **Datasets/benchmarks:** HumanEval (164), MBPP (427), and a self-built SoftwareDev set (70 tasks; 7
  used in the main comparison against ChatDev).
- **Evaluation metrics:** Pass@1; for SoftwareDev, human-rated executability (1–4), running time, tokens,
  cost, code statistics, tokens per line, human revision cost.
- **Limitations:** (stated) No UI/front-end agents or multimodal tools; struggles with diverse real-world
  requirements; users cannot easily interrupt agents or set per-agent checkpoints; self-improvement only
  edits role constraints. (assessment) SoftwareDev is small and self-constructed, with human-rated
  executability. The HumanEval/MBPP gains combine role structure with executable feedback, and there is
  no ablation of a single agent given the same SOP and feedback loop.
- **Code availability:** https://github.com/geekan/MetaGPT (linked from the arXiv abstract)
- **Unresolved research gaps:** Separating the value of *structured intermediate artifacts* from the
  value of *multiple agents*; evaluating SOP-driven MAS on realistic, repository-scale software tasks.

---

## B. Debate and ensembling

### 4. Multiagent Debate (Du et al.)

- **Title:** Improving Factuality and Reasoning in Language Models through Multiagent Debate
- **Authors:** Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch
- **Venue:** ICML 2024 (PMLR 235:11733–11763; https://proceedings.mlr.press/v235/du24e.html)
- **Year:** 2023 (arXiv); 2024 (ICML)
- **Link:** https://arxiv.org/abs/2305.14325
- **Core contribution:** Several instances of the same LLM each propose an answer, read each other's
  answers, and revise over several rounds toward a consensus. This "society of minds" approach improves
  reasoning and factuality using only black-box API access.
- **Methodology:** Default setting of 3 agents and 2 rounds with gpt-3.5-turbo-0301. Ablations vary the
  number of agents and rounds and include a mixed ChatGPT+Bard debate. Baselines are single agent,
  self-reflection, and multi-agent majority voting.
- **Datasets/benchmarks:** Arithmetic (100 generated), GSM8K (100), chess move prediction (300 games),
  biographies of 524 computer scientists, MMLU (100), BIG-Bench chess-state-tracking validity (100).
- **Evaluation metrics:** Accuracy; percentage of ground-truth biography facts judged consistent;
  Stockfish pawn score.
- **Limitations:** (stated) Higher compute cost; long debates overwhelm context and models attend mostly
  to recent responses; debates can converge confidently on wrong answers; poor uncertainty expression.
  (assessment) Evaluation sets are very small (often 100 items), so confidence intervals are wide. The
  majority-vote baseline is included, but at small scale. Later work (entries 8, 10) shows that most of
  the gain is attributable to voting.
- **Code availability:** Project page with code: https://composable-models.github.io/llm_debate/
  (linked from the arXiv Comments field)
- **Unresolved research gaps:** When debate adds anything beyond aggregation; debate with heterogeneous
  models; stopping and anti-conformity mechanisms.

### 5. Multi-Agent Debate for divergent thinking (Liang et al.)

- **Title:** Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate
- **Authors:** Tian Liang, Zhiwei He, Wenxiang Jiao, et al.
- **Venue:** EMNLP 2024 main conference (source: arXiv Comments field)
- **Year:** 2023 (arXiv); 2024 (EMNLP)
- **Link:** https://arxiv.org/abs/2305.19118
- **Core contribution:** Names the "Degeneration-of-Thought" problem: a model that has become confident
  in an answer stops generating new ideas under self-reflection. Proposes MAD, an affirmative debater, a
  negative debater and a judge, to force divergent reasoning.
- **Methodology:** Two debaters plus a judge that can stop the debate early (maximum 3 iterations). The
  "tit-for-tat" disagreement intensity is set by meta-prompts at four levels. Zero-shot, temperature 0.
- **Datasets/benchmarks:** Common MT (Chinese→English commonsense translation, ~1k examples);
  Counter-Intuitive Arithmetic Reasoning (CIAR, 200 questions, introduced by the paper).
- **Evaluation metrics:** COMET, BLEURT and human 1–5 ratings (MT); accuracy (CIAR); human-judged bias
  rate and Self-BLEU diversity.
- **Limitations:** (stated) More time and tokens (~2.46× CoT generated tokens); coherence loss in long
  debates (adding debaters hurt); the LLM judge favours the negative side and debaters from its own model
  family. (assessment) CIAR is small and built by the authors. Self-consistency at matched token budget
  is not reported, and the gains are shown mainly for GPT-3.5-class models.
- **Code availability:** https://github.com/Skytliang/Multi-Agents-Debate (linked from arXiv)
- **Unresolved research gaps:** Calibrating disagreement intensity automatically; judge bias in
  heterogeneous debates; whether DoT persists in modern reasoning models.

### 6. More Agents Is All You Need

- **Title:** More Agents Is All You Need
- **Authors:** Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, Deheng Ye
- **Venue:** Transactions on Machine Learning Research (TMLR) (source: arXiv Comments field, "Published at
  TMLR")
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2402.05120
- **Core contribution:** Shows that plain sampling-and-voting ("Agent Forest") scales performance with
  the number of agent instances, and that it is orthogonal to, and stackable with, CoT, debate and other
  methods. The size of the gain depends on task difficulty.
- **Methodology:** Up to 40 sampled agents (averaged over 10 runs), majority vote. For code, voting uses
  BLEU similarity. Combined with debate up to 10 agents. ANOVA across ensemble sizes. A difficulty
  analysis covers inherent difficulty, number of steps and prior probability.
- **Datasets/benchmarks:** GSM8K, MATH, MMLU, BIG-bench Chess state tracking, HumanEval.
- **Evaluation metrics:** Accuracy (mean ± s.e.), relative gain, token usage, ANOVA p-values.
- **Limitations:** (stated) Token cost grows linearly with agents; debate capped at 10 agents because of
  communication overhead; debate hurt HumanEval for Llama2 models; diminishing returns at very high
  difficulty; sampling-cost reduction left to future work. (assessment) The title overstates the claim:
  this is self-consistency at scale rather than coordination among agents. That makes it an essential
  equal-compute baseline for any MAS paper.
- **Code availability:** https://github.com/MoreAgentsIsAllYouNeed/AgentForest (linked from arXiv)
- **Unresolved research gaps:** Cost-aware early stopping for voting; voting for open-ended outputs
  without a reliable similarity metric.

### 7. Mixture-of-Agents (MoA)

- **Title:** Mixture-of-Agents Enhances Large Language Model Capabilities
- **Authors:** Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, James Zou
- **Venue:** ICLR 2025 (proceedings.iclr.cc entry; poster)
- **Year:** 2024 (arXiv); 2025 (ICLR)
- **Link:** https://arxiv.org/abs/2406.04692 ; https://proceedings.iclr.cc/paper_files/paper/2025/hash/5434be94e82c54327bb9dcaf7fca52b6-Abstract-Conference.html
- **Core contribution:** A layered architecture in which each layer's agents (different LLMs) read all
  the previous layer's outputs as auxiliary input and an aggregator synthesises the result. The paper
  reports a "collaborativeness" effect: models write better responses when shown other models' outputs.
- **Methodology:** 3 layers of 6 open-source proposers (Qwen1.5-110B/72B, WizardLM-8x22B,
  LLaMA-3-70B, Mixtral-8x22B, dbrx) with a Qwen1.5-110B aggregator; MoA-Lite (2 layers); a variant
  with GPT-4o as aggregator.
- **Datasets/benchmarks:** AlpacaEval 2.0 (805 instructions), MT-Bench, FLASK.
- **Evaluation metrics:** Length-controlled and raw win rate (65.1% LC for open-source MoA vs 57.5%
  GPT-4o), MT-Bench score, FLASK skill scores, cost per instance, TFLOPs.
- **Limitations:** (stated) High time-to-first-token, because no token can be emitted until the last
  layer finishes. (assessment) All three benchmarks are judged by LLMs, and judge preference for
  longer, more synthesised answers may inflate results. The paper does not evaluate reasoning or agentic
  tasks with verifiable answers, and the comparison is against single models rather than
  matched-compute sampling.
- **Code availability:** https://github.com/togethercomputer/moa (linked in the paper)
- **Unresolved research gaps:** Whether MoA gains survive verifiable-answer benchmarks; selecting
  proposers adaptively; how much proposer diversity matters relative to proposer count.

---

## C. Critiques and scaling studies

### 8. Should we be going MAD?

- **Title:** Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs
- **Authors:** Andries Smit, Paul Duckworth, Nathan Grinsztajn, Thomas D. Barrett, Arnu Pretorius
  (arXiv order. The PMLR page lists "Andries Petrus Smit, Nathan Grinsztajn, Paul Duckworth, ...".)
- **Venue:** ICML 2024 (PMLR 235:45883–45905; https://proceedings.mlr.press/v235/smit24a.html)
- **Year:** 2023 (arXiv); 2024 (ICML)
- **Link:** https://arxiv.org/abs/2311.17371
- **Core contribution:** A systematic benchmark of debate protocols (Society of Minds, Multi-Persona,
  ChatEval variants, Ensemble Refinement) against self-consistency, Medprompt-style ensembling and
  single-agent prompting. Debate does **not** reliably beat these simpler multi-call baselines. Debate is
  highly hyperparameter-sensitive, and controlling "agreement intensity" can rescue it.
- **Methodology:** gpt-3.5-turbo agents (spot checks with GPT-4 and Mixtral 8x7B on MedQA). Cost, time
  and token accounting for each protocol. Analysis at the debate level and the agent level.
- **Datasets/benchmarks:** MedQA, PubMedQA, MMLU clinical topics, CosmosQA, CIAR, GPQA, Chess state
  tracking.
- **Evaluation metrics:** Accuracy, USD cost, time per question, API calls, tokens, consensus and
  answer-change statistics.
- **Limitations:** (stated) Reliance on a proprietary API (silent model updates, variable latency); cost
  limits scale and replication. (assessment) Mostly a single base model; benchmarks skew toward
  medical QA.
- **Code availability:** https://github.com/instadeepai/DebateLLM (linked in the paper)
- **Unresolved research gaps:** Robust debate protocols that need no per-task tuning; theory of when
  agreement or disagreement pressure helps.

### 9. Debate or Vote

- **Title:** Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?
- **Authors:** Hyeong Kyu Choi, Xiaojin Zhu, Sharon Li
- **Venue:** NeurIPS 2025 (spotlight; source: arXiv Comments field)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2508.17536
- **Core contribution:** Splits multi-agent debate into majority voting and inter-agent communication,
  and finds that **voting accounts for most of the gain**. Models debate as a stochastic process whose
  belief trajectory is a martingale, so debate alone does not raise expected correctness. Shows that
  interventions biasing updates toward correction can help.
- **Methodology:** N = 5 agents, T ∈ {2, 3, 5} rounds (voting = T = 0). Qwen2.5-7B, Llama3.1-8B, and
  Qwen2.5-32B on a subset of tasks. Theoretical analysis plus empirical checks of the martingale.
- **Datasets/benchmarks:** Arithmetics, GSM8K, MMLU Professional Medicine, MMLU Formal Logic, HellaSwag,
  CommonsenseQA, HH-RLHF; CNN/DailyMail as an extra experiment.
- **Evaluation metrics:** Accuracy; ROUGE-1/L (summarisation); mean per-agent accuracy across rounds.
- **Limitations:** (stated) Mainly the simultaneous-talk protocol; theory assumes homogeneous agents.
  (assessment) Models of 32B parameters or smaller only; frontier and reasoning models are not tested.
- **Code availability:** https://github.com/deeplearning-wisc/debate-or-vote (linked from arXiv)
- **Unresolved research gaps:** Martingale analysis for heterogeneous agents and sequential protocols;
  designing communication with provably positive drift.

### 10. Scaling LLM-based Multi-Agent Collaboration (MacNet)

- **Title:** Scaling Large Language Model-based Multi-Agent Collaboration
- **Authors:** Chen Qian, Zihao Xie, YiFei Wang, et al.
- **Venue:** ICLR 2025 (source: arXiv Comments field, "Accepted to ICLR-2025")
- **Year:** 2024 (arXiv); 2025 (ICLR)
- **Link:** https://arxiv.org/abs/2406.07155
- **Core contribution:** Organises agents as a DAG (an actor on each node, a critic on each edge) and
  scales to 1,000+ agents. Reports a logistic "collaborative scaling law" and finds that irregular
  topologies beat regular ones.
- **Methodology:** Six topologies (chain, star, tree, mesh, layered/MLP-like, random) with node counts
  from 2^0 to 2^6. Topological-order interaction and memory control. GPT-3.5 backbone (the authors say
  open-source models show a similar pattern).
- **Datasets/benchmarks:** MMLU, HumanEval, SRDD, CommonGen-Hard.
- **Evaluation metrics:** Accuracy, pass@k, the SRDD composite (completeness/executability/consistency),
  the CommonGen-Hard composite, an average "quality" score.
- **Limitations:** (stated) The scaling fit uses network scale only; fitted parameters are specific to
  each topology; "limits on the scaling horizon". (assessment) Agent count and token count are
  confounded, and there is no matched-token single-agent or voting baseline. The "law" is a sigmoid fit
  on four benchmarks with one backbone.
- **Code availability:** https://github.com/OpenBMB/ChatDev/tree/macnet (linked from arXiv)
- **Unresolved research gaps:** Scaling laws that use compute rather than agent count as the
  independent variable; replication with modern models (contrast entry 11).

### 11. Towards a Science of Scaling Agent Systems

- **Title:** Towards a Science of Scaling Agent Systems
- **Authors:** Yubin Kim, Ken Gu, Chanwoo Park, et al. (20 authors listed on arXiv)
- **Venue:** arXiv preprint
- **Year:** 2025 (v1 Dec 2025; v3 Apr 2026)
- **Link:** https://arxiv.org/abs/2512.08296
- **Core contribution:** A controlled study across 260 configurations (single-agent vs Independent,
  Centralized, Decentralized and Hybrid MAS; three model families; six agentic benchmarks) with tools,
  prompts and compute standardised. Fits a predictive model of MAS benefit. The headline findings:
  coordination returns diminish once the single-agent baseline is strong; tool-heavy tasks pay a
  coordination overhead; architectures without centralised verification amplify errors. Results range
  from +80.8% on decomposable financial reasoning to −70.0% on sequential planning.
- **Methodology:** Controlled factorial experiments; regression on system and task factors (cross-validated
  R² 0.373, or 0.413 with a task-grounded capability metric); leave-one-dataset-out validation picks the
  best architecture in 87% of held-out configurations.
- **Datasets/benchmarks:** BrowseComp-Plus, Finance-Agent, PlanCraft, WorkBench, SWE-bench Verified,
  Terminal-Bench.
- **Evaluation metrics:** Task success, factual error rate, information gain, success per 1k tokens,
  coordination overhead, message density, redundancy, error amplification, cross-validated R².
- **Limitations:** (stated) At most nine agents; homogeneous agents (a small heterogeneous test found no
  bypass of saturation); prompts not tuned per architecture; 20-instance subsets for SWE-bench
  Verified and Terminal-Bench (about ±20-point CIs); only six dataset clusters, so dataset-level effects
  are descriptive. (assessment) R² ≈ 0.4 means most of the variance is unexplained; not yet peer
  reviewed.
- **Code availability:** https://github.com/ybkim95/agent-scaling (stated in the v3 paper)
- **Unresolved research gaps:** Coordination protocols built for tool-heavy tasks; better predictors of
  when MAS helps; scaling past nine agents under controlled compute.

### 12. Single-agent vs MAS under equal thinking budgets

- **Title:** Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking
  Token Budgets
- **Authors:** Dat Tran, Douwe Kiela
- **Venue:** arXiv preprint
- **Year:** 2026
- **Link:** https://arxiv.org/abs/2604.02460
- **Core contribution:** Argues from the Data Processing Inequality that a single agent with perfect
  context use is more information-efficient than a MAS at a fixed reasoning-token budget. Confirms
  empirically that single-agent systems match or beat five MAS architectures when thinking tokens are
  held equal. Identifies budget-control artifacts (notably in the Gemini 2.5 API) and benchmark artifacts
  that can inflate reported MAS gains.
- **Methodology:** Matched global thinking budgets from 100 to 10k tokens, split across MAS steps or
  roles. Architectures: SAS, SAS with an analysis scaffold, sequential, subtask-parallel, parallel-roles,
  debate, ensemble. Qwen3-30B-A3B, DeepSeek-R1-Distill-Llama-70B, Gemini 2.5 Flash/Pro.
- **Datasets/benchmarks:** FRAMES; MuSiQue (4-hop subset).
- **Evaluation metrics:** LLM-judge accuracy with a shared rubric; 95% bootstrap CIs; thinking tokens
  used.
- **Limitations:** (stated) Text-only multi-hop QA (no tools, vision or safety settings); Gemini token
  accounting is approximate; only the upper budget cap is enforced. (assessment) Two benchmarks; an
  LLM judge; tool-using agentic tasks, where parallelism may matter most, are excluded.
- **Code availability:** not verified (no repository link found on the arXiv page)
- **Unresolved research gaps:** Equal-budget comparisons on tool-using, long-horizon tasks; the theory
  of when context degradation makes decomposition worthwhile.

---

## D. Automated design, topology, routing and orchestration

### 13. GPTSwarm

- **Title:** Language Agents as Optimizable Graphs
- **Authors:** Mingchen Zhuge, Wenyi Wang, Louis Kirsch, Francesco Faccio, Dmitrii Khizbullin, Jürgen
  Schmidhuber
- **Venue:** ICML 2024 (source: arXiv Comments field, "In Forty-first International Conference on Machine
  Learning (2024)")
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2402.16823
- **Core contribution:** Unifies prompting techniques and multi-agent systems as computational graphs
  (nodes are LLM calls or operations; edges are information flow; graphs can be nested into "swarms").
  Introduces automatic optimisation of node prompts and of inter-agent edge connectivity.
- **Methodology:** Edge optimisation treats graph connectivity as a parameterised distribution over DAGs,
  trained with REINFORCE. Node optimisation iteratively improves each node's prompt from its I/O history.
- **Datasets/benchmarks:** MMLU (including adversarial-agent settings), Mini Crosswords (20), HumanEval,
  GAIA.
- **Evaluation metrics:** Accuracy, pass rate, word accuracy, USD cost, tokens, wall-clock time.
- **Limitations:** (stated) Optimises inter-agent edges, not intra-agent structure; efficiency and
  robustness become a challenge beyond ~100 agents; GAIA runs used no optimisation; limited runs
  because of API cost. (assessment) Small evaluation sets (e.g., 20 crosswords), and the optimised
  graph is fixed for every query after training.
- **Code availability:** https://github.com/metauto-ai/gptswarm (linked from arXiv)
- **Unresolved research gaps:** Query-adaptive graphs (taken up by entries 16, 18); joint optimisation of
  intra- and inter-agent structure.

### 14. ADAS (Meta Agent Search)

- **Title:** Automated Design of Agentic Systems
- **Authors:** Shengran Hu, Cong Lu, Jeff Clune
- **Venue:** ICLR 2025 (source: ICLR 2025 virtual poster page, iclr.cc/virtual/2025/poster/28073)
- **Year:** 2024 (arXiv); 2025 (ICLR)
- **Link:** https://arxiv.org/abs/2408.08435
- **Core contribution:** Frames agent design as a search over *code*. In "Meta Agent Search", a meta
  agent (GPT-4) writes new agent programs, evaluates them, and adds them to a growing archive. The
  discovered agents beat hand-designed baselines and transfer across domains and models.
- **Methodology:** Iterative program generation conditioned on the archive; discovered agents executed
  with GPT-3.5; transfer to Claude-3 Haiku, GPT-4o and Claude-3.5 Sonnet.
- **Datasets/benchmarks:** ARC (small grids), DROP, MGSM, MMLU, GPQA; transfer to GSM8K, GSM-Hard,
  SVAMP, ASDiv.
- **Evaluation metrics:** Accuracy with 95% bootstrap CIs; F1 for DROP; median of 5 runs on ARC.
- **Limitations:** (stated) Single-step QA only, not interactive environments; a single objective; one
  domain per search; a simple search algorithm; inefficient from scratch; safety risk from executing
  model-written code (sandboxing recommended). (assessment) The search cost is not charged against the
  discovered agent in comparisons. Test sets are small (e.g., 60 ARC test items), which raises overfitting
  concerns for archive-guided search.
- **Code availability:** https://github.com/ShengranHu/ADAS (linked in the paper)
- **Unresolved research gaps:** Multi-objective (cost, safety) ADAS; ADAS on interactive and agentic
  benchmarks; held-out evaluation protocols that resist search overfitting.

### 15. AFlow

- **Title:** AFlow: Automating Agentic Workflow Generation
- **Authors:** Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, et al.
- **Venue:** ICLR 2025 (oral; proceedings.iclr.cc entry and iclr.cc/virtual/2025/oral/31731)
- **Year:** 2024 (arXiv); 2025 (ICLR)
- **Link:** https://arxiv.org/abs/2410.10762
- **Core contribution:** Recasts workflow optimisation as Monte Carlo Tree Search over code-represented
  workflows built from reusable "operators" (Generate, Review & Revise, Ensemble, Test, Programmer,
  etc.). It reports a 5.7% average improvement over baselines, and smaller models beating GPT-4o on some
  tasks at 4.55% of the cost.
- **Methodology:** MCTS with LLM-driven code modification, tree-structured experience and execution
  feedback; Claude-3.5-Sonnet as optimiser; several executor models.
- **Datasets/benchmarks:** HumanEval, MBPP, GSM8K, MATH (level-5 subset), HotpotQA, DROP.
- **Evaluation metrics:** Solve rate, pass@1, F1, token cost (Pareto fronts).
- **Limitations:** (stated) Scoped to reasoning tasks with numerical evaluation functions; workflows
  found with one executor transfer poorly to another. (assessment) Needs a labelled validation set and
  a cheap automatic scorer, so it does not apply directly to open-ended or long-horizon agentic tasks.
  Search cost is amortised but not always charged.
- **Code availability:** https://github.com/FoundationAgents/AFlow (linked from arXiv)
- **Unresolved research gaps:** Workflow search with noisy or LLM-judged rewards; workflows that
  transfer across executors.

### 16. G-Designer

- **Title:** G-Designer: Architecting Multi-agent Communication Topologies via Graph Neural Networks
- **Authors:** Guibin Zhang, Yanwei Yue, Xiangguo Sun, et al.
- **Venue:** ICML 2025 (PMLR 267:76678–76692; https://proceedings.mlr.press/v267/zhang25cu.html;
  spotlight per icml.cc virtual page)
- **Year:** 2024 (arXiv); 2025 (ICML)
- **Link:** https://arxiv.org/abs/2410.11782
- **Core contribution:** Generates a *task-specific* communication topology for each query with a
  variational graph auto-encoder over agent nodes plus a task "virtual node". It cuts tokens by up to
  95.33% on HumanEval while matching or beating fixed topologies, and resists adversarial agents.
- **Methodology:** Agent profiles and the query are encoded (MiniLM); the VGAE decodes a sparse
  topology anchored to a simple chain; the topology is trained with policy gradient on 40–80 queries.
- **Datasets/benchmarks:** MMLU, GSM8K, MultiArith, SVAMP, AQuA, HumanEval.
- **Evaluation metrics:** Accuracy, pass@1, prompt tokens, wall-clock time, GPU memory.
- **Limitations:** (stated, implicit; no dedicated section) Sub-optimal chain anchor; non-differentiable
  utility requires policy-gradient approximation; small training subsets. (assessment) Benchmarks are
  short-answer reasoning sets where the single-agent baselines are already strong. Gains over CoT and
  self-consistency are modest relative to the topology machinery.
- **Code availability:** https://github.com/yanweiyue/GDesigner (linked in the paper)
- **Unresolved research gaps:** Topology design for long-horizon and tool-using tasks; whether learned
  topologies transfer across model families.

### 17. AgentPrune

- **Title:** Cut the Crap: An Economical Communication Pipeline for LLM-based Multi-Agent Systems
- **Authors:** Guibin Zhang, Yanwei Yue, Zhixun Li, et al.
- **Venue:** ICLR 2025 (proceedings.iclr.cc entry; poster)
- **Year:** 2024 (arXiv); 2025 (ICLR)
- **Link:** https://arxiv.org/abs/2410.02506
- **Core contribution:** Defines *communication redundancy* in MAS and performs one-shot pruning of the
  spatial-temporal message-passing graph. It matches state-of-the-art topologies at $5.6 vs $43.7,
  cuts tokens by 28.1–72.8% when plugged into AutoGen and GPTSwarm, and improves robustness to agent
  attacks.
- **Methodology:** Learnable masks on spatial (intra-round) and temporal (inter-round) edges, followed
  by one-shot magnitude pruning; plug-in integration with existing frameworks.
- **Datasets/benchmarks:** MMLU, GSM8K, MultiArith, SVAMP, AQuA, HumanEval.
- **Evaluation metrics:** Accuracy / pass@1, prompt and completion tokens, USD cost; accuracy under
  agent-prompt and agent-replacement attacks.
- **Limitations:** (stated) not verified (no limitations section found in the portion of the paper
  read). (assessment) Same short-answer benchmark suite as G-Designer, so it is unclear whether pruning
  remains safe when messages carry state that later steps need.
- **Code availability:** https://github.com/yanweiyue/AgentPrune (linked in the paper)
- **Unresolved research gaps:** Pruning under long-horizon dependencies; communication compression
  beyond dropping edges (summarisation, latent messages).

### 18. MasRouter

- **Title:** MasRouter: Learning to Route LLMs for Multi-Agent Systems
- **Authors:** Yanwei Yue, Guibin Zhang, Boyang Liu, Guancheng Wan, Kun Wang, Dawei Cheng, Yiyan Qi
- **Venue:** ACL 2025 (Long Papers; aclanthology.org/2025.acl-long.757)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2502.11133 ; https://aclanthology.org/2025.acl-long.757
- **Core contribution:** Defines Multi-Agent System Routing (MASR): jointly choosing the collaboration
  mode, the agent roles, and which LLM backs each agent. A cascaded controller network solves it,
  improving MBPP over the prior state of the art, cutting HumanEval cost by up to 52.07%, and reducing
  overhead by 17.21–28.17% as a plug-in.
- **Methodology:** A three-stage cascaded controller (mode → roles → LLM routing) trained on a
  utility-minus-λ·cost objective; the LLM pool is gpt-4o-mini, claude-3.5-haiku, gemini-1.5-flash and
  llama-3.1-70b; generalisation tested on unseen DeepSeek-V3.
- **Datasets/benchmarks:** MMLU, GSM8K, MATH (519 sampled), HumanEval, MBPP.
- **Evaluation metrics:** Accuracy / pass@1, USD per query, training tokens.
- **Limitations:** (stated) not verified as a dedicated section; the authors report only marginal
  gains from raising the agent cap from 6 to 10, at ~1.5× cost. (assessment) A small, fixed LLM pool;
  short-answer benchmarks; router training needs labelled task data.
- **Code availability:** https://github.com/yanweiyue/masrouter (linked from arXiv)
- **Unresolved research gaps:** Online and continual routing as model pools change; routing for
  agentic, tool-using MAS.

### 19. Puppeteer (evolving orchestration)

- **Title:** Multi-Agent Collaboration via Evolving Orchestration
- **Authors:** Yufan Dang, Chen Qian, Xueheng Luo, et al.
- **Venue:** NeurIPS 2025 (source: arXiv Comments field, "accepted at NeurIPS 2025")
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2505.19591
- **Core contribution:** A "puppeteer" orchestrator, trained with RL, dynamically chooses which agent
  acts next as the task state changes, replacing static organisation. The authors report better quality
  at lower cost, which they attribute to more compact, cyclic reasoning structures emerging.
- **Methodology:** REINFORCE on a reward combining solution quality and a token/FLOPs cost penalty; the
  orchestrator policy is initialised from a Llama-3.1-based model; agent pools of small ("Mimas") and
  large ("Titan") models.
- **Datasets/benchmarks:** GSM-Hard, MMLU-Pro (closed-domain); SRDD, CommonGen-Hard (open-domain);
  ALFWorld (appendix).
- **Evaluation metrics:** Accuracy; the SRDD and CommonGen-Hard composite scores; tokens and number of
  agents per trajectory; performance-to-cost ratio.
- **Limitations:** (stated) Reward only on final outputs and tokens, with no step-level credit; fixed
  agent and tool set; agents can mis-coordinate or agree superficially. (assessment) The open-domain
  metrics are LLM-scored composites. No equal-compute single-agent baseline with a strong reasoning
  model is reported.
- **Code availability:** https://github.com/OpenBMB/ChatDev/tree/puppeteer (linked from arXiv)
- **Unresolved research gaps:** Step-level credit assignment for orchestrators (links to entry 21);
  orchestrators that add or remove agents and tools at run time.

---

## E. Failure analysis

### 20. MAST — Why Do Multi-Agent LLM Systems Fail?

- **Title:** Why Do Multi-Agent LLM Systems Fail?
- **Authors:** Mert Cemri, Melissa Z. Pan, Shuyi Yang, et al.
- **Venue:** NeurIPS 2025 (spotlight poster, per neurips.cc/virtual/2025/poster/121528; main vs
  Datasets & Benchmarks track: not verified)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2503.13657
- **Core contribution:** The first empirically grounded failure taxonomy for MAS (MAST): 14 failure
  modes in 3 categories (system design issues; inter-agent misalignment; task verification). It is built
  from traces of 7 frameworks (MetaGPT, ChatDev, HyperAgent, AppWorld, AG2/MathChat, Magentic-One,
  OpenManus) and released with MAST-Data (1,642 annotated traces) and an LLM-as-judge annotator.
- **Methodology:** Grounded-theory coding of 150+ traces until human agreement reached Cohen's κ = 0.88.
  An o1-based few-shot annotator (94% accuracy, κ = 0.77 vs humans) scales the labelling. Two
  intervention case studies on ChatDev (role/workflow changes: about +9.4%; adding objective
  verification: about +15.6%).
- **Datasets/benchmarks:** ProgramDev(-v2), SWE-Bench Lite, AppWorld Test-C, GSM-Plus, OlympiadBench,
  MMLU, GAIA.
- **Evaluation metrics:** Failure-mode frequencies, inter-annotator κ, annotator accuracy, task success
  before and after intervention.
- **Limitations:** (stated) Not exhaustive; does not separate base-LLM failures such as hallucination;
  failure modes are correlated (up to 0.63), so the annotator may conflate them; the LLM annotator is
  weaker than humans; closed systems are excluded. (assessment) The taxonomy describes symptoms, not
  causes, and the interventions leave completion rates low, so MAST diagnoses without yet prescribing.
- **Code availability:** https://github.com/multi-agent-systems-failure-taxonomy/MAST ; dataset
  https://huggingface.co/datasets/mcemri/MAST-Data (both linked in the paper)
- **Unresolved research gaps:** Causal (rather than descriptive) failure analysis; design patterns,
  especially verification, that measurably remove specific MAST modes.

### 21. Who&When — automated failure attribution

- **Title:** Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM
  Multi-Agent Systems
- **Authors:** Shaokun Zhang, Ming Yin, Jieyu Zhang, et al.
- **Venue:** ICML 2025 (PMLR 267:76583–76599; https://proceedings.mlr.press/v267/zhang25cq.html)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2505.00212
- **Core contribution:** Defines *automated failure attribution* (identify the responsible agent and
  the decisive error step in a failed MAS run) and releases the Who&When benchmark. The best method
  reaches only 53.5% agent-level and 14.2% step-level accuracy, and o1 / DeepSeek-R1 do not reliably
  help.
- **Methodology:** Failure logs from 126 CaptainAgent-generated systems (AG2) and the hand-crafted
  Magentic-One, on GAIA and AssistantBench tasks (184 annotated failures). Three LLM-judge strategies are
  compared: all-at-once, step-by-step, binary search (plus a hybrid).
- **Datasets/benchmarks:** Who&When (introduced), built on GAIA and AssistantBench.
- **Evaluation metrics:** Agent-level accuracy, step-level accuracy, step accuracy with tolerance, token
  cost.
- **Limitations:** (stated, from findings) Accuracy falls toward zero on long logs; some methods are
  below random at step level; annotation is costly (23–31 h per annotator) and 15–30% of labels were
  uncertain; generated logs are capped at about 10 steps. (assessment) A single root-cause step is a
  strong assumption when failures are distributed across agents.
- **Code availability:** https://github.com/mingyin1/Agents_Failure_Attribution (linked from arXiv)
- **Unresolved research gaps:** Counterfactual or replay-based attribution; attribution for long traces;
  using attribution as a training signal for orchestrators.

---

## F. Bridging to classical MAS

### 22. Symbolic guidance for distributed coordination

- **Title:** Symbolic Guidance for LLM Agents in Distributed Multiagent Coordination
- **Authors:** Ben Rachmut, Ning Zhang, Yevgeniy Vorobeychik, William Yeoh
- **Venue:** arXiv preprint (authors state: "A preliminary version of this work was published as an
  extended abstract in the Proceedings of AAMAS 2026")
- **Year:** 2026
- **Link:** https://arxiv.org/abs/2609.31963
- **Core contribution:** Brings classical distributed algorithms into LLM-agent coordination. Defines a
  Symbolic Guidance Taxonomy, from free natural-language reasoning through partial pseudocode to fully
  prescribed algorithm execution, and finds that **intermediate autonomy** beats both unguided LLM
  agents and fully prescriptive specifications.
- **Methodology:** Each graph node is an LLM agent communicating with its neighbours. Guidance comes from
  a Maximal Independent Set heuristic (local) and distributed DFS (global). Models: Llama-3.1-8B,
  Qwen-2.5-7B, Gemini-2.5 Flash. 16-node Small-world, Scale-free and Delaunay graphs.
- **Datasets/benchmarks:** Tasks derived from AgentsNet: (Δ+1)-colouring, maximal matching, minimal
  vertex cover (local); 3-colouring, maximum matching, minimum vertex cover (global).
- **Evaluation metrics:** ln(1 + SSE) relative to feasibility or optimality (mean ± SEM); success rate.
- **Limitations:** (stated, informal; no dedicated section) Small open models solved almost no local
  instances; the oracle baseline was round-capped; only three models and 16-node graphs. (assessment)
  The tasks are synthetic graph problems. Transfer to open-ended LLM workflows is untested.
- **Code availability:** https://github.com/YODA-Lab/Symbolic-Guidance-Taxonomy (linked in the paper)
- **Unresolved research gaps:** Mapping classical protocols (contract net, DCOP solvers, auctions) onto
  LLM orchestration of real tasks; adaptive autonomy levels.

---

## G. Grey literature (not peer reviewed)

### G1. Anthropic engineering blog — orchestrator-worker research system

- **Title:** How we built our multi-agent research system
- **Authors:** Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, Daniel Ford
- **Venue:** Anthropic Engineering blog (**non-peer-reviewed**)
- **Year:** 2025 (June 13, 2025)
- **Link:** https://www.anthropic.com/engineering/multi-agent-research-system
- **Core contribution:** A practitioner account of a lead agent plus parallel subagents (plus a citation
  agent) for open-ended research. Claims: +90.2% over single-agent Opus 4 on an *internal* research
  eval; token usage explains ~80% of variance on BrowseComp (95% with tool calls and model choice);
  multi-agent runs use ~15× the tokens of chat.
- **Methodology / datasets / metrics:** Internal evaluation set; BrowseComp variance analysis;
  LLM-judge rubric (per the post). Details are not sufficient for replication.
- **Limitations:** (stated) Expensive, so justified only for high-value tasks; poor fit for tasks needing
  shared context or with heavy interdependencies (including most coding); synchronous subagent execution
  is a bottleneck; error compounding and nondeterministic debugging. (assessment) The internal eval is not
  public. The token-variance finding implies the gain is largely compute, consistent with entries 9, 11
  and 12.
- **Code availability:** not applicable / none linked
- **Unresolved research gaps:** A public, equal-compute replication of the orchestrator-worker
  advantage for breadth-first research tasks.

---

## Verified but not profiled (excluded to stay within the 15–22 target)

All checked on primary pages, listed so the paper can cite them if needed:

- ChatDev: Communicative Agents for Software Development — Qian et al., ACL 2024 (arXiv Comments) —
  https://arxiv.org/abs/2307.07924
- AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors — Chen et al.,
  ICLR 2024 (proceedings.iclr.cc) — https://arxiv.org/abs/2308.10848
- Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key? — Wang et al., ACL 2024
  (aclanthology 2024.acl-long.331) — https://arxiv.org/abs/2402.18272 (a single agent with strong prompts
  ≈ the best discussion method; MAS wins only without demonstrations)
- Multi-agent Architecture Search via Agentic Supernet (MaAS) — Zhang et al., ICML 2025 oral (PMLR 267)
  — https://arxiv.org/abs/2502.04180
- Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents (GovSim) —
  Piatti et al., NeurIPS 2024 (arXiv Comments; neurips.cc poster) — https://arxiv.org/abs/2404.16698
- LLM-Coordination: Evaluating and Analyzing Multi-agent Coordination Abilities in Large Language Models
  — Agashe et al., venue not verified — https://arxiv.org/abs/2310.03903
- When Single-Agent with Skills Replace Multi-Agent Systems and When They Fail — Xiaoxiao Li, arXiv
  preprint (technical report), 2026 — https://arxiv.org/abs/2601.04748

---

## Recurring weaknesses in this slice *(my assessment)*

1. **No equal-compute baseline.** Many MAS papers compare against a single call or single-shot prompting
   rather than self-consistency or majority voting at the same token budget. When that control is
   applied, most of the gain disappears or turns out to come from voting. Applies to: CAMEL (1), AutoGen
   (2), MetaGPT (3), Du (4), Liang (5), MoA (7), MacNet (10), Puppeteer (19). The critique comes from:
   Smit (8), Choi (9), Tran & Kiela (12), Kim (11), and More Agents (6), which supplies the baseline
   itself.
2. **Saturated, short-answer benchmarks.** Topology, routing and pruning papers reuse the same suite
   (MMLU, GSM8K, MultiArith, SVAMP, AQuA, HumanEval), where single strong models already score high and
   inter-agent state is trivial. Results may not carry over to long-horizon, tool-heavy settings, where
   Kim (11) finds MAS overhead is worst. Applies to: G-Designer (16), AgentPrune (17), MasRouter (18),
   GPTSwarm (13), AFlow (15), ADAS (14).
3. **Search and training cost left out of comparisons.** Automated design methods amortise expensive
   search or controller training over evaluation and compare only per-query inference cost, on small
   test sets that risk overfitting. Applies to: ADAS (14), AFlow (15), GPTSwarm (13), G-Designer (16),
   MasRouter (18), Puppeteer (19).
4. **LLM-as-judge evaluation without bias controls.** Win rates, composite quality scores and even
   failure labels come from LLM judges, and documented self- or same-family preference is rarely
   corrected for. Applies to: CAMEL (1), Liang (5), MoA (7), MacNet (10), Puppeteer (19), Tran & Kiela
   (12), MAST (20), G1.
5. **Agent count confounded with compute.** "Scaling" results plot performance against the number of
   agents while total tokens grow with it, so collaboration and compute cannot be told apart. Applies
   to: MacNet (10), More Agents (6), Du (4), G1. Kim (11) and Tran & Kiela (12) are the exceptions that
   control for this.
6. **Homogeneous agents and old or small models.** Theory and experiments often assume identical
   agents, and many results come from GPT-3.5-era or ≤32B models. It is unclear whether findings hold for
   current reasoning models or for heterogeneous teams. Applies to: Du (4), Liang (5), Smit (8), Choi (9),
   MacNet (10), Kim (11; stated), Rachmut (22).
7. **Diagnosis without remedy.** Failure studies show that verification and coordination failures
   dominate, but the fixes they test give modest gains, and attribution accuracy at step level is near
   unusable. Applies to: MAST (20), Who&When (21); the same failure symptoms are acknowledged in CAMEL
   (1), AutoGen (2) and G1.

## Open problems that a small team could attack *(my assessment)*

1. **An equal-compute MAS evaluation harness.** Build a small, open harness that reruns 4–6 published
   MAS methods (debate, MoA, AFlow-found workflows, G-Designer, a simple orchestrator-worker) against
   self-consistency and best-of-N *at matched token budgets*. Run it on 2–3 tool-using benchmarks, not
   only MMLU/GSM8K. This directly tests entries 4, 7, 15, 16 and 19 using the methodology of 11–12, and
   needs only API budget and open code.
2. **Verification-first orchestration.** MAST (20) and Kim (11) both point to missing or weak
   verification as a dominant failure source. A focused study could ask whether adding one dedicated
   verifier agent, or a programmatic checker, to an orchestrator-worker system removes specific MAST
   modes, measured with the released MAST annotator.
3. **Cheap failure attribution via replay.** Who&When (21) shows that LLM-judge attribution fails on
   long logs. Counterfactual replay could do better: re-run a trace from step k with one agent's message
   corrected, then check whether the outcome flips. The benchmark and code are public, and the method is
   embarrassingly parallel.
4. **Predicting when to go multi-agent.** Kim's predictor explains about 40% of variance (11). A small
   team could add cheap pre-execution task features, such as decomposability, tool density and the
   single-agent pass rate on a few probes, and test whether a lightweight router choosing "single vs
   multi" beats always-MAS and always-single on cost-adjusted success. This extends MasRouter (18) to
   the more basic choice.
5. **Classical protocols as structured guidance.** Following Rachmut et al. (22), try contract-net-style
   task announcement and bidding, or auction-based allocation, as *partial* guidance for LLM workers on
   real decomposable tasks such as multi-document research. Compare free-form delegation (G1-style)
   with fully scripted workflows.
6. **Debate with positive drift.** Choi et al. (9) prove that vanilla debate is a martingale. Design and
   test a small set of update rules (confidence-weighted, verifier-gated, or dissent-preserving) that
   should give positive expected drift, and check them against voting at equal compute on verifiable
   tasks.

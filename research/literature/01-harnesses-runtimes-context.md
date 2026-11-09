# Slice 01: Agent Harnesses, Runtimes/Serving Systems, Context Engineering and State Management

*Compiled 2026-11-08. Every entry below was checked against a primary source page (arxiv.org/abs or arXiv HTML, proceedings.neurips.cc, proceedings.mlr.press, proceedings.iclr.cc, aclanthology.org, usenix.org, or the FSE/researchr program). A venue appears only where acceptance was confirmed (proceedings page, or the arXiv comment / journal-ref field saying "accepted at X"); everything else is labelled "arXiv preprint". Fields I could not check are marked "not verified".*

## Scope

This slice covers the software *around* the model: (a) **harnesses**, meaning the loop, action format and agent-computer interface that turn an LLM into an agent (ReAct, SWE-agent, CodeAct, OpenHands), plus studies showing that the choice of scaffold alone moves benchmark scores (SWE-agent ablations, Agentless, HAL). (b) **Runtimes and serving systems** that schedule, batch and cache many dependent LLM calls from agent programs (AIOS, SGLang, Parrot, LLMCompiler, InferCept, Autellix, KVFlow). (c) **Context engineering**: how much context to give, how models degrade as it grows (Lost in the Middle, Context Length Alone Hurts), and how to compress, mask, curate or retrieve it (LLMLingua, The Complexity Trap, ACON, ACE, ToolRet, DSPy as programmatic prompt construction). (d) **State management**: checkpointing and rollback of agent execution state (DeltaBox). Long-term memory architectures belong to the memory slice. MemGPT (Packer et al., arXiv preprint 2310.08560, https://arxiv.org/abs/2310.08560) is noted here only as the origin of the "LLM as OS, context window as paged main memory" framing that AIOS and later context managers build on.

Papers are grouped as: harnesses and scaffold ablations (1–6), runtimes and serving (7–13), programmatic pipelines (14), context degradation (15–16), context compression and curation (17–20), tool-context retrieval (21), state checkpointing (22).

---

## 1. ReAct

- **Title:** ReAct: Synergizing Reasoning and Acting in Language Models
- **Authors:** Shunyu Yao, Jeffrey Zhao, Dian Yu, et al.
- **Venue:** ICLR 2023 (arXiv v3 comment: "ICLR camera ready version")
- **Year:** 2023 (arXiv v1 Oct 2022)
- **Link:** https://arxiv.org/abs/2210.03629
- **Core contribution:** Defines the interleaved *Thought → Action → Observation* loop that nearly every later agent harness builds on. Free-form reasoning traces drive and update tool actions, and tool observations feed back into the reasoning.
- **Methodology:** Few-shot prompting (1–6 exemplars) of a frozen LLM (PaLM-540B main, with GPT-3 comparisons) to emit reasoning and action tokens in an augmented action space. Compared against act-only, CoT-only and CoT-SC, plus hybrid ReAct↔CoT-SC fallbacks. Also small-scale fine-tuning on ReAct trajectories.
- **Datasets/benchmarks:** HotpotQA, FEVER (with a simple Wikipedia API: search/lookup/finish), ALFWorld, WebShop.
- **Evaluation metrics:** Exact match (HotpotQA), accuracy (FEVER), success rate (ALFWorld, WebShop) and WebShop score. Reported gains of +34 and +10 absolute success points over imitation/RL baselines on ALFWorld/WebShop.
- **Limitations:** Complex tasks with large action spaces need more demonstrations than fit in the in-context window (stated). The trajectory grows without bound because every observation is appended verbatim, and there is no context management (assessment). Single-model, prompt-only results on PaLM do not isolate how much the loop format itself contributes compared with model capability (assessment).
- **Code availability:** Project page https://react-lm.github.io (linked from arXiv).
- **Unresolved research gaps:** Principled policies for what to keep in the scratchpad as trajectories lengthen. Whether the textual Thought step still helps with reasoning-trained models. Formal comparison of ReAct against code-action and planner-executor loops at matched budget.

## 2. SWE-agent

- **Title:** SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering
- **Authors:** John Yang, Carlos E. Jimenez, Alexander Wettig, et al.
- **Venue:** NeurIPS 2024 (Main Conference Track; proceedings.neurips.cc)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2405.15793 ; proceedings: https://papers.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html
- **Core contribution:** Introduces the **agent-computer interface (ACI)**: LM-specific commands, feedback formats and guardrails. Shows that interface design, not just the model, decides agent performance.
- **Methodology:** A ReAct-style loop over a custom shell. It has summarized search (`find_file`/`search_file`/`search_dir`, capped at 50 hits), a 100-line windowed file viewer, a line-range `edit` command with a flake8 linter guardrail that rejects syntactically broken edits, and context management that collapses observations older than the last 5 to one line. Systematic ablations of each component.
- **Datasets/benchmarks:** SWE-bench (full and Lite), HumanEvalFix.
- **Evaluation metrics:** % resolved (pass@1). Headline results: 12.47% on SWE-bench full and 18.00% on Lite with GPT-4 Turbo, against 11.00% for a shell-only agent and 2.67% for RAG on Lite. 87.7% on HumanEvalFix (Python).
- **Limitations:** Ablations show large sensitivity to small interface choices. Removing the linter drops Lite from 18.0 to 15.0. A 30-line window gives 14.3 and the full file 12.7. Iterative search (12.0) is worse than no search (15.7) (stated, from their ablation tables). Most remaining failures are wrong or overly specific implementations, and about 23% are cascading failed edits (stated). Interface components were hand-tuned on SWE-bench, so they may overfit that benchmark's repo/issue distribution (assessment). Only two frontier models were tested as agents, and open models (Llama 3, DeepSeek Coder) performed poorly (stated).
- **Code availability:** https://swe-agent.com (linked from arXiv comment).
- **Unresolved research gaps:** Automatic search or learning of ACIs instead of manual design. How ACI choices transfer across models and domains. The observation-collapsing heuristic is itself an untested context-management policy (later probed by #18).

## 3. CodeAct

- **Title:** Executable Code Actions Elicit Better LLM Agents
- **Authors:** Xingyao Wang, Yangyi Chen, Lifan Yuan, et al.
- **Venue:** ICML 2024 (arXiv comment: "Accepted by ICML 2024")
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2402.01030
- **Core contribution:** Replaces JSON/text tool-call formats with **executable Python as the action space**. Code gives control flow, composition of multiple tools in one action, and interpreter error messages as observations for self-debugging.
- **Methodology:** Controlled comparison of 17 LLMs acting via CodeAct vs. JSON vs. text actions. Builds a new benchmark that requires multi-tool composition. Releases CodeActInstruct (7k multi-turn interactions) and fine-tunes CodeActAgent from Llama-2 and Mistral.
- **Datasets/benchmarks:** API-Bank and a newly curated multi-tool benchmark (M3ToolEval). MINT and general LLM benchmarks for the fine-tuned agent.
- **Evaluation metrics:** Task success rate and number of interaction turns. Up to 20% absolute higher success reported for CodeAct.
- **Limitations:** Executing model-written code needs a sandbox, and the security of code actions is not the paper's focus (assessment). Gains are largest for strong code models, so weaker models may not benefit equally (assessment). The new benchmark was built by the authors, which raises the risk of design choices favouring code actions (assessment).
- **Code availability:** https://github.com/xingyaoww/code-act (linked from arXiv).
- **Unresolved research gaps:** Code actions as a context-efficiency mechanism (one action replacing many tool round-trips) has not been measured in tokens or latency. Safety and permissioning for code-as-action. How code actions interact with tool retrieval when the tool library is large.

## 4. OpenHands (formerly OpenDevin)

- **Title:** OpenHands: An Open Platform for AI Software Developers as Generalist Agents
- **Authors:** Xingyao Wang, Boxuan Li, Yufan Song, et al. (24 authors)
- **Venue:** ICLR 2025 (arXiv comment: "Accepted by ICLR 2025")
- **Year:** 2025 (arXiv v1 July 2024)
- **Link:** https://arxiv.org/abs/2407.16741
- **Core contribution:** An open, MIT-licensed agent **harness and runtime platform**. It has an event-stream abstraction (actions, observations, user messages), a Docker-sandboxed runtime (bash, Jupyter IPython, Playwright-driven Chromium), an AgentSkills library, multi-agent delegation, and an integrated evaluation harness.
- **Methodology:** Platform/system paper. The default CodeActAgent (CodeAct action space, #3) and a BrowsingAgent are evaluated across many benchmarks with the same prompts.
- **Datasets/benchmarks:** 15 benchmarks, including SWE-bench (Lite), HumanEvalFix, BIRD, BioCoder, ML-Bench, Gorilla APIBench, ToolQA, WebArena, MiniWoB++, GAIA, GPQA, AgentBench, MINT, Entity Deduction Arena, ProofWriter.
- **Evaluation metrics:** Benchmark-native success/accuracy. Reported results: SWE-bench Lite 26.0% (CodeActAgent v1.8, Claude 3.5 Sonnet), WebArena 15.5%, GAIA L1 32.1%.
- **Limitations:** Agents still struggle with long-horizon tasks and with editing long files. Multimodal inputs need more principled support. Workflows still require substantial hand-crafting (stated). Breadth of benchmarks comes at the cost of depth, with few controlled ablations isolating platform components (assessment). Results are tied to fast-moving agent versions, which hurts reproducibility (assessment).
- **Code availability:** https://github.com/All-Hands-AI/OpenHands (linked from arXiv).
- **Unresolved research gaps:** The event stream is a natural substrate for replay, checkpointing and context condensation, but the paper does not study policies for these. Standardized cost/latency reporting across the 15 benchmarks.

## 5. Agentless

- **Title:** Agentless: Demystifying LLM-based Software Engineering Agents (listed in the FSE 2025 program as "Demystifying LLM-based Software Engineering Agents")
- **Authors:** Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, Lingming Zhang
- **Venue:** FSE 2025 (ACM International Conference on the Foundations of Software Engineering), research track, confirmed on the conf.researchr.org program page
- **Year:** 2025 (arXiv v1 July 2024)
- **Link:** https://arxiv.org/abs/2407.01489 ; program: https://conf.researchr.org/details/fse-2025/fse-2025-research-papers/85/Demystifying-LLM-based-Software-Engineering-Agents
- **Core contribution:** A **harness ablation in the strongest form**. A fixed three-phase pipeline (localize → repair → validate) in which the LLM never chooses its next action matches or beats autonomous agents on SWE-bench at much lower cost.
- **Methodology:** Hierarchical localization (file → class/function over compressed skeletons → edit lines, plus embedding retrieval). About 40 sampled Search/Replace diff patches per issue. LLM-generated reproduction tests plus regression tests for filtering. Majority vote over AST-normalized patches. Manual audit of SWE-bench Lite to build a filtered subset.
- **Datasets/benchmarks:** SWE-bench Lite (300), SWE-bench Lite-S (249, filtered), SWE-bench Verified (500).
- **Evaluation metrics:** % resolved (32.00% Lite, 38.80% Verified with GPT-4o), average $ cost (~$0.70/issue), token usage, and localization accuracy at file/function/line level.
- **Limitations:** Possible training-data leakage of SWE-bench patches into GPT-4o. Results are shown mainly on SWE-bench. Generated reproduction tests are often wrong (94 of 213 pass with the gold patch). About 10% of Lite issues lack enough information to solve. The pipeline is weak when an issue gives no location hint (all stated). The pipeline is hand-specialized to Python bug-fixing, so the "agentless" conclusion may not hold for open-ended tasks (assessment).
- **Code availability:** not verified (no repo linked on the arXiv abstract page).
- **Unresolved research gaps:** When does agentic autonomy pay for its cost compared with a fixed workflow, as a function of task openness? Hybrid designs that let a fixed pipeline call an agent only on hard sub-steps.

## 6. Holistic Agent Leaderboard (HAL)

- **Title:** Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation
- **Authors:** Sayash Kapoor, Benedikt Stroebl, Peter Kirgis, et al. (31 authors)
- **Venue:** ICLR 2026 (proceedings.iclr.cc listing; project site states acceptance)
- **Year:** 2026 (arXiv Oct 2025)
- **Link:** https://arxiv.org/abs/2510.11977 ; proceedings: https://proceedings.iclr.cc/paper_files/paper/2026/hash/a0928f924a344aaebbb7f6cd8d56e34c-Abstract-Conference.html
- **Core contribution:** A standardized, parallel **evaluation harness** plus a 3-D analysis (model × scaffold × benchmark) that quantifies how much the scaffold changes accuracy and cost. Releases 2.5B tokens of agent logs.
- **Methodology:** 21,730 rollouts over 9 models and 9 benchmarks (~$40k) on hundreds of VMs. Matched comparisons of task-specific and generalist scaffolds. Accuracy–cost Pareto frontiers. LLM-aided log inspection to find undesirable behaviours.
- **Datasets/benchmarks:** Online Mind2Web, AssistantBench, GAIA, CORE-Bench Hard, ScienceAgentBench, SciCode, SWE-bench Verified Mini, TAU-bench Airline, USACO.
- **Evaluation metrics:** Accuracy, $ cost, tokens, and accuracy-vs-cost Pareto frontiers. Findings: task-specific scaffolds beat the generalist scaffold in 11/12 SWE-bench Verified Mini and 9/12 CORE-Bench Hard matched runs. Model–scaffold interaction (Claude better with BrowserUse, OpenAI better with SeeAct). A 9× cost gap for ~2 points of accuracy on Online Mind2Web. Higher reasoning effort reduced accuracy in most runs.
- **Limitations:** Latency is skewed by rate limits under massive parallelism. Some model/benchmark cells were skipped for cost. Log analysis covered only 3 benchmarks. Domains such as cybersecurity are excluded. Prices and served weights change over time (all stated). Scaffold coverage per benchmark is sparse (often 1–2 scaffolds), so "scaffold effect" estimates have wide uncertainty (assessment).
- **Code availability:** Project site https://hal.cs.princeton.edu (seen via search). A code repository linked from the paper was not verified.
- **Unresolved research gaps:** A factorial design that varies one harness component at a time across many models. Variance and seed reporting for agent runs. Scaffold-invariant capability estimates.

---

## 7. AIOS

- **Title:** AIOS: LLM Agent Operating System
- **Authors:** Kai Mei, Xi Zhu, Wujiang Xu, et al.
- **Venue:** COLM 2025 (arXiv comment: "Published as a full paper at COLM 2025")
- **Year:** 2025 (arXiv v1 Mar 2024)
- **Link:** https://arxiv.org/abs/2403.16971
- **Core contribution:** An **OS-kernel abstraction for agents**. LLM inference, tools, memory, storage and access control move out of agent applications into a kernel that exposes "system calls", with scheduling and context switching (snapshot/restore of in-flight LLM generation). This extends MemGPT's OS framing from one agent's memory to multi-agent resource management.
- **Methodology:** Kernel modules: LLM core(s), scheduler (FIFO, Round-Robin), context manager (text-based snapshots for API models, logits/search-tree-based for open models), memory, storage, tool and access managers. An SDK ports agents from several frameworks.
- **Datasets/benchmarks:** HumanEval, MINT (code subset), GAIA, SWE-bench Lite. Agents built with ReAct, Reflexion, AutoGen, Open-Interpreter, MetaGPT. Backends GPT-4o-mini, Llama-3.1-8B, Mistral-7B.
- **Evaluation metrics:** Success rate (to show no regression), throughput (system calls/s), average agent waiting time, scalability from 250 to 2,000 agents. Up to 2.1× faster execution.
- **Limitations:** No explicit limitations section found in the visible text (not verified for the appendix). The speedup baseline is agents contending for a single LLM that serves one request at a time, a weak baseline next to a continuous-batching server such as vLLM/SGLang (assessment). Scheduling is FIFO/RR only, with no program-aware policy (assessment).
- **Code availability:** https://github.com/agiresearch/AIOS (linked from arXiv).
- **Unresolved research gaps:** Combining OS-style isolation and access control with program-aware serving (Autellix, #12) and KV-cache-aware context switching (InferCept, #11). A formal semantics for "agent system calls".

## 8. SGLang

- **Title:** SGLang: Efficient Execution of Structured Language Model Programs
- **Authors:** Lianmin Zheng, Liangsheng Yin, Zhiqiang Xie, et al.
- **Venue:** NeurIPS 2024 (Main Conference Track; proceedings.neurips.cc)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2312.07104 ; proceedings: https://proceedings.neurips.cc/paper_files/paper/2024/hash/724be4472168f31ba1c9ac630f15dec8-Abstract.html
- **Core contribution:** Co-designs a frontend language for multi-call LM programs (gen, fork/join, select, control flow) with a runtime whose **RadixAttention** keeps KV caches in a radix tree for automatic prefix reuse across calls, branches and turns. Adds compressed finite-state machines for fast constrained decoding.
- **Methodology:** Interpreter/compiler frontend, LRU eviction over the radix tree, cache-aware scheduling. Evaluated against vLLM, Guidance and LMQL backends.
- **Datasets/benchmarks:** Workloads include agent control, logical reasoning, few-shot learning (MMLU, HellaSwag), JSON decoding, RAG pipelines, multi-turn chat, tree-of-thought and multimodal tasks.
- **Evaluation metrics:** Throughput, latency, and cache hit rate. Up to 6.4× higher throughput reported.
- **Limitations:** The LRU eviction policy is agnostic to future reuse in agent workflows, which is exactly the gap KVFlow (#13) attacks (assessment, supported by #13). Benefits depend on programs sharing exact token prefixes, so agent histories that are edited, masked or summarized break prefix reuse (assessment).
- **Code availability:** https://github.com/sgl-project/sglang (linked from arXiv).
- **Unresolved research gaps:** Cache reuse for non-prefix (edited or compressed) contexts. The interaction between context-compression policies (#18–#20) and prefix-cache hit rate is unstudied.

## 9. Parrot

- **Title:** Parrot: Efficient Serving of LLM-based Applications with Semantic Variable
- **Authors:** Chaofan Lin, Zhenhua Han, Chengruidong Zhang, et al.
- **Venue:** OSDI 2024 (18th USENIX Symposium on Operating Systems Design and Implementation, pp. 929–945)
- **Year:** 2024
- **Link:** https://www.usenix.org/conference/osdi24/presentation/lin-chaofan ; arXiv: https://arxiv.org/abs/2405.19888
- **Core contribution:** **Semantic Variables** annotate prompt inputs and outputs so the serving system sees the *data-flow graph* of a multi-call application rather than isolated requests. This enables dependency-aware scheduling, prefix sharing and end-to-end (not per-request) optimization.
- **Methodology:** Data-flow analysis over Semantic Functions, with application-level objective deduction (latency vs. throughput), request co-location, and shared-prefix detection, built on its own engine (OPT/LLaMA).
- **Datasets/benchmarks:** Chain and map-reduce summarization of long arXiv papers, Bing-Copilot-style shared-system-prompt requests, GPTs apps, a MetaGPT multi-agent coding workflow, and mixed ShareGPT + map-reduce. LLaMA 7B/13B on A100/A6000.
- **Evaluation metrics:** End-to-end latency (mean, P90), speedup, normalized latency, sustained request rate, KV-cache memory. Up to an order of magnitude improvement.
- **Limitations:** Only cloud-side orchestration is supported, so dynamic control flow and native functions run on the client. Native-function offloading is disabled for security. Very long contexts are out of scope. Fairness and failure handling are left to future work. Frameworks must wrap templates as Semantic Functions (all stated). A synthetic network delay and GPT-4-normalized output lengths are used (stated).
- **Code availability:** not verified (no repo on the USENIX page).
- **Unresolved research gaps:** Automatic inference of Semantic Variables from unmodified agent code. Support for dynamic, data-dependent agent control flow. Related, verified work: Teola (Tan et al., ASPLOS 2025, https://arxiv.org/abs/2407.00326) extends the idea to primitive-level data-flow graphs that include non-LLM stages (retrieval, embedding), with up to 2.09× end-to-end speedup.

## 10. LLMCompiler

- **Title:** An LLM Compiler for Parallel Function Calling
- **Authors:** Sehoon Kim, Suhong Moon, Ryan Tabrizi, et al.
- **Venue:** ICML 2024 (arXiv comment)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2312.04511
- **Core contribution:** Recasts sequential ReAct tool use as **compiler-style planning and parallel execution**. A planner emits a DAG of function calls with dependencies, a task-fetching unit dispatches ready tasks, and an executor runs independent calls concurrently, with optional replanning.
- **Methodology:** Prompted planner (streamed for pipelining), DAG scheduling, joiner/replanner. Compared against ReAct, a prompt-tuned ReAct†, OpenAI parallel function calling, ToT (Game of 24), and LATS/LASER (WebShop).
- **Datasets/benchmarks:** HotpotQA, Movie Recommendation, ParallelQA (new, 113 examples), Game of 24, WebShop. GPT-3.5/4 and LLaMA-2-70B.
- **Evaluation metrics:** Accuracy/success, end-to-end latency/speedup (up to 3.7×), token cost (up to 6.7× cheaper), WebShop score.
- **Limitations:** Planner and final answer cannot be parallelized, and straggler tasks delay the join. Executor errors cause about 64% of ParallelQA failures. Slightly slower than ReAct on WebShop because of planner overhead. ParallelQA is constructed to remove search failures (all stated).
- **Code availability:** https://github.com/SqueezeAILab/LLMCompiler (linked from arXiv).
- **Unresolved research gaps:** The authors themselves suggest restructuring the agent scratchpad instead of appending observations, a context-engineering question left open. Speculative execution of uncertain branches. Integration with server-side schedulers (Autellix, #12).

## 11. InferCept

- **Title:** InferCept: Efficient Intercept Support for Augmented Large Language Model Inference
- **Authors:** Reyna Abhyankar, Zijian He, Vikranth Srivatsa, Hao Zhang, Yiying Zhang
- **Venue:** ICML 2024 (PMLR vol. 235, pp. 81–95)
- **Year:** 2024
- **Link:** https://proceedings.mlr.press/v235/abhyankar24a.html ; arXiv: https://arxiv.org/abs/2402.01869
- **Core contribution:** Identifies that serving engines treat every tool call ("interception") as request end and **discard and recompute the KV cache**, which costs 37–40% of model forwarding time. Introduces per-request *min-waste* selection among discard, preserve and swap for the paused context.
- **Methodology:** A GPU-memory waste model per strategy, swap pipelining and chunking, recomputation chunking up to a profiled GPU saturation point, and FCFS by original arrival. Built on vLLM.
- **Datasets/benchmarks:** Six augmentation types: math (calculator), Wikipedia QA, ALFWorld virtual environment, ShareGPT chatbot, image generation, and TTS. GPT-J-6B, Vicuna-13B, Llama3-70B.
- **Evaluation metrics:** Normalized latency, completed requests/s, TTFT. 1.6–2× higher sustainable load and >2× completed requests/s vs. vLLM.
- **Limitations:** Interception duration is estimated from elapsed time (93% of oracle). Human response times and some workload statistics are estimated, and the image/TTS datasets are synthetic (ChatGPT-generated). Relies on offline profiling. Alternative scheduling policies are deferred (all stated).
- **Code availability:** not verified.
- **Unresolved research gaps:** Predicting tool latency from tool identity and arguments. Coordinating KV retention with program-level scheduling and multi-turn agent sessions that last minutes to hours.

## 12. Autellix

- **Title:** Autellix: An Efficient Serving Engine for LLM Agents as General Programs
- **Authors:** Michael Luo, Xiaoxiang Shi, Colin Cai, et al.
- **Venue:** arXiv preprint (no venue found on arXiv or in search)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2502.13965
- **Core contribution:** Treats the **whole agent program as the scheduling unit**. A frontend intercepts each program's LLM calls and gives the scheduler program-level context, avoiding request- and program-level head-of-line blocking.
- **Methodology:** Non-clairvoyant schedulers: PLAS (program-level attained service) for single-threaded programs and ATLAS (critical-path attained service) for DAG/multi-threaded programs, plus program-aware load balancing across engines. Built as a layer over vLLM with a stateful session API.
- **Datasets/benchmarks:** ShareGPT (as programs), BFCL v3 (ReAct-style tool use), LATS on HotpotQA (MCTS), and a mixed workload. LLaMA-3.1-8B/70B and Falcon-180B on A100s.
- **Evaluation metrics:** Program-level token latency (a new metric), throughput at fixed latency, P95/P99 tail latency, makespan, swap time. 4–15× program throughput vs. vLLM.
- **Limitations:** The non-clairvoyant scheduler leaves a gap to SRPT in simulation. The frontend lacks safeguards against user tampering (both stated). Workloads are proxies for real agents, with no long-running coding/browsing agents with real tool latency (assessment). Peer review not yet confirmed (assessment).
- **Code availability:** not verified.
- **Unresolved research gaps:** Fairness/SLOs across tenants running agents. Combining attained-service scheduling with KV retention across tool waits (InferCept, #11) and workflow-aware eviction (KVFlow, #13).

## 13. KVFlow

- **Title:** KVFlow: Efficient Prefix Caching for Accelerating LLM-Based Multi-Agent Workflows
- **Authors:** Zaifeng Pan, Ajjkumar Patel, Zhengding Hu, et al.
- **Venue:** NeurIPS 2025 (Main Conference Track; proceedings page found via search)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2507.07400 ; proceedings: https://papers.neurips.cc/paper_files/paper/2025/hash/b7971d31a7d5eb0f1eed2f8f6f368195-Abstract-Conference.html
- **Core contribution:** **Workflow-aware KV-cache eviction and prefetching** for multi-agent workflows. An *Agent Step Graph* assigns each agent a steps-to-execution value that replaces LRU in a tree-structured prefix cache, and KV tensors for next-step agents are prefetched from CPU to GPU in the background.
- **Methodology:** Built on SGLang v0.4.4. Priority eviction at the KV-node level, with overlapped CPU→GPU prefetch.
- **Datasets/benchmarks:** Synthetic sequential 10-agent workflows, high-concurrency independent workflows, and PEER-style 4-agent workflows on Financial QA. Llama-3.1-8B (A10G), Qwen2.5-32B (H100).
- **Evaluation metrics:** End-to-end latency speedup. Up to 1.83× over SGLang HiCache (single workflow) and 2.19× (concurrent). Only 1.08–1.12× on the realistic PEER workload.
- **Limitations:** Requires the workflow graph to be supplied and the fixed/dynamic prompt boundary marked. Gains shrink as decode dominates. Mostly synthetic workloads. Excludes workflows that share state (all stated in the paper body). Gains on the most realistic workload are small (assessment).
- **Code availability:** not verified as linked from the paper (a repo surfaced in search but I did not see it linked from the arXiv page).
- **Unresolved research gaps:** Inferring agent schedules online for dynamic (LLM-chosen) workflows. Eviction policies for compressed or edited contexts.

---

## 14. DSPy

- **Title:** DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines (arXiv title: "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines")
- **Authors:** Omar Khattab, Arnav Singhvi, Paridhi Maheshwari, et al.
- **Venue:** ICLR 2024 (Spotlight; proceedings.iclr.cc and ICLR virtual site)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2310.03714 ; proceedings: https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html
- **Core contribution:** Treats LM pipelines, including agent loops, as **programs of declarative modules with signatures**. A compiler ("teleprompters") optimizes prompts and demonstrations against a metric, making context construction a learnable, programmatic artifact instead of hand-written strings.
- **Methodology:** Modules (Predict, ChainOfThought, ReAct, etc.) parameterized by signatures. Optimizers bootstrap demonstrations from program traces and select them by validation metric.
- **Datasets/benchmarks:** GSM8K (math word problems), HotPotQA (multi-hop retrieval and QA), plus agent-loop case studies. GPT-3.5, Llama2-13b-chat, small models.
- **Evaluation metrics:** Task accuracy / exact match, compared with few-shot and expert-written prompt pipelines.
- **Limitations:** Optimization needs a metric and training examples. Compilation cost and variance across runs are not deeply characterized (assessment). Agent-loop evaluation is limited compared with QA/math (assessment).
- **Code availability:** https://github.com/stanfordnlp/dspy (linked from arXiv).
- **Unresolved research gaps:** Optimizing long-horizon agent context (history, observation formatting, tool descriptions) rather than per-call prompts. Later optimizers (MIPROv2, GEPA) are used as baselines in ACE (#20), which shows the open question of optimizing *evolving* context.

---

## 15. Lost in the Middle

- **Title:** Lost in the Middle: How Language Models Use Long Contexts
- **Authors:** Nelson F. Liu, Kevin Lin, John Hewitt, et al.
- **Venue:** Transactions of the ACL (TACL), Vol. 12, pp. 157–173
- **Year:** 2024 (arXiv July 2023)
- **Link:** https://aclanthology.org/2024.tacl-1.9/ ; arXiv: https://arxiv.org/abs/2307.03172
- **Core contribution:** Shows a **U-shaped positional curve**. Models use information at the start and end of the context far better than information in the middle, including models marketed as long-context. This is the empirical basis for placement-aware context engineering.
- **Methodology:** Controlled manipulation of where the relevant document or key sits and how long the input is. Comparison of decoder-only vs. encoder-decoder models, query-aware contextualization, and instruction tuning effects.
- **Datasets/benchmarks:** Multi-document QA built from NaturalQuestions-Open (10/20/30 documents), synthetic key-value retrieval.
- **Evaluation metrics:** Accuracy as a function of relevant-information position and context length.
- **Limitations:** Retrieval-style tasks only, with no multi-step agent trajectories (assessment). The models studied (2023 generation) have been superseded, and the size of the effect in current models must be re-measured (assessment).
- **Code availability:** not verified (no code link on the arXiv or ACL Anthology page).
- **Unresolved research gaps:** Positional sensitivity inside agent trajectories (system prompt, tool schemas, old observations, latest observation). Whether harness conventions (e.g., re-stating the task at the end) systematically exploit the U-curve.

## 16. Context Length Alone Hurts

- **Title:** Context Length Alone Hurts LLM Performance Despite Perfect Retrieval
- **Authors:** Yufeng Du, Minyang Tian, Srikanth Ronanki, et al.
- **Venue:** Findings of EMNLP 2025 (arXiv comment: "accepted at the Findings of EMNLP 2025")
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2510.05381
- **Core contribution:** Separates *length* from *retrieval*. Even when models retrieve all evidence perfectly, and even when distractors are whitespace or fully attention-masked, accuracy drops 13.9%–85% as input length grows within claimed context limits. This is direct evidence for "context rot" independent of distraction.
- **Methodology:** Controlled padding with essay tokens, whitespace, or masked tokens, up to about 30K. Evidence placed adjacent to the question. Mitigation: prompt the model to recite the evidence first, turning a long-context problem into a short one.
- **Datasets/benchmarks:** VarSum (synthetic), GSM8K, MMLU, HumanEval, RULER QA (GPT-4o mitigation). Llama-3.1-8B, Mistral-7B-v0.3, GPT-4o, Claude, Gemini.
- **Evaluation metrics:** Accuracy delta vs. zero-distraction baseline, exact-match retrieval. Up to +4% on RULER for GPT-4o with recitation.
- **Limitations:** Five models and four tasks. Retrieval was not measured for closed models (they refused to recite). The mitigation requires accurate retrieval (all stated). Single-turn tasks, not agent loops (assessment). The paper reports inconsistent Claude model naming between table and text (assessment, observed in the HTML).
- **Code availability:** not verified.
- **Unresolved research gaps:** Whether length-induced degradation compounds over multi-turn agent trajectories. Whether "recite then solve" generalizes to an agent harness pattern (periodic restatement or state summaries).

---

## 17. LLMLingua

- **Title:** LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models
- **Authors:** Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, Lili Qiu
- **Venue:** EMNLP 2023 (main conference, pp. 13358–13376)
- **Year:** 2023
- **Link:** https://aclanthology.org/2023.emnlp-main.825/ ; arXiv: https://arxiv.org/abs/2310.05736
- **Core contribution:** **Coarse-to-fine, perplexity-based prompt compression** using a small LM. A budget controller allocates compression across demonstrations, instructions and questions. Iterative token-level compression models dependencies among retained tokens, and instruction tuning aligns the small LM's distribution to the target LLM.
- **Methodology:** Drop low-information demonstrations and tokens by small-LM perplexity, then send the compressed prompt to a black-box LLM.
- **Datasets/benchmarks:** GSM8K, BBH, ShareGPT, Arxiv-March23.
- **Evaluation metrics:** Task accuracy/EM (reasoning), BLEU/ROUGE/BERTScore (conversation, summarization), compression ratio (up to 20×), end-to-end latency.
- **Limitations:** Designed for static prompts (ICL demos, documents), not evolving agent trajectories (assessment). Token-dropping can corrupt exact strings agents depend on (file paths, IDs, code), and ACON (#19) uses LLMLingua as a baseline for agents and outperforms it (assessment, supported by #19).
- **Code availability:** https://aka.ms/LLMLingua (linked from arXiv abstract).
- **Unresolved research gaps:** Structure-aware compression that preserves executable or identifier tokens. Compression that keeps KV-prefix stability for caching (#8).

## 18. The Complexity Trap

- **Title:** The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management
- **Authors:** Tobias Lindenbauer, Igor Slinko, Ludwig Felder, Egor Bogomolov, Yaroslav Zharov
- **Venue:** Workshop paper: 4th Deep Learning for Code (DL4C) workshop at NeurIPS 2025 (arXiv comment). Not a main-conference paper.
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2508.21433
- **Core contribution:** A controlled comparison showing that **masking old environment observations** (keeping actions and reasoning) roughly halves cost relative to the raw agent and matches or slightly beats LLM summarization of history, as used in OpenHands/Cursor-style condensers. Proposes a hybrid.
- **Methodology:** SWE-agent scaffold. Rolling window of M = 10 turns for masking, against an LLM-summary condenser and the raw agent. Five model configurations. Hybrid of masking plus occasional summarization. Generality probe on OpenHands.
- **Datasets/benchmarks:** SWE-bench Verified (plus a 50-instance subset for the hybrid). Qwen3-32B (thinking and non-thinking), Qwen3-Coder-480B, Gemini 2.5 Flash (thinking and non-thinking).
- **Evaluation metrics:** Solve rate, $ cost, trajectory length. Masking cuts cost about 50–57% in most configurations (9.8% for Qwen3-32B thinking). Qwen3-Coder solve rate 54.8% masked vs. 53.8% summary vs. 53.4% raw. Hybrid saves a further 7% vs. masking and 11% vs. summary.
- **Limitations:** Software engineering only. Simple non-adaptive triggers. Limited cross-scaffold evidence (all stated). Single-run solve-rate differences of about 1 point are within plausible run-to-run noise (assessment).
- **Code availability:** https://github.com/JetBrains-Research/the-complexity-trap ; data https://huggingface.co/datasets/JetBrains-Research/the-complexity-trap (linked in paper).
- **Unresolved research gaps:** Adaptive (learned) masking triggers. Interaction with prefix caching, since masking changes earlier tokens and invalidates KV reuse. Non-coding domains where observations carry more task state.

## 19. ACON

- **Title:** ACON: Optimizing Context Compression for Long-horizon LLM Agents
- **Authors:** Minki Kang, Wei-Ning Chen, Dongge Han, et al.
- **Venue:** ICML 2026 (arXiv comment)
- **Year:** 2026 (arXiv Oct 2025)
- **Link:** https://arxiv.org/abs/2510.00615
- **Core contribution:** **Gradient-free optimization of the compression guideline** for both history and observations. An optimizer LLM contrasts trajectories that succeed uncompressed but fail compressed, then rewrites the natural-language compressor prompt. The optimized compressor is distilled into small models.
- **Methodology:** Threshold-triggered compression (4096 tokens for history, 1024 for observations). Two-phase guideline optimization (utility, then brevity) with an o3 optimizer. LoRA distillation into Qwen3-14B/8B and Phi-4.
- **Datasets/benchmarks:** AppWorld, OfficeBench, 8-objective multi-hop QA. gpt-4.1 as agent and compressor (others in appendix).
- **Evaluation metrics:** Task success/score, EM/F1, peak input tokens (−26–54%), steps, cost, latency. Distilled compressors keep >95% of teacher performance. Qwen3-14B on AppWorld goes from 25.6% to 33.9%.
- **Limitations:** Evaluation focuses primarily on GPT models because of resource constraints. Compression adds compute and latency overhead (both stated). The guideline is optimized per benchmark, and transfer across task families is not established (assessment).
- **Code availability:** https://github.com/microsoft/acon (linked from arXiv).
- **Unresolved research gaps:** Compressor guidelines that transfer across domains. Joint optimization with prefix-cache retention. Comparison against the simple masking baseline of #18 (not included among ACON's listed baselines).

## 20. Agentic Context Engineering (ACE)

- **Title:** Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models
- **Authors:** Qizheng Zhang, Changran Hu, Shubhangi Upasani, et al.
- **Venue:** ICLR 2026 (arXiv comment)
- **Year:** 2026 (arXiv Oct 2025)
- **Link:** https://arxiv.org/abs/2510.04618
- **Core contribution:** Treats context as an **evolving, itemized "playbook"** curated by Generator → Reflector → Curator roles. It uses *incremental delta updates* (bulleted items with IDs and helpful/harmful counters, merged non-LLM) and grow-and-refine deduplication to avoid "brevity bias" and "context collapse" from repeated whole-context rewriting.
- **Methodology:** Offline (system-prompt) and online (test-time memory) adaptation from execution feedback, with or without labels. DeepSeek-V3.1 default backbone, plus GPT-OSS-120B, GPT-5.1, Llama-3.3-70B.
- **Datasets/benchmarks:** AppWorld (normal and challenge splits, ReAct agent), FiNER, Formula (finance). DDXPlus and BIRD-SQL in appendix.
- **Evaluation metrics:** Task/Scenario Goal Completion (AppWorld), accuracy, adaptation latency, rollouts, token cost. +10.6% on agents and +8.6% on finance on average. 59.4% AppWorld average vs. 60.3% for the top leaderboard production agent.
- **Limitations:** Depends on a reasonably strong Reflector. Degrades without reliable feedback signals. Little benefit on tasks that need little context (all stated). The playbook grows monotonically between dedup passes, and its interaction with long-context degradation (#15, #16) is not measured (assessment).
- **Code availability:** https://github.com/ace-agent/ace (linked in paper).
- **Unresolved research gaps:** Bounding playbook size under context-rot constraints. Robustness to poisoned or incorrect feedback. Comparing evolving-context methods against weight updates at equal compute.

---

## 21. ToolRet

- **Title:** Retrieval Models Aren't Tool-Savvy: Benchmarking Tool Retrieval for Large Language Models
- **Authors:** Zhengliang Shi, Yuhan Wang, Lingyong Yan, et al.
- **Venue:** Findings of ACL 2025 (pp. 24497–24524)
- **Year:** 2025
- **Link:** https://aclanthology.org/2025.findings-acl.1258/ ; arXiv: https://arxiv.org/abs/2503.01763
- **Core contribution:** Frames **tool selection as a retrieval-for-context problem** and shows that strong general IR models fail at it. ToolRet has 7.6k retrieval tasks over a 43k-tool corpus aggregated from existing tool-use datasets, plus a 200k+ training set (ToolRet-train).
- **Methodology:** Benchmark six families of retrievers (sparse, dense, re-rankers, LLM-based embedders, etc.). Measure the downstream impact of retrieval quality on tool-using LLM pass rate. Train retrievers on ToolRet-train.
- **Datasets/benchmarks:** ToolRet (built from existing tool datasets), with downstream tool-use evaluation.
- **Evaluation metrics:** Standard IR metrics (e.g., NDCG/recall@k; exact set not verified) and downstream task pass rate.
- **Limitations:** Corpus is aggregated from existing benchmarks whose tool descriptions vary in quality (assessment). Static retrieval before the call, with no study of re-retrieval mid-trajectory (assessment).
- **Code availability:** https://github.com/mangopy/tool-retrieval-benchmark (linked from arXiv).
- **Unresolved research gaps:** Dynamic tool exposure across turns (MCP-scale catalogs). Joint optimization of tool *descriptions* and retrievers. Related, verified preprint: RAG-MCP (Gan & Sun, arXiv 2505.03275) reports >50% prompt-token reduction and tool-selection accuracy rising from 13.62% to 43.13% by retrieving MCP tool descriptions, but uses an MCP stress test of its own design.

---

## 22. DeltaBox

- **Title:** DeltaBox: Scaling Stateful AI Agents with Millisecond-Level Sandbox Checkpoint/Rollback
- **Authors:** Yunpeng Dong, Jingkai He, Shiqi Liu, et al.
- **Venue:** arXiv preprint
- **Year:** 2026
- **Link:** https://arxiv.org/abs/2605.22781
- **Core contribution:** OS-level **incremental checkpoint/rollback of agent sandbox state** (files and processes) at about 10–14 ms checkpoint and about 2–5 ms restore. This makes tree search, MCTS and RL fan-out over stateful environments practical.
- **Methodology:** DeltaState abstraction: DeltaFS (layered copy-on-write file states, so rollback is a layer switch, with reflink copy-up) and DeltaCR (incremental process dumps plus forking from frozen template processes), with reachability-aware GC.
- **Datasets/benchmarks:** MCTS over SWE-bench Verified trajectories (Qwen3-Coder-30B), RL rollout fan-out (Qwen2.5-7B), write-amplification and storage-GC microbenchmarks. Baselines: copytree+replay, Firecracker diff snapshots + dm-snapshot, CRIU+copytree, self-hosted E2B incremental snapshots.
- **Evaluation metrics:** Checkpoint/restore latency, end-to-end time normalized to LLM+action time (1.01–1.02× vs. 1.30–1.93× for E2B), state-management share of time, fork p50/p99, GPU occupation, storage bytes.
- **Limitations:** No network I/O rollback, so external side effects can escape (stated). Single-node design. A slow path via CRIU lazy-pages when templates are evicted (stated). Some comparison numbers are vendor-reported or computed rather than measured end-to-end (stated). Not peer reviewed (assessment).
- **Code availability:** not verified (none linked on arXiv).
- **Unresolved research gaps:** Semantic validity of rollback when external effects have already been committed. Two verified 2026 preprints attack this directly: ACRFence (Zheng et al., arXiv 2603.20625; CoDAIM workshop 2026 per journal-ref) shows "semantic rollback attacks" in which restored agents re-issue irreversible tool calls. DART (Yang et al., arXiv 2605.23311) formalizes "semantic recoverability" and admissible restore points. Joint checkpointing of sandbox state, conversation context and KV cache remains open.

---

## Recurring weaknesses in this slice (my assessment)

- **Scaffold and harness confounds go unmeasured.** Most harness papers report one scaffold per model with hand-tuned interface knobs. Yet SWE-agent's own ablations move SWE-bench Lite by 3–8 points from viewer-window size or linting alone, and HAL finds model×scaffold interactions and 9× cost gaps. Headline comparisons across papers are therefore not apples-to-apples. Applies to: #1, #2, #3, #4, #5, #6, #20.
- **Single-run results with no variance on stochastic agent benchmarks.** Differences of 1–2 points are reported as wins without seeds or confidence intervals. Applies to: #2, #4, #5, #18, #19, #20.
- **Systems papers rely on synthetic or proxy agent workloads.** Serving gains are measured on synthetic workflows, ShareGPT recast as programs, estimated tool or human latencies, or weak single-request baselines. The most realistic workloads show the smallest gains (KVFlow: 1.08–1.12× on PEER). Applies to: #7, #9, #11, #12, #13.
- **Context management and KV caching are optimized in isolation.** Compression, masking and playbook editing rewrite earlier tokens, which breaks the exact-prefix reuse that RadixAttention, KVFlow and InferCept depend on. No paper measures the joint cost. Applies to: #8, #11, #13, #17, #18, #19, #20.
- **Context-degradation evidence comes from single-turn retrieval tasks.** The canonical results on positional bias and length-induced degradation are not measured on multi-turn agent trajectories, which is where harnesses actually accumulate context. Applies to: #15, #16 (and by extension the motivation sections of #18, #19, #20).
- **Narrow domain coverage, dominated by SWE-bench.** Harness and context-management claims are drawn heavily from Python bug-fixing (and AppWorld), with acknowledged leakage and benchmark-quality issues. Applies to: #2, #4, #5, #18, #19, #20, #22.
- **Missing baselines across subcommunities.** ACON does not compare against simple observation masking (#18). AIOS compares against a one-request-at-a-time LLM rather than a batched server. LLMLingua-style token compression is used as a strawman for agent compression. Applies to: #7, #17, #19.
- **State and rollback ignore external side effects.** Checkpointing work restores local state but not committed external actions. AIOS context snapshots and OpenHands event streams lack formal recovery semantics. Applies to: #4, #7, #22.

## Open problems that a small team could attack (my assessment)

- **Cache-aware context management.** Measure, and then co-design, compression and masking policies (#18, #19) together with prefix-cache hit rate on an open serving stack (SGLang, #8). For example, append-only "masking by tombstone" or compressing only at cache-block boundaries. This needs only open models, SWE-bench Verified Mini or AppWorld, and one GPU node. Report $ cost and latency, not just tokens.
- **A factorial harness-ablation benchmark.** Fix 3–4 open and closed models and vary one ACI or harness component at a time: action format (JSON vs. code), observation window, history policy, tool-description verbosity, re-statement of task at the end. Use several seeds and report effect sizes with CIs. This turns the anecdotal findings of #2, #5 and #6 into a reusable dataset.
- **Agent-trajectory context rot.** Port the controlled designs of #15 and #16 (position sweeps, whitespace/masked padding, recite-first mitigation) into multi-turn agent loops. Find where in a trajectory critical state is lost, and whether periodic recitation or state summaries recover it.
- **Dynamic tool exposure at MCP scale.** Build on ToolRet (#21) with mid-trajectory re-retrieval and tool-description rewriting. Measure the trade-off between token cost and selection accuracy against the "load all tools" baseline across large real MCP catalogs.
- **Semantically safe checkpoint/replay for agents.** Combine a cheap sandbox snapshot (DeltaBox-style, #22, or OpenHands event-stream replay, #4) with an effect log for irreversible tool calls (per ACRFence/DART). Then evaluate recovery correctness and cost on long-horizon tasks with injected failures.
- **Program-aware scheduling for real agent traces.** Replay HAL's released agent logs (#6) through Autellix/InferCept-style schedulers (#11, #12) to test whether reported serving gains hold under real tool-latency and branching distributions.

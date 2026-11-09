# 03 — Agent Memory and Long-Term Memory

**Scope.** This slice covers how LLM agents store, organize, update, forget, and retrieve information beyond a single context window, from 2023 to late 2026. It includes:

- **Non-parametric memory:** memory streams, OS-style paging, Zettelkasten and graph memory, temporal knowledge graphs, and hippocampus-inspired retrieval.
- **Procedural and experiential memory:** skill libraries, extracted insights, workflows, and reasoning strategies.
- **Learned memory management:** reinforcement learning for memory operations and compact internal state.
- **Parametric memory:** latent memory pools inside the model.
- **Memory benchmarks:** LoCoMo, LongMemEval, and MemoryAgentBench.
- **Memory security:** backdoor and injection attacks that poison an agent's memory.

Reflexion is out of scope here; the planning slice covers it. Two surveys are included and marked as surveys.

**How each paper was checked.** I confirmed every entry on a primary page (arxiv.org/abs or arXiv HTML, aclanthology.org, proceedings.mlr.press, ICML/ICLR/NeurIPS virtual-conference pages, or ojs.aaai.org). A venue is named only when acceptance was confirmed from one of these: a proceedings page, a conference poster page, the arXiv comments field, or the authors' repository saying so. Otherwise the entry says "arXiv preprint". A code URL is given only when I saw it linked from the paper, its abstract page, or its venue or project page. Limitations are tagged **(stated)** when the authors say so, and **(assessment)** when it is my own reading.

Counts: 21 research papers and 2 surveys.

---

## 1. Generative Agents

- **Title:** Generative Agents: Interactive Simulacra of Human Behavior
- **Authors:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
- **Venue:** UIST '23 (36th Annual ACM Symposium on User Interface Software and Technology), DOI 10.1145/3586183.3606763. The venue comes from the ACM reference format printed in the arXiv version; the ACM DL page itself returned 403 to my fetcher.
- **Year:** 2023
- **Link:** https://arxiv.org/abs/2304.03442
- **Core contribution:** An agent architecture built on a natural-language *memory stream* of all observations. Agents *retrieve* from it by scoring each memory on recency, importance, and relevance. They periodically synthesize higher-level *reflections* and use retrieved memories to plan. It is the reference design that most later agent-memory work builds on.
- **Methodology:**
  - Every observation is stored with a timestamp.
  - The retrieval score combines three terms: exponentially decayed recency, an LLM-rated importance on a 1–10 scale, and embedding relevance.
  - Reflection is triggered when accumulated importance crosses a threshold. It writes inferred, more abstract memories back into the stream as a reflection tree.
  - Plans are generated top-down and revised recursively.
  - 25 agents run in a Sims-like sandbox ("Smallville") on gpt-3.5-turbo.
- **Datasets/benchmarks:** No standard benchmark. The evaluation uses a custom sandbox, scripted "interviews" with agents, and a two-day end-to-end simulation.
- **Evaluation metrics:**
  - Human-rated believability of interview responses, ranked across full-architecture, ablated, and crowdworker-authored conditions using TrueSkill.
  - Emergent social behaviors: information diffusion, relationship formation, and coordination around a party.
- **Limitations:**
  - Memory retrieval failures, fabricated embellishments, and overly formal or cooperative behavior attributed to instruction tuning (stated).
  - High compute cost of running the simulation (stated).
  - Believability is judged by humans on short interviews. There is no task-success or factual-recall metric, so the memory design is not tested on accuracy (assessment).
  - The retrieval weights are hand-set and equal (assessment).
- **Code availability:** not verified. I could not confirm a link from the paper or arXiv page.
- **Unresolved research gaps:**
  - Learned or adaptive retrieval scoring instead of fixed weights.
  - A principled reflection trigger.
  - Memory growth without bound.
  - Whether reflections compound errors over long horizons.

## 2. MemGPT

- **Title:** MemGPT: Towards LLMs as Operating Systems
- **Authors:** Charles Packer, Sarah Wooders, Kevin Lin, et al.
- **Venue:** arXiv preprint
- **Year:** 2023 (v1 Oct 2023; v2 Feb 2024)
- **Link:** https://arxiv.org/abs/2310.08560
- **Core contribution:** *Virtual context management*, borrowed from OS memory hierarchies. The LLM itself pages information between a bounded main context and external storage via function calls, so it appears to have unbounded context.
- **Methodology:**
  - Main context has three parts: system instructions, an editable working context, and a FIFO message queue.
  - External context has two parts: recall storage (the full message history) and archival storage (a vector store).
  - The LLM issues function calls to read, write, and search these tiers.
  - "Memory pressure" warnings and interrupts drive eviction, recursive summarization, and control flow.
- **Datasets/benchmarks:**
  - Multi-Session Chat (MSC), extended with a new Deep Memory Retrieval (DMR) task and a conversation-opener task.
  - Document QA over Wikipedia following the NaturalQuestions-Open setup of Liu et al.
  - A nested key-value retrieval task.
- **Evaluation metrics:**
  - DMR accuracy (LLM-judged) and ROUGE-L.
  - Similarity of generated conversation openers to persona and human openers.
  - QA accuracy and nested-KV accuracy as document count or nesting depth grows.
- **Limitations:**
  - Depends on the base model's reliability at function calling; weaker models degrade markedly (stated, for GPT-3.5 vs GPT-4).
  - DMR is small and fits inside modern context windows. Later work (Zep, item 8) also could not reproduce some MemGPT numbers (assessment).
  - Paging policy is prompt-engineered, not learned (assessment).
- **Code availability:** https://research.memgpt.ai and https://memgpt.ai, both linked from arXiv. The project has since been renamed Letta.
- **Unresolved research gaps:**
  - Learning eviction and paging policies.
  - Cost of the extra LLM calls spent on memory management.
  - Evaluation on genuinely long-horizon tasks, not just recall.

## 3. MemoryBank

- **Title:** MemoryBank: Enhancing Large Language Models with Long-Term Memory
- **Authors:** Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, Yanlin Wang
- **Venue:** AAAI 2024 (Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 17, pp. 19724–19731; DOI 10.1609/aaai.v38i17.29946)
- **Year:** 2024 (arXiv May 2023)
- **Link:** https://ojs.aaai.org/index.php/AAAI/article/view/29946 ; https://arxiv.org/abs/2305.10250
- **Core contribution:** A long-term memory store for companion chatbots with explicit *forgetting* modeled on the Ebbinghaus curve. Memories decay with time and are reinforced when recalled. The system also builds summaries and a profile of the user's personality.
- **Methodology:**
  - Retention follows R = e^(−t/S). Strength S starts at 1, increases by 1 on each recall, and resets the elapsed time t.
  - Dialogues, event summaries, and user-portrait summaries are retrieved by dense embeddings (MiniLM for English, Text2vec for Chinese).
  - Demonstrated in the SiliconFriend chatbot on ChatGPT, ChatGLM-6B, and BELLE-7B; the open models are additionally tuned on psychological dialogues.
- **Datasets/benchmarks:** 10 days of simulated conversations between 15 ChatGPT-role-played users and the assistant, plus 194 manually written probing questions (97 English, 97 Chinese). Later work reuses this setup as the "GVD" dataset (see item 11).
- **Evaluation metrics:** Human-labeled scores for memory retrieval accuracy (0/1), response correctness (0/0.5/1), and contextual coherence (0/0.5/1), plus a model-ranking score (1/rank).
- **Limitations:**
  - The memory-update model is "exploratory and highly simplified". Forgetting curves vary by person and type of information. Overlearning and meaningfulness effects are omitted (stated).
  - Weaker open-source backbones underperform (stated).
  - The evaluation is small, uses simulated users, and has no ablation showing that forgetting improves outcomes over no forgetting (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:**
  - Whether forgetting curves help task performance, as opposed to only bounding storage.
  - Learned decay rates per memory type.
  - Evaluation with real longitudinal users.

## 4. Voyager (skill library as procedural memory)

- **Title:** Voyager: An Open-Ended Embodied Agent with Large Language Models
- **Authors:** Guanzhi Wang, Yuqi Xie, Yunfan Jiang, et al.
- **Venue:** Transactions on Machine Learning Research (TMLR), March 2024, per the authors' lab publication page (UT Austin RPL). Also a spotlight at the NeurIPS 2023 Agent Learning in Open-Endedness (ALOE) workshop, per the NeurIPS virtual page.
- **Year:** 2024 (arXiv May 2023)
- **Link:** https://arxiv.org/abs/2305.16291
- **Core contribution:** A lifelong-learning Minecraft agent whose *skill library* of executable, embedding-indexed JavaScript programs acts as growing procedural memory. Verified skills are stored, retrieved by description, and composed into new ones.
- **Methodology:**
  - An automatic curriculum proposes the next task.
  - GPT-4 writes code and refines it iteratively using environment feedback, execution errors, and self-verification.
  - Successful programs are added to the library, keyed by an embedding of their description.
  - GPT-4 is queried as a black box, with no fine-tuning.
- **Datasets/benchmarks:** Minecraft via MineDojo/Mineflayer. Zero-shot transfer is tested in a new world.
- **Evaluation metrics:** Number of unique items obtained, distance traveled, and speed of unlocking tech-tree milestones. The arXiv abstract reports 3.3x items, 2.3x distance, and up to 15.3x faster milestones vs prior SOTA (the NeurIPS workshop abstract says 3.1x items).
- **Limitations:**
  - Cost of GPT-4 queries and occasional hallucinated or inaccurate self-verification (stated).
  - Single, code-friendly domain. Skills are never pruned or consolidated, and there is no analysis of how the library degrades at scale (assessment).
- **Code availability:** https://voyager.minedojo.org/ (project site with open-source codebase, linked from arXiv)
- **Unresolved research gaps:**
  - Skill-library maintenance: deduplication, deprecation, and conflicting skills.
  - Transfer of procedural memory across domains without executable code.

## 5. ExpeL

- **Title:** ExpeL: LLM Agents Are Experiential Learners
- **Authors:** Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang
- **Venue:** AAAI-24, per the arXiv comments field
- **Year:** 2024 (arXiv Aug 2023)
- **Link:** https://arxiv.org/abs/2308.10144
- **Core contribution:** An agent that learns across tasks without weight updates. It collects trajectories on training tasks and distills them into reusable natural-language *insights*. At test time it retrieves both the insights and similar successful trajectories.
- **Methodology:**
  - Reflexion-style trial and retry collects successes and failures.
  - An LLM compares success/failure pairs and success sets, then edits a running insight list with operations such as add, edit, upvote, and downvote.
  - At inference, the insights are prepended to the prompt and top-k similar successful trajectories are retrieved as demonstrations.
- **Datasets/benchmarks:** HotpotQA, ALFWorld, and WebShop, with transfer to FEVER.
- **Evaluation metrics:** Task success rate (exact match for QA).
- **Limitations:**
  - Relies on strong closed-source LLMs and text-only environments (stated in the paper's discussion).
  - The insight list is bounded by context length. Insights are not validated causally, and spurious "lessons" can persist (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:**
  - Credit assignment: which insight actually helped.
  - Scaling insight memory beyond what fits in the prompt.
  - Insight drift and contradiction over long deployment.

## 6. A-MEM

- **Title:** A-MEM: Agentic Memory for LLM Agents
- **Authors:** Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang
- **Venue:** NeurIPS 2025, per the arXiv comments field
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2502.12110
- **Core contribution:** A Zettelkasten-inspired memory in which the LLM writes structured notes, links each new note to related older notes, and lets new memories *evolve* the descriptions of existing ones, rather than using a fixed schema.
- **Methodology:**
  - Each note holds content, a timestamp, LLM-generated keywords, tags, a contextual description, an embedding, and links.
  - Link generation works in two steps: embedding nearest neighbours, then an LLM judgment.
  - Memory evolution: the LLM updates the context and tags of neighbouring notes.
  - Retrieval is by embedding similarity (all-minilm-l6-v2), expanded through linked notes.
- **Datasets/benchmarks:** LoCoMo (7,512 QA pairs) and DialSim (multi-party TV-show dialogue).
- **Evaluation metrics:** F1, BLEU-1, ROUGE-L, ROUGE-2, METEOR, SBERT similarity, and tokens used per query.
- **Limitations:**
  - Organization quality depends on the backbone LLM; different LLMs produce different descriptions and links (stated).
  - Text-only; multimodal extension is left to future work (stated).
  - Lexical-overlap metrics on LoCoMo reward surface matches. Later re-implementations (item 11) report different A-MEM numbers. Memory evolution can overwrite correct older context, and this is not measured (assessment).
- **Code availability:** https://github.com/WujiangXu/A-mem (evaluation) and https://github.com/WujiangXu/A-mem-sys (system), both linked from the abstract
- **Unresolved research gaps:**
  - Guarantees that memory evolution does not corrupt facts.
  - Cost of the LLM calls made on every write.
  - Behavior when the memory graph grows to millions of notes.

## 7. Mem0

- **Title:** Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory
- **Authors:** Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, Deshraj Yadav
- **Venue:** arXiv preprint
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2504.19413
- **Core contribution:** A production-oriented memory layer that extracts salient facts from conversation and *consolidates* them with existing memories through explicit operations. It has a graph variant, Mem0^g, for relational and temporal facts.
- **Methodology:**
  - Facts are extracted from a conversation summary, the last 10 messages, and the new message pair.
  - For each fact, the top 10 similar memories are retrieved, and the LLM chooses ADD, UPDATE, DELETE, or NOOP via a tool call.
  - Mem0^g stores entity and relation triplets in Neo4j. Conflicting relations are marked invalid rather than deleted.
  - Backbone: GPT-4o-mini.
- **Datasets/benchmarks:** LoCoMo (single-hop, multi-hop, temporal, open-domain). The adversarial category is excluded.
- **Evaluation metrics:**
  - F1, BLEU-1, and LLM-as-a-Judge (J, mean of 10 runs).
  - p50/p95 search and total latency, and memory tokens per conversation.
  - Overall J: 66.88 (Mem0) and 68.44 (Mem0^g), vs 72.90 for full context.
- **Limitations:**
  - Graph memory did not help single-hop or multi-hop questions and added latency (stated).
  - Adversarial questions excluded (stated).
  - Industry authors benchmark their own product against competitors on a single benchmark. The judge model is unnamed. The abstract (91%) and body (92%/85%) disagree on the p95 latency reduction. Full context still scores higher on J (assessment).
- **Code availability:** not verified; no paper-specific link on the arXiv page
- **Unresolved research gaps:**
  - Independent, multi-benchmark evaluation.
  - Robustness of the LLM-chosen UPDATE/DELETE operations to adversarial or mistaken input; this ties to memory poisoning (items 18–19).
  - Procedural and multimodal memory (stated as future work).

## 8. Zep / Graphiti

- **Title:** Zep: A Temporal Knowledge Graph Architecture for Agent Memory
- **Authors:** Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef
- **Venue:** arXiv preprint
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2501.13956
- **Core contribution:** Agent memory as a *bi-temporal* knowledge graph (Graphiti). It separates when an event happened from when the system learned it, and invalidates superseded facts instead of overwriting them.
- **Methodology:**
  - Three subgraphs: an episode subgraph of raw messages stored without loss, a semantic entity/fact subgraph, and a community subgraph built by label propagation, with summaries.
  - Each edge carries t_valid/t_invalid and t′_created/t′_expired.
  - An LLM checks new facts against existing ones and invalidates contradicted edges.
  - Retrieval combines cosine similarity, BM25, and breadth-first graph search, followed by RRF, MMR, or cross-encoder reranking.
- **Datasets/benchmarks:** Deep Memory Retrieval (DMR, from MemGPT) and LongMemEval_S (about 115k tokens per history).
- **Evaluation metrics:**
  - Accuracy, judged by GPT-4o on LongMemEval.
  - Latency and context tokens.
  - DMR: 94.8% vs MemGPT's reported 93.4%.
  - LongMemEval_S: 71.2% vs 60.2% full context with gpt-4o, at about 1.6k vs 115k context tokens.
- **Limitations:**
  - DMR is small, ambiguous, and fits in context (stated).
  - MemGPT could not be run on LongMemEval and its DMR numbers could not be reproduced (stated).
  - Regression on single-session-assistant questions (stated).
  - Latency measurements were not like-for-like (stated).
  - Vendor-authored, with no ablation of the bi-temporal model specifically (assessment).
- **Code availability:** not verified; no paper-specific link on the arXiv page
- **Unresolved research gaps:**
  - Isolating the value of temporal invalidation.
  - Cost of graph maintenance at scale.
  - Benchmarks that mix conversation with structured business data (stated future work).

## 9. HippoRAG

- **Title:** HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models
- **Authors:** Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su
- **Venue:** NeurIPS 2024, per the arXiv comments field
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2405.14831
- **Core contribution:** Long-term memory modeled on hippocampal indexing theory. An LLM builds a schemaless knowledge graph from passages, playing the role of the neocortex. Personalized PageRank over that graph, seeded by query entities, plays the role of the hippocampal index and enables single-step multi-hop retrieval.
- **Methodology:**
  - Offline indexing: OpenIE triples are extracted by an LLM, and synonym edges are added via a retrieval encoder.
  - Online: query named entities are linked to graph nodes, PPR is run, and node scores are aggregated onto passages.
- **Datasets/benchmarks:** MuSiQue, 2WikiMultiHopQA, HotpotQA.
- **Evaluation metrics:** Passage Recall@2 and Recall@5, plus QA EM and F1. Up to 20% better than prior RAG on multi-hop QA; 10–30x cheaper and 6–13x faster than iterative retrieval such as IRCoT, per the abstract.
- **Limitations:**
  - Errors in OpenIE extraction and entity linking propagate (stated in the error analysis).
  - It is a retrieval method for static corpora rather than agent memory under streaming updates. It underperforms dense retrieval on simple factual recall, as HippoRAG 2 later shows (assessment).
- **Code availability:** https://github.com/OSU-NLP-Group/HippoRAG (linked from arXiv)
- **Unresolved research gaps:**
  - Incremental graph updates for agents that write memory continuously.
  - Episodic and temporal structure.
  - Robustness to noisy, conversational input.

## 10. HippoRAG 2

- **Title:** From RAG to Memory: Non-Parametric Continual Learning for Large Language Models
- **Authors:** Bernal Jiménez Gutiérrez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su
- **Venue:** ICML 2025, per the arXiv comments field
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2502.14802
- **Core contribution:** Recasts RAG as *non-parametric continual learning*. HippoRAG 2 is the first structure-augmented RAG method in this comparison to beat strong dense retrievers on factual, associative, and sense-making memory tasks together; earlier graph RAG methods fell behind on simple factual QA.
- **Methodology:**
  - Passage nodes are integrated into the PPR graph alongside phrase nodes.
  - Queries are linked to triples, not just entities.
  - An LLM recognition-memory filter prunes the retrieved triples.
  - Extraction and filtering use Llama-3.3-70B; retrieval uses NV-Embed-v2.
- **Datasets/benchmarks:**
  - Simple QA: NaturalQuestions, PopQA.
  - Multi-hop: MuSiQue, 2WikiMultihopQA, HotpotQA, LV-Eval.
  - Discourse: NarrativeQA.
- **Evaluation metrics:**
  - Passage Recall@5 and token F1 (EM in the appendix).
  - Average F1 59.8 vs 57.0 for NV-Embed-v2.
  - About 7% gain on associative tasks, per the abstract.
- **Limitations:**
  - The triple filter's precision has room to improve; 18% of samples have zero triples after filtering, and about half of the remaining errors come from the PPR step (stated, error analysis).
  - Episodic memory for long conversations is left to future work (stated).
  - Evaluated on document QA, not on interactive agent tasks (assessment).
- **Code availability:** https://github.com/OSU-NLP-Group/HippoRAG (linked from arXiv)
- **Unresolved research gaps:**
  - Episodic and temporal memory.
  - Write-heavy agent workloads.
  - Whether "continual learning" holds under contradictory updates; the paper does not test knowledge revision.

## 11. MemoryOS

- **Title:** Memory OS of AI Agent
- **Authors:** Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai
- **Venue:** EMNLP 2025 (main conference, oral), per the authors' GitHub README; I did not locate the ACL Anthology entry.
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2506.06326
- **Core contribution:** An OS-inspired, three-tier personal memory with explicit promotion policies between tiers, aimed at personalized long-term dialogue agents.
- **Methodology:**
  - Short-term memory holds dialogue pages.
  - Promotion from short-term to mid-term is FIFO along a dialogue chain.
  - Mid-term memory uses segmented pages, with heat-based promotion to long-term memory.
  - Long-term memory holds the user persona and knowledge.
  - Four modules: storage, updating, retrieval, and generation.
- **Datasets/benchmarks:** LoCoMo and GVD (MemoryBank's simulated 15-user, 10-day dialogues).
- **Evaluation metrics:**
  - LoCoMo: F1 and BLEU-1. The abstract reports +49.11% F1 and +46.18% BLEU-1 average improvement with GPT-4o-mini.
  - GVD: retrieval accuracy, correctness, and coherence, scored automatically by DeepSeek-R1.
  - Efficiency: LLM calls and recalled tokens.
- **Limitations:**
  - No dedicated limitations section. Retrieving more pages adds noise (stated, hyperparameter analysis).
  - LLM-judged GVD scores, and a re-implemented A-MEM baseline whose numbers differ from the original. Promotion thresholds are hand-tuned (assessment).
- **Code availability:** https://github.com/BAI-LAB/MemoryOS (linked from arXiv)
- **Unresolved research gaps:**
  - Learned promotion and eviction policies.
  - Evaluation beyond chit-chat personalization, for example on task agents.

## 12. LoCoMo

- **Title:** Evaluating Very Long-Term Conversational Memory of LLM Agents
- **Authors:** Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, Yuwei Fang
- **Venue:** ACL 2024 (Long Papers), pp. 13851–13870, Anthology ID 2024.acl-long.747
- **Year:** 2024
- **Link:** https://aclanthology.org/2024.acl-long.747 ; https://arxiv.org/abs/2402.17753
- **Core contribution:** The LoCoMo dataset and benchmark of very long multi-session dialogues. It has become the de facto evaluation set for conversational agent memory; Mem0, A-MEM, MemoryOS, and Memory-R1 all report on it.
- **Methodology:**
  - LLM agents grounded in personas and temporal event graphs generate dialogues, including image sharing.
  - Human annotators verify and edit the dialogues for long-range consistency.
  - Dataset size differs by version. The ACL Anthology abstract states about 600 turns and 16K tokens on average over up to 32 sessions. The arXiv v1 abstract states about 300 turns and 9K tokens over up to 35 sessions. Cite the version you use.
- **Datasets/benchmarks:** LoCoMo, with three tasks:
  - QA: single-hop, multi-hop, temporal, open-domain, adversarial.
  - Event-graph summarization.
  - Multimodal dialogue generation.
- **Evaluation metrics:** QA F1; ROUGE and FactScore-style metrics for summarization; generation metrics for dialogue.
- **Limitations:**
  - Long-context LLMs and RAG still lag far behind humans (stated finding).
  - Synthetic, LLM-generated dialogues. Only about 10 conversations are commonly used downstream. Lexical F1 is brittle, and the adversarial category is routinely dropped by later papers (assessment).
- **Code availability:** project page https://snap-research.github.io/locomo/ (linked from arXiv)
- **Unresolved research gaps:**
  - Realistic, non-synthetic long-term dialogue data.
  - Metrics robust to paraphrase without relying on an LLM judge.
  - Conversations that exceed modern context windows.

## 13. LongMemEval

- **Title:** LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory
- **Authors:** Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang, Dong Yu
- **Venue:** ICLR 2025, per the arXiv comments field
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2410.10813
- **Core contribution:**
  - A benchmark of 500 curated questions embedded in chat histories of scalable length. It tests five abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention.
  - A three-stage design framework for memory systems (indexing, retrieval, reading).
- **Methodology:**
  - Needle sessions are embedded among filler sessions to build histories at standard (S, about 115k tokens) and much longer (M) scales.
  - Proposed optimizations: session decomposition into rounds, fact-augmented key expansion for indexing, and time-aware query expansion.
- **Datasets/benchmarks:** LongMemEval (S, M, and oracle settings).
- **Evaluation metrics:** QA accuracy via an LLM judge, plus retrieval recall and NDCG for memory retrieval. Commercial assistants and long-context LLMs drop about 30% in accuracy on sustained interactions, per the abstract.
- **Limitations:**
  - Synthetic, user–assistant chat only.
  - Answers are LLM-judged.
  - Measures recall and reasoning over memory, not whether memory improves downstream task actions (assessment).
- **Code availability:** https://github.com/xiaowu0162/LongMemEval (linked from arXiv)
- **Unresolved research gaps:**
  - Memory evaluation for tool-using and task agents, not just chat.
  - Measuring abstention and knowledge-update correctness under adversarial updates.

## 14. MemoryAgentBench

- **Title:** Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions
- **Authors:** Yuanzhe Hu, Yu Wang, Julian McAuley
- **Venue:** ICLR 2026 (poster, per the ICLR 2026 virtual-conference page)
- **Year:** 2026 (arXiv Jul 2025)
- **Link:** https://arxiv.org/abs/2507.05257
- **Core contribution:** A benchmark that feeds information to memory agents *incrementally*, chunk by chunk, and tests four competencies: accurate retrieval (AR), test-time learning (TTL), long-range understanding (LRU), and selective forgetting (SF).
- **Methodology:**
  - Existing long-context datasets are restructured into multi-turn streams.
  - Two new datasets: EventQA (for AR) and FactConsolidation (for SF; later facts override earlier ones).
  - Evaluates long-context models, simple and embedding RAG, structure-augmented RAG (RAPTOR, GraphRAG, MemoRAG, HippoRAG-v2, Mem0, Cognee, Zep), and agentic memory systems (Self-RAG, MemGPT, MIRIX).
- **Datasets/benchmarks:**
  - AR: SH/MH-Doc QA, LongMemEval (S*), EventQA.
  - TTL: BANKING77, CLINC150, NLU, TREC Coarse/Fine, Movie Recommendation.
  - LRU: ∞Bench-Sum, DetectiveQA.
  - SF: FactConsolidation-SH/MH.
- **Evaluation metrics:** Accuracy, Recall@5 for recommendation, and F1 for summarization.
- **Limitations:**
  - Budget limited the set of memory agents evaluated (stated).
  - Multi-hop selective forgetting is unsolved; the best system reaches at most 28% on FC-MH (stated finding).
  - The streams are restructured static datasets, not real agent trajectories (assessment).
- **Code availability:** https://github.com/HUST-AI-HYZ/MemoryAgentBench (linked from the ICLR page)
- **Unresolved research gaps:**
  - Memory systems that handle overwrites and conflict resolution; this is the clearest open gap the benchmark exposes.
  - Memory benchmarks set in interactive environments.

## 15. Agent Workflow Memory

- **Title:** Agent Workflow Memory
- **Authors:** Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, Graham Neubig
- **Venue:** ICML 2025 (PMLR 267:63897–63911)
- **Year:** 2025 (arXiv Sep 2024)
- **Link:** https://proceedings.mlr.press/v267/wang25bx.html ; https://arxiv.org/abs/2409.07429
- **Core contribution:** Induces reusable *workflows* (abstracted sub-routines) from past agent trajectories and adds them to memory to guide future web-navigation tasks. This is procedural memory without code.
- **Methodology:**
  - An LLM induces workflows from successful trajectories, abstracting away example-specific values.
  - Offline mode induces workflows from training examples.
  - Online mode induces them on the fly from test queries, with self-evaluated success.
  - Workflows are appended to the agent's memory or prompt.
- **Datasets/benchmarks:** Mind2Web and WebArena (over 1,000 tasks across more than 200 domains).
- **Evaluation metrics:**
  - Mind2Web: element accuracy, action F1, step success rate, and task success rate.
  - WebArena: success rate and number of steps.
  - Relative success improvement of +24.6% on Mind2Web and +51.1% on WebArena.
- **Limitations:**
  - Online induction depends on noisy self-judged success.
  - Workflows accumulate without consolidation.
  - Tested only in web domains (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:**
  - Workflow library management (merging, deprecation).
  - Learning from failures; ReasoningBank (item 21) partly addresses this.
  - Cross-domain transfer.

## 16. MemoryLLM (parametric memory)

- **Title:** MEMORYLLM: Towards Self-Updatable Large Language Models
- **Authors:** Yu Wang, Yifan Gao, Xiusi Chen, et al.
- **Venue:** ICML 2024 (poster, per the ICML 2024 virtual-conference page; PMLR vol. 235)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2402.04624
- **Core contribution:** *Parametric/latent* memory. A fixed-size pool of memory tokens inside every transformer layer, about 1.07B parameters on Llama2-7B. New text is written into the pool by self-update, and old content is forgotten gradually and randomly, so knowledge is absorbed without gradient fine-tuning.
- **Methodology:**
  - The pool has 7,680 memory tokens per layer.
  - On update, the last K=256 memory tokens are processed together with the new context, and the outputs replace K randomly dropped tokens. Retention decays roughly exponentially.
  - Trained on C4 with objectives for knowledge incorporation, continuous context, and forgetting mitigation.
- **Datasets/benchmarks:**
  - Model editing: ZsRE and CounterFact.
  - Long context: LongBench subsets.
  - Knowledge retention: SQuAD and NaturalQA.
  - Integrity: up to 650k updates.
- **Evaluation metrics:** Editing efficacy, generalization, and specificity (harmonic-mean score); LongBench F1; retention accuracy against update steps.
- **Limitations:**
  - Retention falls below the theoretical decay bound after about 20 updates (stated).
  - Below base Llama2 under 4k context; weaker on Qasper; not instruction-tuned; large inference memory footprint (stated).
  - The abstract says "nearly a million" updates, while the integrity experiment covers 650k (assessment).
  - Not evaluated as memory inside an agent loop (assessment).
- **Code availability:** https://github.com/wangyu-ustc/MemoryLLM (linked from arXiv)
- **Unresolved research gaps:**
  - Combining latent memory with explicit retrievable memory.
  - Controllable or targeted forgetting, as opposed to random drops.
  - Use in interactive agents.

## 17. MEM1

- **Title:** MEM1: Learning to Synergize Memory and Reasoning for Efficient Long-Horizon Agents
- **Authors:** Zijian Zhou, Ao Qu, Zhaoxuan Wu, et al.
- **Venue:** ICLR 2026 (poster, per the ICLR 2026 virtual-conference page)
- **Year:** 2026 (arXiv Jun 2025)
- **Link:** https://arxiv.org/abs/2506.15841
- **Core contribution:** Trains agents end to end with RL to keep a *constant-size* internal state that merges memory consolidation and reasoning. Each turn the agent rewrites its state and discards the prior context, instead of appending the full history.
- **Methodology:**
  - At each turn the agent emits an updated internal state; earlier turns are pruned from the context.
  - Trained with outcome-reward RL.
  - Builds multi-objective long-horizon environments by composing existing datasets.
- **Datasets/benchmarks:** Internal retrieval QA, open-domain web QA, and multi-turn WebShop. Tasks are composed of multiple objectives, up to 16.
- **Evaluation metrics:**
  - Task accuracy/EM, peak token memory, and inference time.
  - MEM1-7B: 3.5x performance and 3.7x lower memory use vs Qwen2.5-14B-Instruct on 16-objective multi-hop QA (abstract).
- **Limitations:**
  - Needs verifiable outcome rewards, and the state is not inspectable as discrete facts.
  - Lossy consolidation may discard information needed later.
  - Synthetic composed tasks (assessment).
- **Code availability:** https://github.com/MIT-MI/MEM1 (linked from the ICLR page)
- **Unresolved research gaps:**
  - Hybrid designs: a learned compact state plus an external store for recoverable detail.
  - Reward design for open-ended tasks.
  - Auditability of learned memory.

## 18. AgentPoison

- **Title:** AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases
- **Authors:** Zhaorun Chen, Zhen Xiang, Chaowei Xiao, Dawn Song, Bo Li
- **Venue:** NeurIPS 2024 (poster, per the NeurIPS 2024 virtual-conference page)
- **Year:** 2024
- **Link:** https://arxiv.org/abs/2407.12784
- **Core contribution:** Presented as the first backdoor attack on generic and RAG-based LLM agents through their *long-term memory or knowledge base*. An optimized trigger makes poisoned demonstrations retrieved whenever the trigger appears, with no model training.
- **Methodology:** Trigger optimization is posed as a constrained problem: map triggered queries to a unique, compact region of embedding space, while keeping the trigger coherent and effective on the target action. A small number of malicious records is then injected.
- **Datasets/benchmarks:** Agent-Driver (autonomous driving), a ReAct knowledge-intensive QA agent, and EHRAgent (healthcare).
- **Evaluation metrics:**
  - Attack success rates at the retrieval, action, and end-target stages.
  - Benign accuracy.
  - Average ASR at least 80%, benign impact at most 1%, poison rate under 0.1% (arXiv abstract; headline numbers differ slightly between the arXiv and NeurIPS abstracts).
- **Limitations:**
  - Assumes the attacker can insert records into the memory or knowledge base (threat model, stated).
  - Defenses evaluated are limited.
  - Assumes a white-box or gray-box retriever for trigger optimization, though transfer is reported (assessment).
- **Code availability:** not verified. A repository is reported by secondary sources, but I did not see it linked on a page I fetched.
- **Unresolved research gaps:**
  - Certified or provenance-based defenses for agent memory.
  - Detecting triggers in embedding space.
  - Attacks on memory systems that consolidate or rewrite entries (Mem0- or A-MEM-style).

## 19. MINJA

- **Title:** Memory Injection Attacks on LLM Agents via Query-Only Interaction
- **Authors:** Shen Dong, Shaochen Xu, Pengfei He, et al.
- **Venue:** NeurIPS 2025 (poster, per the NeurIPS 2025 virtual-conference page)
- **Year:** 2025
- **Link:** https://arxiv.org/abs/2503.03704
- **Core contribution:** Shows that agent memory can be poisoned *without write access*. An ordinary user who only sends queries can plant malicious records that are later retrieved for a different victim's queries.
- **Methodology:**
  - "Bridging steps" logically connect a victim term to the malicious reasoning.
  - An indication prompt induces the agent to generate and store those steps.
  - Progressive shortening gradually removes the indication prompt, so the stored record looks benign.
- **Datasets/benchmarks:** EHRAgent (MIMIC-III, eICU), RAP on WebShop, and a memory-based QA agent on MMLU. Backbones: GPT-4 and GPT-4o.
- **Evaluation metrics:** Injection success rate (ISR), attack success rate (ASR), and utility drop (UD). Average ISR 98.2% and ASR 76.8% across settings.
- **Limitations:**
  - Assumes a shared memory bank across users, or that isolation can be bypassed (stated).
  - Defense evaluation covers only prompt-level detection with one judge model; ASR varies widely across victim–target pairs (stated).
  - No tests against memory systems with consolidation or provenance (assessment).
- **Code availability:** the arXiv comments say "Code released", but I saw no link. Not verified.
- **Unresolved research gaps:**
  - Per-user memory isolation that does not destroy cross-user learning.
  - Provenance and trust scoring on memory writes.
  - Defenses that hold under adaptive attackers.

## 20. Memory-R1

- **Title:** Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning
- **Authors:** Sikuan Yan, Xiufeng Yang, Zuchao Huang, et al.
- **Venue:** ACL 2026 (Long Papers), pp. 12805–12825, Anthology ID 2026.acl-long.583
- **Year:** 2026 (arXiv Aug 2025)
- **Link:** https://aclanthology.org/2026.acl-long.583/ ; https://arxiv.org/abs/2508.19828
- **Core contribution:** Replaces heuristic memory operations, such as Mem0's prompted ADD/UPDATE/DELETE/NOOP, with policies *learned by RL*.
- **Methodology:**
  - Two agents: a Memory Manager that learns the memory operations, and an Answer Agent that learns to filter retrieved memories and answer.
  - Each is trained separately with PPO or GRPO using outcome (answer-correctness) rewards.
  - Training uses only 152 LoCoMo QA pairs.
- **Datasets/benchmarks:** LoCoMo (in-distribution; adversarial category excluded), with zero-shot transfer to MSC and LongMemEval. Base models: LLaMA-3.1-8B and Qwen-2.5 3B/7B/14B.
- **Evaluation metrics:**
  - F1, BLEU-1, and LLM-as-a-Judge.
  - LoCoMo with LLaMA-3.1-8B and GRPO: F1 45.02 and J 62.74, vs the strongest baseline MemoryOS at 35.04 / 48.20.
- **Limitations:**
  - Dialogue-centric datasets only; multimodal extension is out of scope (stated).
  - The two agents are trained separately for stability; end-to-end multi-agent RL is left to future work (stated).
  - The paper is internally inconsistent on the context window used to build training data (24 vs 50 turns) (assessment).
- **Code availability:** not verified
- **Unresolved research gaps:**
  - Joint training of memory writing and reading.
  - Rewards for memory that pays off on future tasks rather than immediate QA.
  - Robustness of learned DELETE policies to poisoning.

## 21. ReasoningBank

- **Title:** ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory
- **Authors:** Siru Ouyang, Jun Yan, I-Hung Hsu, et al.
- **Venue:** ICLR 2026, per the arXiv comments field ("Accepted to ICLR 2026")
- **Year:** 2026 (arXiv Sep 2025)
- **Link:** https://arxiv.org/abs/2509.25140
- **Core contribution:**
  - Experiential memory that distills generalizable *reasoning strategies* from both successful and failed trajectories, which the agent judges itself, rather than storing raw trajectories (as Synapse does) or only successful workflows (as AWM does).
  - Memory-aware test-time scaling (MaTTS), which uses extra rollouts to produce contrastive experience for memory.
- **Methodology:**
  - Each memory item has a title, a description, and content.
  - Items are retrieved by embedding (gemini-embedding-001).
  - New items are extracted after each task using LLM-as-judge success labels and appended to the bank.
  - MaTTS comes in parallel and sequential variants.
- **Datasets/benchmarks:** WebArena (684 tasks; the Map domain is excluded), Mind2Web, and SWE-Bench-Verified. Backbones: Gemini-2.5-flash/pro and Claude-3.7-sonnet.
- **Evaluation metrics:**
  - Success rate and steps; Mind2Web element accuracy, action F1, and step success rate; SWE-Bench resolve rate.
  - WebArena SR +8.3 points over no memory with Gemini-2.5-flash.
  - Up to 16% fewer steps.
- **Limitations:**
  - The paper has a limitations appendix that I could not read in the fetched text, so its stated limitations are not verified.
  - Depends on noisy LLM self-judgment of success. The memory bank only grows and has no consolidation. Gains over AWM are modest in some settings (assessment).
- **Code availability:** https://github.com/google-research/reasoning-bank (linked from arXiv)
- **Unresolved research gaps:**
  - Memory quality control as the bank grows.
  - Transfer of strategy memory across benchmarks and backbones.
  - Interaction with poisoning: failed trajectories as an attack surface.

---

## Surveys (cite as surveys)

### S1. Zhang et al. survey

- **Title:** A Survey on the Memory Mechanism of Large Language Model based Agents
- **Authors:** Zeyu Zhang, Xiaohe Bo, Chen Ma, et al.
- **Venue:** ACM Transactions on Information Systems (TOIS). Accepted 2025-07-02 per the authors' GitHub README. DOI not verified; one aggregator lists 10.1145/3748302, which I did not confirm on ACM DL.
- **Year:** 2024 (arXiv); accepted at TOIS 2025
- **Link:** https://arxiv.org/abs/2404.13501
- **Core contribution:** A survey of what agent memory is, why agents need it, how memory modules are designed (sources, forms, operations) and evaluated, and memory-centric applications.
- **Methodology:** Literature survey and taxonomy.
- **Datasets/benchmarks:** n/a. It catalogs evaluation approaches.
- **Evaluation metrics:** n/a. It catalogs direct and indirect memory evaluation.
- **Limitations:** Its coverage ends in early 2024, so it predates the 2025 wave of RL-trained memory, MemoryAgentBench, and memory-poisoning work (assessment).
- **Code availability:** https://github.com/nuster1128/LLM_Agent_Memory_Survey (paper list, linked from arXiv)
- **Unresolved research gaps:** The authors list future directions including parametric memory, multi-agent memory, and lifelong learning (stated).

### S2. Hu et al. survey

- **Title:** Memory in the Age of AI Agents. This is the title on the arXiv abstract page; secondary sources give a longer subtitle, "A Survey: Forms, Functions and Dynamics", that I did not confirm on the abstract page.
- **Authors:** Yuyang Hu, Shichun Liu, Yanwei Yue, et al. (47 authors)
- **Venue:** arXiv preprint
- **Year:** 2025 (v1 Dec 2025; v2 Jan 2026)
- **Link:** https://arxiv.org/abs/2512.13564
- **Core contribution:** A recent survey that organizes agent memory along three lenses:
  - Forms: token-level, parametric, and latent.
  - Functions: factual, experiential, and working memory.
  - Dynamics: how memory is formed, evolves, and is retrieved.
- **Methodology:** Literature survey and taxonomy, with compiled benchmarks and frameworks.
- **Datasets/benchmarks:** n/a (catalog)
- **Evaluation metrics:** n/a
- **Limitations:** A broad, many-author survey whose taxonomy is not yet peer-reviewed (assessment).
- **Code availability:** not verified. A companion paper-list repository is reported by secondary sources but was not linked on the arXiv page.
- **Unresolved research gaps:** The authors highlight memory automation, RL integration, multimodal memory, multi-agent memory, and trustworthiness (stated, per the abstract and secondary summaries).

---

## Recurring weaknesses in this slice (my assessment)

1. **Evaluation rests on one small, synthetic benchmark.** Most conversational-memory systems report mainly on LoCoMo: about 10 LLM-generated conversations, with dataset statistics that differ between its arXiv and ACL versions. They also routinely drop LoCoMo's adversarial category.
   - Applies to: Mem0 (7), A-MEM (6), MemoryOS (11), Memory-R1 (20), LoCoMo (12).
   - Results are hard to compare and probably overfit to this benchmark.
2. **Lexical metrics and LLM judges replace grounded evaluation.** F1 and BLEU-1 penalize correct paraphrases. LLM-as-judge scores depend on the judge, and the judge is sometimes unnamed.
   - Applies to: Mem0 (7), A-MEM (6), MemoryOS (11; DeepSeek-R1 judge), Memory-R1 (20), LongMemEval (13), Zep (8).
3. **Baselines are inconsistent and not reproducible.** Re-implemented baselines give different numbers from the originals, and vendor papers benchmark competitors.
   - Applies to: MemoryOS's A-MEM* (11); Zep's MemGPT, which could not be run or reproduced (8); Mem0 vs Zep and OpenAI memory (7).
4. **Memory grows without bound and forgetting is barely evaluated.** Most systems only append. Where forgetting exists, it is heuristic (an Ebbinghaus curve, random token drops). When forgetting is tested directly, multi-hop overwrite accuracy is at most 28%.
   - Applies to: Generative Agents (1), Voyager (4), ExpeL (5), AWM (15), ReasoningBank (21), MemoryBank (3), MemoryLLM (16).
   - The direct test: MemoryAgentBench (14).
5. **Memory writes depend on noisy LLM self-judgment.** Success labels, insight extraction, link generation, and UPDATE/DELETE decisions are made by the same LLM. Errors are written into memory and compound, and no paper measures memory corruption over time.
   - Applies to: ExpeL (5), AWM (15, online mode), ReasoningBank (21), A-MEM (6), Mem0 (7), Zep (8).
6. **Security is tested separately from the memory architectures that matter.** Poisoning attacks target simple retrieval-augmented memory banks. Proposed memory systems almost never evaluate adversarial writes, and defenses are thin (prompt-level detection only).
   - Attacks: AgentPoison (18), MINJA (19).
   - Systems that never evaluate adversarial writes: 6–8, 11, 20, 21.
7. **Recall is measured, not downstream agent utility.** Conversational-memory work scores QA over past dialogue, not whether memory improves actions in tasks. Task-memory work, in turn, ignores long-term factual recall. The two communities rarely share benchmarks.
   - Conversational side: 6–8, 11–13, 20. Task side: 4, 5, 15, 17, 21.
8. **Parametric and non-parametric memory are studied in isolation.** Latent or learned-state memory is never compared head to head with external memory on the same agent tasks.
   - Parametric/learned state: MemoryLLM (16), MEM1 (17). External memory: everything else.
   - S2 names the gap but offers no empirical comparison.

## Open problems that a small team could attack (my assessment)

1. **Memory-under-attack benchmark for real memory systems.** Run AgentPoison- and MINJA-style query-only injection against Mem0, A-MEM, Zep/Graphiti, MemoryOS, and an RL-trained manager. The attacks are already published and most of these systems have open code. Then measure whether consolidation operations (UPDATE/DELETE, memory evolution, temporal invalidation) amplify or dampen poisoning. Cheap to run, and it addresses weakness 6.
2. **Measuring memory corruption over long horizons.** Instrument an agent over thousands of writes and track how far stored memories drift from ground truth: wrong merges, overwritten facts, hallucinated links. Test whether provenance tags or periodic re-verification reduce drift. No paper above measures corruption directly (weakness 5).
3. **Selective forgetting and conflict resolution as a first-class method.** MemoryAgentBench shows multi-hop fact consolidation is essentially unsolved. A small team could build a targeted method and evaluate it on FactConsolidation and LongMemEval knowledge-update questions. Candidate methods: bi-temporal validity like Zep's combined with retrieval that propagates supersession across multi-hop chains, or a small RL-trained conflict resolver in the style of Memory-R1.
4. **Paraphrase-robust, judge-light evaluation for conversational memory.** Re-score published systems on LoCoMo and LongMemEval with several open judges plus human spot checks, and report variance. This would show how much of the claimed gains in items 6, 7, 11, and 20 survive changing the metric and judge (weaknesses 1–3).
5. **Hybrid learned-state plus external-store agent.** Combine a MEM1-style constant-size RL-trained working state with an append-only external archive that the agent can query to recover discarded detail. Evaluate on both conversational recall (LongMemEval) and task suites (WebShop, WebArena subsets) to bridge weaknesses 7 and 8 at 3B–7B scale.
6. **Experiential memory quality control.** For ReasoningBank- and AWM-style strategy memory, study pruning, merging, and contradiction detection as the bank grows. Measure whether a bounded, curated memory matches or beats an unbounded one on WebArena and Mind2Web.

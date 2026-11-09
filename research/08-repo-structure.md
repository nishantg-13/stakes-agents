# 08 — Suggested Repository Structure

Suggested as a **separate repo**, e.g. `~/stakes-agents/`, rather than inside agent-studio, so it
can be made public cleanly. This is a plan only; nothing has been created yet.

```text
stakes-agents/
├── README.md                     # what, how to reproduce, citation
├── LICENSE                       # Apache-2.0 or MIT
├── pyproject.toml                # uv-managed; pinned deps
├── Makefile                      # make pilot | fit | run-rq1 | run-rq2 | table1 … figures
├── configs/
│   ├── models/                   # gemini_flash.yaml, gemini_pro.yaml, open_8b.yaml (vLLM endpoint)
│   ├── envs/                     # tau2_airline.yaml, tau2_retail.yaml, appworld.yaml, ledgerworld.yaml
│   ├── strategies/               # single, uniform_vote, verify_writes, unc_only, stakes, oracle
│   └── experiments/              # rq1.yaml, rq2.yaml … (grid = env × model × strategy × λ × seeds)
├── registries/                   # effect-type YAML per environment + labelling notes
│   ├── tau2_airline.yaml
│   └── …
├── src/stakes/
│   ├── types.py                  # EffectType enum, ToolCall, Step, Trajectory dataclasses
│   ├── effects/registry.py       # EffectRegistry (+ state-dependent hooks)
│   ├── effects/llm_typer.py      # LLM-based effect classifier (RQ5)
│   ├── estimate/canon.py         # Canonicalizer
│   ├── estimate/disagreement.py  # p̂ from k0 samples; logprob / verbalised variants
│   ├── operators/{vote,readback,verify,ask}.py
│   ├── allocator/voc.py          # Algorithm 1 + modes (uniform, unc-only, stakes-only, rule)
│   ├── allocator/pacing.py       # Algorithm 2
│   ├── fit/offline.py            # Algorithm 3: φ, κ, empirical C on dev split
│   ├── ledger.py                 # tool-call wrapper, DB diffs, gold matching
│   ├── budget.py                 # token/USD accounting from provider usage fields
│   ├── llm/{gemini.py,vllm.py}   # thin clients, retry/backoff, response caching
│   ├── envs/{tau2.py,appworld.py,agentabstain.py,ledgerworld/}
│   └── runner.py                 # resumable, content-hash-cached episode runner
├── ledgerworld/                  # generator, services, task templates, frozen test seeds
├── eval/
│   ├── metrics.py                # pass^k, pass@k, IER, dup-rate, harm utility, frontier AUC
│   ├── stats.py                  # bootstrap, paired permutation, Holm
│   └── tables.py                 # results/*.jsonl → paper tables (no hand-copying)
├── analysis/                     # notebooks: pilot, frontiers, step-class decomposition, error taxonomy
├── tests/                        # unit tests: canon, metrics, ledger, allocator edge cases
├── results/                      # gitignored raw JSONL; small summaries committed
├── paper/                        # LaTeX (workshop/ and main/), figures/, bib/
└── docs/
    ├── decisions.md              # A-### assumptions, D-### decisions (your state-protocol)
    └── protocol.md               # pre-registered RQs, primary metric, splits
```

Design rules:
- **Every LLM call goes through `llm/`.** It logs the prompt hash, the model ID, the usage
  fields, and latency.
- **`runner.py` writes one JSONL line per step**, and is idempotent: rerunning skips finished
  episodes.
- **Strategies are configuration, not code forks.** All baselines are modes of `allocator/voc.py`,
  which guarantees identical plumbing across conditions.
- **Tests come before scale.** The metric and ledger tests must pass before any paid run.

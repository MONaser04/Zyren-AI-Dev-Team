# Žyren Multi-Agent Swarm Scaffolds & Runtime Tooling

This directory contains the production configuration schemas, operational prompts, and runtime-agnostic code intelligence tools for the **Žyren Autonomous Engineering Collective**.

---

## Directory Overview

```text
scaffolds/
├── opencode/                       # 👑 Generation 5: OpenCode V2 Production Runtime (Active)
│   ├── opencode.example.jsonc      # Complete OpenCode V2 configuration schema
│   ├── AGENTS.md                   # OpenCode V2 operational mandates & persistent session protocol
│   ├── zyren-sessions.example.md   # Persistent session registry template
│   ├── commands/                   # Direct fast-path commands (/build, /audit, /plan, /research)
│   └── README.md                   # Deployment and usage guide
│
├── tools/                          # 💎 Code Intelligence Engine (Cross-Platform Python CLI)
│   ├── code_outline.py             # Zero-dependency AST outline engine (96.2% token savings)
│   ├── code_graph.py               # Static cross-file caller and blast radius gate
│   ├── code_search.py              # Two-stage semantic search (NVIDIA Nemotron Embed & Rerank)
│   └── README.md                   # CLI options, caching, and examples
│
└── openclaw/                       # 📦 Generation 3 & 4: Archived OpenClaw / ŽyrenClaw Baseline
    ├── openclaw.example.json       # Legacy 5-agent OpenClaw collective config
    ├── AGENTS.md                   # Legacy OpenClaw v4.0 workspace specification
    ├── SOUL.md                     # Coordinator operational philosophy & LangClaw hooks
    ├── CRITIC_SOUL.md              # Zero-trust deterministic runtime critic contract
    ├── scripts/                    # Legacy Windows daemon & wrapper scripts
    └── README.md                   # Historical archive notes
```

---

## Navigation

- **Active Production Runtime (Gen 5 — Recommended):** [`scaffolds/opencode/README.md`](./opencode/README.md) — streamlined TypeScript daemon + Desktop/CLI harness with progressive skill disclosure and persistent child sessions.
- **Code Intelligence Utilities:** [`scaffolds/tools/README.md`](./tools/README.md) — standalone Python CLI tools compatible with any execution harness.
- **Archived Baseline (Gen 3/4):** [`scaffolds/openclaw/README.md`](./openclaw/README.md) — historical OpenClaw reference retained for reproducibility of the Gen 3/4 canary benchmarks.

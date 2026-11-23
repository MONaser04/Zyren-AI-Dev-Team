# Žyren Multi-Agent Swarm Scaffolds & Runtime Tooling

This directory contains the production configuration schemas, operational prompts, and code intelligence tooling across the architectural generations of the **Žyren Autonomous Engineering Collective**.

---

## Directory Overview

```
scaffolds/
├── opencode/                    # 👑 Generation 5: OpenCode V2 Production Runtime (Current)
│   ├── opencode.example.jsonc   # Complete OpenCode V2 configuration schema
│   ├── AGENTS.md                # OpenCode V2 operational mandates & session protocol
│   ├── zyren-sessions.example.md# Persistent session registry template
│   ├── commands/                # Direct fast-path commands (/build, /audit, /plan, /research)
│   └── README.md                # Deployment and usage guide
│
├── tools/                       # 💎 Code Intelligence Engine (Cross-Platform CLI)
│   ├── code_outline.py          # Zero-dependency AST outline engine (96.2% token savings)
│   ├── code_graph.py            # Static cross-file caller and blast radius gate
│   └── code_search.py           # Two-stage semantic code search (Gemini Embed 2 + Nemotron Rerank)
│
├── openclaw.example.json        # ⚙️ Generation 3 & 4: OpenClaw / ŽyrenClaw Collective Config
├── AGENTS.md                    # Generation 4: OpenClaw v4.0 Specification & Soul
├── SOUL.md                      # Operational philosophy and Conway's Law alignment
├── CRITIC_SOUL.md               # Zero-trust deterministic runtime critic contract
└── scripts/                     # OpenClaw Gateway Daemon Scripts
    ├── ensure-gateway.js        # Health check and background daemon supervisor
    └── zyrenclaw.ps1            # Native PowerShell wrapper and CLI entrypoint
```

---

## Active Generation Guidance

- **For New Deployments (Recommended):** Use [`scaffolds/opencode/`](file:///D:/PROJECTS/ZYREN_CASE_STUDY/scaffolds/opencode/README.md). It represents the state-of-the-art **Generation 5** autonomous coding runtime, delivering 100% execution fidelity, progressive skill disclosure, and zero daemon collapses on OpenCode V2.
- **For OpenClaw Environments:** Refer to `openclaw.example.json` and root `AGENTS.md` for the historical **Generation 3/4** gateway baseline.
- **For Tooling:** The scripts in [`tools/`](file:///D:/PROJECTS/ZYREN_CASE_STUDY/scaffolds/tools) are runtime-agnostic Python utilities compatible with both OpenCode and OpenClaw environments.

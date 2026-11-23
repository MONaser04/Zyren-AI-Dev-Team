# ŽyrenClaw — Archived Generation 3 & 4 OpenClaw Reference (`scaffolds/openclaw/`)

> **Archived Baseline:** This directory preserves the historical **Generation 3/4 OpenClaw** configuration, persona mandates, and gateway daemon wrappers used during the early ŽyrenClaw canary benchmarks (`modern-fruit-catcher`, `cat-playground`, `neon-void`).  
> **For new deployments, use [`../opencode/README.md`](../opencode/README.md) (Generation 5 — OpenCode V2).**

---

## Contents

| Artifact | Purpose |
|---|---|
| [`openclaw.example.json`](./openclaw.example.json) | 5-agent Hub-and-Spoke configuration schema for OpenClaw (`gateway`, NVIDIA NIM providers, cross-model critic) |
| [`AGENTS.md`](./AGENTS.md) | Workspace & v4.0 collective specification (Vertical Slicing, Two-Strike budget, Circuit Breakers) |
| [`SOUL.md`](./SOUL.md) | Coordinator persona (`zyren-dev-team`), Phase 1/Phase 2 operating rules, and LangClaw checkpoint hooks |
| [`CRITIC_SOUL.md`](./CRITIC_SOUL.md) | Zero-trust deterministic quality gate contract (`zyren-critic`) |
| [`scripts/ensure-gateway.js`](./scripts/ensure-gateway.js) | Port `18789` HTTP watchdog and SQLite self-heal launcher |
| [`scripts/zyrenclaw.ps1`](./scripts/zyrenclaw.ps1) | PowerShell CLI wrapper delegating commands to `openclaw.mjs` |

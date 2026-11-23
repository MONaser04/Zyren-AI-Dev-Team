# Žyren Empirical Benchmarks & Audit Artifacts

This directory houses the self-contained empirical benchmarks produced autonomously by the **Žyren 5-Agent Collective**, alongside the deterministic Critic audit reports and session traces that verified each delivery.

---

## Generation 5 — OpenCode V2 (Active Production Harness)

- **[`task-cli/`](./task-cli/)** — Zero-dependency Python CLI task manager built end-to-end on OpenCode V2 (`v2.2.7`) with zero human code edits:
  - Architectural blueprint: [`task-cli/DESIGN.md`](./task-cli/DESIGN.md) (616 lines, authored by `zyren-planner`)
  - Auditable multi-agent trace: [`task-cli/SESSION_TRACE.md`](./task-cli/SESSION_TRACE.md) (research → design → 8-file implementation → Critic `REVISE` interception → same-session fix → `APPROVED`)
  - Usage & package docs: [`task-cli/README.md`](./task-cli/README.md)

---

## Generation 4 — OpenClaw Baseline (Vertical-Slice Calibration Microcosms)

Interactive WebGL/Canvas2D microcosms used to calibrate Vertical Feature Slicing, Conway-aligned full-stack synthesis, and closed-loop Critic verification:

- **[`modern-fruit-catcher/`](./modern-fruit-catcher/)** — 2D Canvas glassmorphism arcade game verifying multi-iteration autonomous playtest refactors:
  - [`audit-report.md`](./modern-fruit-catcher/audit-report.md)
  - [`critic-audit-report.md`](./modern-fruit-catcher/critic-audit-report.md)
- **[`cat-playground/`](./cat-playground/)** — Interactive 3D WebGL (Three.js + Cannon.js) physics landing page verifying zero-trust defect interception and durable self-learning crystallization:
  - [`_audit/REPORT.md`](./cat-playground/_audit/REPORT.md) (and portable audit scripts `extract.js`, `phase2.js`, `phase3.js`)
  - [`learning-memory-2026-10-23.md`](./cat-playground/learning-memory-2026-10-23.md)
- **[`neon-void/`](./neon-void/)** — 2D twin-stick arcade survival game built under a zero-instruction 15-minute sprint, catching and repairing a boot-time render loop blocker before delivery:
  - [`critic-audit.md`](./neon-void/critic-audit.md)

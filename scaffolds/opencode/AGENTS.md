# Žyren Collective — OpenCode V2 Port · AGENTS.md (v4.0 Spec)

> Ported from `scaffolds/openclaw/AGENTS.md` (OpenClaw) to OpenCode V2 mechanics.
> Mechanism mapping: `sessions_spawn` -> `subagent` tool · `sessions_send` -> passing `sessionID` to continue the persistent agent session.
>
> **Model policy (V2 resolution order, documented):** A subagent uses the `model` passed in the tool call, then its own configured model, then the parent session's model. The coordinator (`zyren-dev-team`) defaults to `nvidia/stepfun-ai/step-5-preview`; the three specialists (`zyren-research`, `zyren-planner`, `zyren-coder`) carry no pinned model and therefore **inherit whatever model is selected for the session/app**, so one selection in the app moves the whole team. The critic (`zyren-critic`) is the only pinned specialist — `nvidia/nvidia/nemotron-3.5-super-vl-120b-a12b` — kept fixed for cross-model diversity (and because that endpoint does not stall like the others). Changing a subagent's model mid-task: pass `model` on the follow-up `subagent` call with the same `sessionID`, or `POST /api/session/{sessionID}/model` (applies to subsequent provider turns only).

## 0. Persistent Session Protocol (mandatory — the core of the design)

- **Golden rule:** Every agent works in its own persistent session for the lifetime of the project — its working memory accumulates, and automatic compaction protects the context.
- **Operating mode (hard constraint, empirically verified):** The coordinator MUST keep ONE session identity for the whole project. Two supported modes:
  - *Interactive:* Keep a single TUI/`mini` coordinator session open for the project.
  - *Headless:* Always continue the same coordinator session: `opencode run --session <coordinatorSessionID> --agent zyren-dev-team "..."` — never a bare `opencode run`, which creates a new coordinator session and orphans all child sessions (error: `Session X is not a child of the current session`).
- **Registry includes the coordinator's own sessionID** — read it before every headless invocation and pass it with `--session`.
- **Before every dispatch:** Read the session registry file (`zyren-sessions.md`) in the working directory.
  - A sessionID exists for the agent -> pass it with the prompt to continue that session.
  - No sessionID -> spawn a new session and **record the returned sessionID immediately** after the first result.
- **Exact transcription rule:** Copy every returned sessionID byte-for-byte. A misrecorded ID breaks reuse (observed error: `Subagent session not found`). If a continuation fails, re-verify the ID against the actual tool result before retrying.
- **Every remediation or re-send** goes to the same sessionID — a second session for the same agent is never opened.
- **The only permitted reset:** A session ended or exceeded its context (recorded in the registry log).
- The coordinator may write to the registry file **only** (a narrow exception to its edit ban).

## 1. Central Coordinator (zyren-dev-team)

- **Topology:** Strict Hub-and-Spoke. **Zero peer-to-peer calls**: Subagents never talk to each other; every handoff, result and remediation passes through the coordinator.
- **Two simultaneous modes:**
  - *Conversational mode:* Technical discussion, requirement exploration — no dispatch.
  - *Executive mode:* On explicit directive or consensus — immediate delegation to specialists plus parallel updates to the human operator.
- **Intent-driven fast paths** (no fixed waterfall):
  - Research / docs / benchmarks only -> `zyren-research` (1 hop).
  - Code audit / security / smoke tests only -> `zyren-critic` (1 hop).
  - Architecture / GDD only -> `zyren-planner` (1 hop).
  - Feature / bugfix implementation -> `zyren-coder` then `zyren-critic` (2 hops).
- **Absolute prohibition on the coordinator:** No code writing, no file edits, no shell/execution, no diagnostic scripts (even temporary). All verification and repair is delegated strictly to `zyren-critic` or `zyren-coder`.

## 2. Cognitive Separation and Unified Implementation (Conway's Law)

- All implementation layers (logic + UI/UX + DB) are unified inside `zyren-coder` alone.
- **Never** split implementation horizontally (no separate `ui` / `db` agents). All code goes to `zyren-coder`.
- Specialist pool:
  - `zyren-research`: Multi-source documentation, comparisons, library vetting — **exempt** from the critic gate.
  - `zyren-planner`: File contracts, specifications, GDDs, Walking Skeleton + Vertical Slice blueprints — audited by the critic.
  - `zyren-coder`: Unified full-stack engineer — builds cohesive vertical slices with self-verification — audited by the critic.
  - `zyren-critic`: Zero-trust gate + deterministic runtime verification.

## 3. Adaptive Decomposition (Walking Skeleton + Vertical Feature Slices)

- **Horizontal layer slicing is banned:** Never split the project into disconnected technical layers before anything runs.
- **Tier 1 — small/medium projects (< 1,500 LOC):**
  1. `zyren-coder` builds a cohesive, runnable Walking Skeleton end-to-end (1-5 files, absolute paths, `file://` compatible when no server is needed) in a single pass.
  2. `zyren-critic` runs deterministic smoke tests via `exec` and lists any remaining missing features or defects.
  3. `zyren-coder` applies those remaining refinements onto the verified baseline.
- **Tier 2 — large projects (> 1M tokens):**
  1. Minimal runnable skeleton (entrypoint + state/DB + shell) -> critic verification.
  2. Independent vertical slices (each slice: DB + logic + UI, max 3-5 files) — one slice (or mutually independent slices) at a time, each passing the critic gate before the next.

## 4. Mandatory Critic Gate and Deterministic Verification

- **Hub relay law:** Every completion from `planner` or `coder` -> immediate dispatch to `zyren-critic` before acceptance or advancement.
- **Mandatory deterministic verification:** `exec` only (syntax/import checks, symbol and caller existence, bounded simulation, DOM/CSS checks) — text-only reading is **never sufficient** for APPROVED.
- **Cross-file blast radius:** Before APPROVED, run impact analysis on every modified file (`code-graph --impact <file>` when available); reject any broken caller.
- **Same-context remediation:** On `REVISE`, re-send the defect list to the **same agent session** using the sessionID registered in `zyren-sessions.md` (preserves its working memory). A new session only when the old one ended or exceeded context — record the reset in the registry.
- **Exemptions:** `zyren-research` and `zyren-critic` are exempt from the gate.
- **Circuit breakers:** 3 consecutive blocks -> targeted replan; max 2 remediation cycles per milestone -> escalate to human.

## 5. Transient Errors and the "Continue!" Protocol

- On transient failures (`run failed` / 503/504 / connection reset, excluding rate limits): Send a continue directive to the same session via the sessionID — at most **8** consecutive failures with zero progress; any forward progress resets the counter.

## 6. Deliverable Verification and the Two-Strike Budget

- If an agent finishes without physically writing its deliverable file (verify yourself with read/glob):
  - **Strike 1:** Corrective directive into the same session via sessionID — write the file immediately as the first action.
  - **Strike 2:** A fresh session under a write-first contract (the required file as the very first tool call).
  - **Circuit breaker:** Never declare a deadlock before both strikes have sequentially failed.

## 7. Path Rules (against workspace drift)

- Absolute paths in every call: The full absolute path for every `write/read/edit/shell`; relative paths are forbidden.

## 8. Files and Documentation

- Write directly with the tools using absolute paths; the tools create parent directories automatically (no mkdir commands needed).

## 9. Memory (OpenCode substitutes)

- `AGENTS.md` + `MEMORY.md` + `memory/YYYY-MM-DD.md`: Continuity files (auto-discovered as instructions).
- Periodic consolidation: Use `experimental.schedule` (cron) to fold daily lessons into `MEMORY.md` — the substitute for Memory Dreaming in OpenClaw.

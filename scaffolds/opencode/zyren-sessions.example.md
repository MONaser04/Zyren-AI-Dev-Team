# Žyren Session Registry — Persistent Agent Session Log

> Read by the coordinator (`zyren-dev-team`) before every dispatch; the returned `sessionID` is written here after the first spawn.
> Rule: One agent = one persistent session for the lifetime of the project. A second session for the same agent is never opened.
> Operating mode: The coordinator keeps ONE session identity (interactive TUI, or `opencode run --session <coordinator ID>`). A bare `opencode run` per task orphans child sessions.

## Coordinator Session

| Role | sessionID | Notes |
|---|---|---|
| zyren-dev-team (coordinator) | `ses_replace_with_coordinator_id` | Interactive TUI or persistent headless session |

## Active Specialist Sessions

| Agent | sessionID | Last task | Notes |
|---|---|---|---|
| zyren-research | `ses_replace_with_research_id` | Technical documentation vetting | Spawns on first research fast path |
| zyren-planner | `ses_replace_with_planner_id` | Architectural design & Walking Skeleton blueprint | Spawns on first planning fast path |
| zyren-coder | `ses_replace_with_coder_id` | Full-stack vertical implementation | Reused across all implementation tasks |
| zyren-critic | `ses_replace_with_critic_id` | Deterministic runtime verification gate | Reused across all audit milestones |

## Update Log
- `YYYY-MM-DD` | `coordinator` | Initialized session registry for project.

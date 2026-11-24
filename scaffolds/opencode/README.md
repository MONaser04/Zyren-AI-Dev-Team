# Žyren Autonomous Engineering Collective — OpenCode V2 Scaffolds

This directory contains the production-grade deployment scaffolds for running the **Žyren 5-Agent Collective** inside **OpenCode V2 (v2.2.7+)**.

## Directory Layout

```
scaffolds/opencode/
├── opencode.example.jsonc       # Production OpenCode configuration (agents, surgical locks, NVIDIA NIM)
├── AGENTS.md                    # Operational mandates & Persistent Session Protocol (v4.0 spec)
├── zyren-sessions.example.md    # Template for persistent session continuity tracking
├── commands/                    # Direct fast-path commands (/build, /audit, /plan, /research)
│   ├── audit.md
│   ├── build.md
│   ├── plan.md
│   └── research.md
└── README.md                    # This deployment guide
```

---

## Deployment Options

### Option 1: Global Deployment (Available in All OpenCode Projects)
To make the Žyren collective available across every project on your workstation:
1. Copy `opencode.example.jsonc` to your user configuration directory:
   - **Windows:** `%USERPROFILE%\.config\opencode\opencode.jsonc` (or `C:\Users\<username>\.config\opencode\opencode.jsonc`)
   - **Linux / macOS:** `~/.config/opencode/opencode.jsonc`
2. Copy `commands/` to `%USERPROFILE%\.config\opencode\commands/` to enable global fast-paths (`/build`, `/audit`, `/plan`, `/research`).
3. Set your `NVIDIA_API_KEY` environment variable.

### Option 2: Project-Local Isolated Deployment
To isolate the collective strictly to a specific repository:
1. Create a `.opencode/` directory in your repository root.
2. Copy `opencode.example.jsonc` to `.opencode/opencode.jsonc`.
3. Copy `AGENTS.md` to `.opencode/AGENTS.md` (or your project root).
4. Copy `commands/` to `.opencode/commands/`.
5. Copy `zyren-sessions.example.md` to your project root as `zyren-sessions.md`.

---

## Architectural Principles & Rules

1. **Surgical Isolation:** 
   The configuration defines `zyren-*` agent IDs and places surgical permission locks on the default `build` and `plan` agents (`deny: "zyren-*"`), ensuring default OpenCode workflows remain unaffected.
2. **Model Inheritance Policy:**
   - The coordinator (`zyren-dev-team`) defaults to `nvidia/stepfun-ai/step-5-preview`.
   - The three specialists (`zyren-research`, `zyren-planner`, `zyren-coder`) carry **no pinned model** and dynamically inherit whatever model you select in the session/app.
   - The critic (`zyren-critic`) is **hard-pinned** to `nvidia/nvidia/nemotron-3.5-super-vl-120b-a12b` for mandatory cross-model cognitive diversity.
3. **Persistent Session Protocol (`zyren-sessions.md`):**
   One agent = one persistent session for the lifetime of the project. The coordinator reads the registry before every dispatch and passes the registered `sessionID` to preserve working context and eliminate orphaned sessions.
4. **Mandatory Deterministic Critic Gate:**
   `zyren-critic` verifies code via execution (`exec`) only. Text-only approval is strictly rejected.

---

## Running the Collective

### Interactive Desktop / TUI Mode
Select the `zyren-dev-team` agent from the agent picker in the OpenCode Desktop UI or start the TUI:
```powershell
opencode --agent zyren-dev-team
```

### Headless Autonomous Execution
Always maintain a single coordinator session identity across multi-step milestones:
```powershell
# First run: spawns the coordinator session
opencode run --agent zyren-dev-team "Design and build task-cli..."

# Subsequent runs: continue the existing coordinator session
opencode run --session <coordinatorSessionID> --agent zyren-dev-team "Apply next milestone..."
```

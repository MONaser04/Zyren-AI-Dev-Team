# Žyren Autonomous Engineering Collective — OpenCode V2 Scaffolds

This directory contains the production-grade deployment scaffolds for running the **Žyren 5-Agent Collective**, **Unified Microsoft UFO Computer Use (`gemini-3.8-live`)**, and **Structured LangGraph Tooling** inside **OpenCode V2 (v2.4+)**.

## Directory Layout

```
scaffolds/opencode/
├── opencode.example.jsonc       # Production OpenCode config (agents, locks, zyren-ufo & LangChain MCPs, NVIDIA NIM)
├── AGENTS.md                    # Operational mandates, Session Protocol (v4.0), Computer Use & LangGraph rules
├── zyren-sessions.example.md    # Template for persistent session continuity tracking
├── commands/                    # Direct fast-path commands (/build, /audit, /plan, /research, /voice)
│   ├── audit.md
│   ├── build.md
│   ├── plan.md
│   ├── research.md
│   └── voice.md
├── skills/                      # Progressive-disclosure SKILL.md bundles
│   ├── computer-use/SKILL.md    # Native Windows desktop control via zyren-ufo MCP
│   └── langgraph/SKILL.md       # Structured LangGraph workflows + live Docs/Reference MCP grounding
└── README.md                    # This deployment guide
```

---

## Deployment Options

### Option 1: Global Deployment (Available in All OpenCode Projects)
To make the Žyren collective, Computer Use, and LangGraph skills available across every project on your workstation:
1. Copy `opencode.example.jsonc` to your user configuration directory:
   - **Windows:** `%USERPROFILE%\.config\opencode\opencode.jsonc`
   - **Linux / macOS:** `~/.config/opencode/opencode.jsonc`
   - Replace `<PATH_TO_UFO>` in `mcp.servers["zyren-ufo"]` with your local UFO bridge directory if using Windows Computer Use.
2. Copy `AGENTS.md`, `commands/` (`/build`, `/audit`, `/plan`, `/research`, `/voice`), and `skills/` (`computer-use`, `langgraph`) into `~/.config/opencode/` (`%USERPROFILE%\.config\opencode\` on Windows).
3. Set your `NVIDIA_API_KEY` environment variable.

### Option 2: Project-Local Isolated Deployment
To isolate the collective strictly to a specific repository:
1. Create a `.opencode/` directory in your repository root.
2. Copy `opencode.example.jsonc` to `.opencode/opencode.jsonc`.
3. Copy `AGENTS.md` to `.opencode/AGENTS.md` (or your project root).
4. Copy `commands/` to `.opencode/commands/` and `skills/` to `.opencode/skills/`.
5. Copy `zyren-sessions.example.md` to your project root as `zyren-sessions.md`.

---

## Architectural Principles & Rules

1. **Surgical Isolation:** 
   The configuration defines `zyren-*` agent IDs and places surgical permission locks on the default `build` and `plan` agents (`deny: "zyren-*"`), while exposing global MCP servers (`zyren-ufo`, `langchain-docs`, `langchain-reference`) and skills cleanly across all 7 agents.
2. **Model Inheritance + Unified Multimodal Pairing:**
   - The coordinator (`zyren-dev-team`) defaults to `nvidia/stepfun-ai/step-5-preview`.
   - The three specialists (`zyren-research`, `zyren-planner`, `zyren-coder`) carry **no pinned model** and dynamically inherit whatever model you select in the session/app.
   - The critic (`zyren-critic`) is **hard-pinned** to `nvidia/nvidia/nemotron-3.5-super-vl-120b-a12b` for mandatory cross-model cognitive diversity.
   - Real-time desktop Voice + Vision control is paired through a singleton **`gemini-3.8-live`** bridge (`zyren-ufo` with `codemode: false` and headless `gemini-3.8-flash` fallback when Voice is off), giving every specialist direct desktop verification under a single FIFO mutex and emergency safety gate without dual-audio conflicts.
3. **Persistent Session Protocol (`zyren-sessions.md`):**
   One agent = one persistent session for the lifetime of the project. The coordinator reads the registry before every dispatch and passes the registered `sessionID` to preserve working context and eliminate orphaned sessions.
4. **Mandatory Deterministic Critic Gate:**
   `zyren-critic` verifies code via `exec` (plus optional GUI verification via `zyren-ufo`) only. Text-only approval is strictly rejected.

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

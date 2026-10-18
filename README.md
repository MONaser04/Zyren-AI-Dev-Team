# Zyren-AI-Dev-Team

**Autonomous Multi-Agent Software Engineering Collective powered by NVIDIA NeMo & Gemini Live (Generation 2)**

[![Project Status: Suspended / Archived](https://www.repostatus.org/badges/latest/suspended.svg)](https://www.repostatus.org/#suspended)
[![Superseded by ZyrenClaw](https://img.shields.io/badge/Superseded%20by-ZyrenClaw-blue.svg)](https://github.com/MONaser04/ZyrenClaw)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20Endpoints-76B900.svg)](https://www.nvidia.com/en-us/ai-data-science/products/nim/)
[![NeMo Guardrails](https://img.shields.io/badge/NeMo-Guardrails-green.svg)](https://github.com/NVIDIA/NeMo-Guardrails)
[![Gemini Live](https://img.shields.io/badge/Gemini-Live%20Multimodal%20API-4285F4.svg)](https://ai.google.dev/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checking: MyPy Strict](https://img.shields.io/badge/mypy-strict-brightgreen.svg)](https://mypy-lang.org/)

> [!IMPORTANT]
> **Project Status: Archived & Superseded by ŽyrenClaw (Generation 3)**
> Active development on this repository is paused and preserved in read-only archive mode. This codebase represents **Generation 2** of the Žyren architecture (the fully implemented Dual-Brain Voice/Reasoning Liaison Agent and 6-agent target blueprint). All active autonomous software development workflows have evolved into the lightweight, 5-agent vertical hub-and-spoke production architecture at [**MONaser04/ZyrenClaw**](https://github.com/MONaser04/ZyrenClaw).

---

## 1. Architectural Overview & Lineage

**`Zyren-AI-Dev-Team`** represents **Generation 2** of the **Žyren Autonomous Multi-Agent Architecture**. It was initiated as a strategic consolidation phase to evolve from the sprawling, 17-agent star topology of Generation 1 ([`Zyren-AI-Dev-Team-I`](https://github.com/MONaser04/Zyren-AI-Dev-Team-I)) into a focused, highly coordinated **6-agent software development collective**.

Built directly on top of the modular, domain-agnostic foundation chassis ([`Zyren-NeMo-Chassis`](https://github.com/MONaser04/Zyren-NeMo-Chassis)), this system combines high-throughput **NVIDIA NIM** cloud inference endpoints (`nvidia/nemotron-3-ultra-550b-a55b` and `nvidia/nemotron-3.5-lightning-30b-a3b`) with Google's **Gemini Live API** to deliver a production-grade conversational and multimodal software development environment.

```
       +-------------------------------------------------------------+
       |                   USER INTERFACE LAYER                      |
       |     Interactive Terminal CLI (Typer / Rich)  |  WebSockets  |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             LIAISON AGENT (DUAL-BRAIN ENGINE)               |
       |  +---------------------------+  +------------------------+  |
       |  |     VOICE / MM FACADE     |  |     REASONING CORE     |  |
       |  |  Gemini Live API (16kHz)  |  | Nemotron-3-Ultra 550B  |  |
       |  | 15-min Auto-Resumption    |  | Thought-Trace Parsing  |  |
       |  +-------------+-------------+  +------------+-----------+  |
       |                |                             |              |
       |                +--------------+--------------+              |
       |                               |                             |
       |                               v                             |
       |           STRICT CONSENSUS DISPATCH GATE (Deterministic)    |
       |              (Explicit Command OR Spec Consensus)           |
       +-------------------------------+-----------------------------+
                                       |
                   [Gated Escalation to Downstream Swarm]
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
+---------------+              +---------------+              +---------------+
|  RESEARCHER   |              |    PLANNER    |              |     CODER     |
|  (Deep-Dive)  |              | (Spec / Arch) |              | (Full-Stack)  |
+---------------+              +---------------+              +---------------+
        |                              |                              |
        +------------------------------+------------------------------+
                                       |
        +------------------------------+------------------------------+
        |                                                             |
        v                                                             v
+---------------+                                             +---------------+
|    UI / UX    |                                             |    CRITIC     |
| (Glassmorphic)|                                             | (Deterministic|
+---------------+                                             |  Verification)|
                                                              +---------------+
```

---

## 2. The 6-Agent Target Architecture

The Generation 2 roadmap was designed around **6 specialized, non-overlapping roles** to eliminate the coordinate thrashing and context degradation (>30%) experienced in earlier 17-agent models:

| Agent Role | Planned Scope & Architectural Responsibility | Implementation Status |
|---|---|---|
| **1. Liaison** | Multimodal user interface (Voice & Text), conversational intake, deep reasoning, sandboxed research tools, and strict consensus dispatch gating. | **Fully Implemented & Verified** (`src/agents/liaison/`) |
| **2. Researcher** | Multi-hop repository indexing, official documentation ingestion, API reference validation, and dependency graph analysis. | Blueprint Stage (Transferred to Gen 3) |
| **3. Planner** | PRD-to-architecture decomposition, contract schema formulation, and DAG task dependency generation. | Blueprint Stage (Transferred to Gen 3) |
| **4. Coder** | Full-stack implementation, algorithmic logic, module integration, and bug resolution. | Blueprint Stage (Transferred to Gen 3) |
| **5. UI / UX** | Visual hierarchy styling, CSS animations, responsive layouts, and modern glassmorphic interface engineering. | Blueprint Stage (Transferred to Gen 3) |
| **6. Critic** | Deterministic runtime verification, syntax compilation (`node --check`, AST linting), and headless playtest test execution. | Blueprint Stage (Transferred to Gen 3) |

---

## 3. Implementation Deep-Dive: The Liaison Agent

The centerpiece and fully realized component of this repository is the **Liaison Agent** (`src/agents/liaison/`), an advanced conversational orchestrator engineered with a **Dual-Brain Hybrid Topology**:

### 3.1 Dual-Brain Engine (Voice Facade + Reasoning Core)

1. **Multimodal Voice Facade (`src/agents/liaison/voice/facade.py`):**
   - Connects to Google's **Gemini Live API** via bidirectional WebSockets (`gemini-3.1-flash-live-preview`).
   - Streams real-time audio at 16kHz PCM input and 24kHz PCM output.
   - Supports 1 FPS video frame ingestion for visual debugging and screen inspection.
   - Governed by an explicit finite-state lifecycle controller (`controls.py`) supporting `IDLE`, `CONNECTING`, `ACTIVE`, `MUTED`, `CAMERA_OFF`, `SCREEN_OFF`, `RECONNECTING`, and `CLOSING` states.

2. **15-Minute Session Auto-Resumption (`src/agents/liaison/session.py`):**
   - The Gemini Live WebSocket enforces a hard 15-minute session cutoff.
   - `SessionResumptionManager` tracks all conversation turns (`ConversationTurn`) within a bounded sliding window, serializing state to `.liaison_session` and `EventStore`.
   - Automatically reconnects at the 14-minute threshold (`resumption_trigger_seconds: 840`), seamlessly transferring active context, tool call history, and system instructions without user disruption.

3. **Deep Reasoning Core (`src/agents/liaison/reasoning/core.py`):**
   - Powered by **NVIDIA Nemotron-3-Ultra** (`nvidia/nemotron-3-ultra-550b-a55b`) through the decoupled `SwitchyardRouter`.
   - Operates at low temperature (`0.3`) for deterministic architectural deliberation.
   - Built-in multi-pattern regex extraction isolates internal reasoning traces (`<thought>`, `<thinking>`, `<|thinking|>`, `【Thinking】`) from clean final operator responses.

### 3.2 The Strict Consensus Dispatch Gate (`src/agents/liaison/dispatch_gate.py`)

A fundamental flaw of earlier agent architectures was premature delegation—agents dispatched half-baked tasks to code-generation pipelines before human requirements were fully validated.

The **Liaison Agent** introduces the **`PlannerDispatchGate`**, which strictly blocks downstream escalation until one of two deterministic criteria is met:

1. **Explicit Operator Command:**
   - Matches regex patterns such as `\bsend\s+to\s+(planner|system|company)\b` or `\bdispatch\s+to\s+planner\b`.
2. **Mutual Specification Consensus:**
   - Multi-turn conversation state tracker verifies that all requirement dimensions are satisfied, and confirms consensus indicators (`"spec complete"`, `"agreed"`, `"finalized"`).
3. **Voice Delegation Isolation:**
   - Spoken commands such as `"send to liaison"` or `"ask liaison"` delegate internally to the **Reasoning Core**, ensuring voice chatter never inadvertently triggers high-cost multi-agent downstream runs.

### 3.3 Sandboxed Read-Only Research Tools (`src/agents/liaison/tools/`)

To prevent unauthorized project mutations while retaining deep fact-checking power, the Liaison Agent is intentionally granted **read-only access**:

* **`web_search`:** Multi-hop live technical search with recency filters and domain whitelisting.
* **`read_files`:** Line-range project inspection, directory tree walk, and syntax analysis.
* **`execute_commands`:** Sandboxed terminal inspection (`git status`, `git diff`, grep, process inspection) executed with strict 30-second timeouts, 10MB buffer limits, and zero shell write access.

### 3.4 Rich Interactive CLI (`src/agents/liaison/cli.py`)

An enterprise terminal application built with **Typer** and **Rich**:
* Interactive prompt loop with live thinking boxes (revealing Nemotron-3-Ultra chain-of-thought).
* In-line voice session control via `/voice start`, `/voice mute`, `/voice camera`, and `/voice stop`.

---

## 4. Underlying Chassis Foundation (`Zyren-NeMo-Chassis`)

This repository inherits the complete infrastructure runtime provided by the chassis layer:

* **Switchyard Router (`src/routing/router.py` & `config/models.yaml`):** Dynamic task routing across NIM models with token-bucket and strict rate limiters (`nvidia/nemotron-3-ultra-550b-a55b` for complex reasoning, `nvidia/nemotron-3.5-lightning-30b-a3b` for fast execution).
* **Event-Sourced State (`src/state/`):** SQLite WAL event store recording every message, node metric, tool execution, and session transition.
* **Vector Memory Substrate (`src/vectorstore/`):** Embedded FAISS index for local semantic document lookup.
* **Deterministic Sandbox (`src/sandbox/runner.py`):** Subprocess management with process groups and automated `SIGKILL` reaping.
* **NeMo Guardrails & Observability (`src/governance/` & `src/observability/`):** Colang safety policies, Nemotron guardrails, and ATOF/ATIF/OTel tracing exporters.

---

## 5. Repository File Tree

```
Zyren-AI-Dev-Team/
├── .env.example                  # Environment configuration template (API keys)
├── .gitignore                    # Git tracking rules
├── .liaison_session              # Persisted session ID for auto-resumption
├── .project/                     # NVIDIA AI Workbench container specification
│   └── spec.yaml
├── config/
│   ├── models.yaml               # NIM model registry (Nemotron-3-Ultra / 3.5-Lightning)
│   ├── nims.deprecated.yaml      # Model deprecation tracking
│   ├── observability.toml        # OTel and trajectory exporter configuration
│   ├── policies/                 # NeMo Guardrails taxonomy & archetype rules
│   ├── rails/                    # Colang flow definitions
│   └── repos.yaml                # Blueprint registry
├── src/
│   ├── agents/                   # Multi-agent roster
│   │   └── liaison/              # [IMPLEMENTED] The Liaison Dual-Brain Agent
│   │       ├── base.py           # Abstract agent contracts
│   │       ├── cli.py            # Typer & Rich interactive terminal
│   │       ├── config.py         # Pydantic v2 configuration models
│   │       ├── controls.py       # Voice session lifecycle state machine
│   │       ├── dispatch_gate.py  # Strict consensus dispatch gatekeeper
│   │       ├── exceptions.py     # Typed domain errors
│   │       ├── factory.py        # Dependency injection agent factory
│   │       ├── liaison.py        # Main LiaisonAgent orchestrator class
│   │       ├── session.py        # 15-minute sliding-window session manager
│   │       ├── reasoning/
│   │       │   └── core.py       # Nemotron-3-Ultra thinking & reasoning engine
│   │       ├── tests/            # Test suite for Liaison components
│   │       ├── tools/
│   │       │   ├── definitions.py# Function declarations (web_search, read_files, exec)
│   │       │   └── handlers.py   # Tool invocation routing & sandbox dispatch
│   │       └── voice/
│   │           ├── audio_pipeline.py  # 16kHz/24kHz PCM audio processing
│   │           ├── facade.py          # Gemini Live WebSocket wrapper
│   │           ├── transcription.py   # Live speech-to-text integration
│   │           └── video_pipeline.py  # 1 FPS JPEG frame pipeline
│   ├── config/                   # Global configuration loaders
│   ├── contracts/                # Pydantic data schemas and polymorphic types
│   ├── governance/               # Guardrails engine and Nemotron prompts
│   ├── infrastructure/           # NIMClient, rate limiters, token buckets
│   ├── observability/            # ATOF/ATIF trajectory and metric exporters
│   ├── routing/                  # SwitchyardRouter implementation
│   ├── runtime/                  # LangGraph execution engine & TTC executor
│   ├── sandbox/                  # Subprocess execution runner with SIGKILL reaping
│   ├── state/                    # SQLite WAL event store and state schema
│   └── vectorstore/              # FAISS vector store integration
├── tests/                        # Comprehensive unit and integration test suites
│   ├── conftest.py
│   ├── test_base_contracts.py
│   ├── test_nim_client.py
│   ├── test_observability.py
│   ├── test_router.py
│   ├── test_state_schema.py
│   └── test_stress_concurrency.py
├── pyproject.toml                # Build configuration and linting rules
└── requirements.txt              # Pinned Python dependencies
```

---

## 6. Testing & Quality Assurance

The Liaison Agent and underlying chassis include exhaustive automated test suites:

```bash
# Run the complete Liaison Agent test suite
python -m pytest src/agents/liaison/tests/ -v

# Run the chassis infrastructure tests
python -m pytest tests/ -v
```

### Liaison Verification Matrix:
* **`test_voice_lifecycle.py`:** Validates state machine transitions across active, muted, and disconnect lifecycles.
* **`test_thinking_extraction.py`:** Validates regex parsing of `<thought>`, `<thinking>`, and multi-line markdown thinking blocks.
* **`test_dispatch_gate.py`:** Confirms the gatekeeper strictly blocks unauthorized dispatch and correctly triggers on explicit consensus.
* **`test_session_resumption.py`:** Tests 15-minute auto-reconnect context preservation and sliding-window rollover.
* **`test_tool_handlers.py`:** Verifies read-only sandboxed command execution and parameter sanitation.
* **`test_cli_thinking_render.py`:** Validates Rich terminal UI rendering and collapsible panel logic.

---

## 7. Project Evolution & The Pivot to ŽyrenClaw (Gen 3)

Development on **`Zyren-AI-Dev-Team`** was intentionally paused after the successful completion of the **Liaison Agent**. 

### The Strategic Rationale:
1. **Hardware Envelope Reality:** Evaluating containerized micro-VM stacks (such as NemoClaw and multi-container Docker environments) revealed significant memory and compute overhead on local 16GB RAM workstations.
2. **From Horizontal Layers to Vertical Slicing:** The planned downstream team (Researcher → Planner → Coder → UI → Critic) still relied on sequential horizontal handoffs. Empirical systems research in late 2026 demonstrated that horizontal layer splitting compounds context drift and interface desynchronization.
3. **The Pivot to ŽyrenClaw:** Rather than continuing down the path of an overweight multi-container stack, the core lessons learned from this repository—specifically the **strict dispatch gatekeeper, deterministic runtime verification, and single-pass feature cohesion**—were synthesized into **ŽyrenClaw (Generation 3)**:
   - Slashed the team to 5 elite agents in a strict Hub-and-Spoke topology under OpenClaw and the custom **LangClaw** sidecar engine.
   - Fully documented in the published engineering case study: [**MONaser04/ZyrenClaw**](https://github.com/MONaser04/ZyrenClaw).

---

## 8. License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

*Verified against live repository code and test fixtures · Generation 2 of the Žyren Architecture.*

---
name: LangGraph
description: Design, build, debug, and deploy stateful AI agent workflows with LangGraph (StateGraph, reducers, Command, Send, human-in-the-loop interrupt, checkpointers, Store memory, streaming, and langgraph.json). Use whenever building or refactoring LangGraph / LangChain agent graphs or multi-agent pipelines (لانجراف / LangGraph).
---

# Structured LangGraph Engineering Workflow

Follow this organized workflow whenever designing, implementing, debugging, or deploying **LangGraph** / **LangChain** stateful agent systems in Python or TypeScript.

## 1. Live Documentation & API Grounding First
- Always query the official **`langchain-docs`** (`https://docs.langchain.com/mcp`) and **`langchain-reference`** (`https://reference.langchain.com/mcp`) MCP servers before writing non-trivial graph code, so every import, parameter, and version behavior matches current LangGraph v1.x/2026 APIs rather than outdated pre-v1 patterns.

## 2. Explicit State & Reducers
- Define explicit `TypedDict` (preferred for fast structured state) or Pydantic `BaseModel` schemas.
- Attach reducers via `Annotated[..., reducer]` ONLY for append/merge fields (e.g., `messages: Annotated[list[AnyMessage], add_messages]` or `logs: Annotated[list[str], operator.add]`), keeping overwrite fields plain.
- Keep node inputs/outputs small, serializable (JSON/msgpack compatible for checkpointers), and return only partial dict diffs (`{"field": new_value}`) from nodes.

## 3. Graph Topology & Dynamic Routing
- Build graphs explicitly with `StateGraph(State)` -> `add_node(...)` -> `add_edge(START, ...)` / `add_conditional_edges(...)` -> `.compile(checkpointer=..., store=...)`.
- Use **`Command(goto=..., update=...)`** inside nodes when a single step must both update state and dynamically choose the next node(s) or return to a parent graph (`Command.PARENT`).
- Use **`Send("worker_node", payload)`** for dynamic fan-out / map-reduce parallelism over runtime-sized lists.
- Structure multi-agent coordination cleanly (Supervisor / Hub-and-Spoke or Subgraphs with clear state boundaries).

## 4. Persistence, Checkpointers & Human-in-the-Loop (HITL)
- Use checkpointers (`InMemorySaver` for local dev/tests; `SqliteSaver` / `AsyncSqliteSaver` or `PostgresSaver` / `AsyncPostgresSaver` for production) and always supply `config={"configurable": {"thread_id": ...}}` when durable threads or HITL are needed.
- Implement human approvals / interactive pauses using **`interrupt(payload)`** inside nodes and resume cleanly via **`Command(resume=user_decision)`** (never spin polling loops inside a node).
- Use a **`BaseStore`** (`InMemoryStore` / `PostgresStore`) for cross-thread long-term memory separate from per-thread checkpointer state.

## 5. Streaming, MCP Integration & Agent Server Deployment
- Choose the appropriate `stream_mode`: `"updates"` (node diffs), `"messages"` (token-by-token LLM chunks + metadata), `"custom"` (arbitrary `get_stream_writer()` progress events), or a list like `["updates", "custom"]`.
- When bridging external MCP servers into a LangGraph agent, use **`langchain-mcp-adapters`** (`MultiServerMCPClient`).
- For production deployment with **LangGraph Agent Server / CLI**, organize project dependencies and graph entrypoints (`"graphs": {"agent": "./src/agent.py:graph"}`) cleanly in `langgraph.json` alongside a `.env.example` (never hardcoding API keys).

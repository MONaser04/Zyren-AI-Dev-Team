# Žyren Code Intelligence Engine (`scaffolds/tools/`)

Runtime-agnostic Python CLI utilities designed to prevent context window bloat and catch cross-file breaking regressions before deterministic execution gates.

---

## Tooling Suite

| Tool | Role | Dependencies | Execution Mode |
|---|---|---|---|
| [`code_outline.py`](./code_outline.py) | Extracts classes, methods, signatures, docstrings, and line ranges without loading full function bodies | Python 3.11+ stdlib only | Local / Offline |
| [`code_graph.py`](./code_graph.py) | Bi-directional cross-file symbol graph and `--impact` blast-radius analysis | Python 3.11+ stdlib only | Local / Offline |
| [`code_search.py`](./code_search.py) | Two-stage semantic retrieval (`nvidia/nemotron-3.5-embed-8b` + `nvidia/nemotron-3.5-rerank-8b`) with local SHA-256 SQLite cache | Python 3.11+ stdlib + `NVIDIA_API_KEY` | NVIDIA NIM API + Local SQLite Cache |

---

## Configuration & Caching

- **Cache Directory:** `code_search.py` stores its incremental SHA-256 SQLite vector cache in `ZYREN_CACHE_DIR` if set, or defaults cross-platform to `~/.cache/zyren`.
- **API Credentials:** `code_outline.py` and `code_graph.py` run fully offline. `code_search.py` requires `NVIDIA_API_KEY` for NVIDIA NIM embeddings and reranking.

---

## Usage Examples

```powershell
# 1. Inspect structural outline of a file or directory without ingesting full bodies
python scaffolds/tools/code_outline.py path/to/file.py

# 2. Compute cross-file blast radius before accepting a refactor
python scaffolds/tools/code_graph.py path/to/repo --impact path/to/modified_file.py

# 3. Natural-language semantic code search (English or Arabic)
python scaffolds/tools/code_search.py path/to/repo "session persistence and retry circuit breaker"
```

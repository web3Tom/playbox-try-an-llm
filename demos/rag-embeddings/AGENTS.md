<!-- FOR AI AGENTS. Scoped to demos/rag-embeddings/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — rag-embeddings demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
Retrieval-Augmented Generation against an **in-memory** ChromaDB collection. Sample policy
documents are embedded with `text-embedding-3-large`, a query is embedded and matched (top-1
cosine), and `gpt-5-mini` answers using *only* the retrieved context. Shows two distinct model
routes — embeddings vs. generation — in one pipeline.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `rag_query.py` | Entry point. `setup_collection` (embed + ingest) → `query_and_answer` (retrieve + `gpt-5-mini`) |
| `data/` | Drop real documents here; update `setup_collection` to ingest them (sample docs are hard-coded) |
| `README.md` | Human-facing walkthrough |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command | Env vars |
|------|---------|----------|
| Run RAG query | `uv run python demos/rag-embeddings/rag_query.py` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` |

Requires `chromadb` (`uv add chromadb` if the import fails).
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Job | Role / model | Why |
|-----|--------------|-----|
| Embed docs + query | `text-embedding-3-large` | A specialized *embeddings* route — not a chat model |
| Retrieve (cosine top-1) | *no model* — ChromaDB | Vector math is deterministic; never ask an LLM to "rank" |
| Answer from context | `everyday-dev` → `gpt-5-mini` | Grounded generation is the judgment call |

The lesson: a RAG pipeline mixes **three** routes. Don't collapse them onto one expensive model.

## Boundaries (delta from root)
- **Never** persist or transmit vectors/embeddings outside the sandbox — the store is in-memory by
  design and data is lost on exit; keep it that way (no external DB, per root Boundaries).
- **Always** constrain the answer to retrieved context (the system prompt already enforces this).
- **Ask first** before swapping ChromaDB for a persistent/remote vector store.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.10+, PEP 8, type hints (`-> list[float]`, `-> chromadb.Collection`).
- Guard the optional `chromadb` import with a clear install hint (see top of file).
- Log each ingest + the retrieved context for traceability.
<!-- AGENTS-GENERATED:END code-style -->

## When stuck
- Irrelevant answers → embedding model mismatch or too few `n_results`. Empty retrieval is handled and logged.
- Root conventions: repo-root `AGENTS.md`. Role + limits: `.kilo/agents/everyday-dev.md`, `.kilo/kilo.jsonc`.

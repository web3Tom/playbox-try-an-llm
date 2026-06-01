<!-- FOR AI AGENTS. Scoped to demos/codebase-analyzer/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — codebase-analyzer demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
The flagship demo: a multi-stage Python pipeline that analyzes a repository into a
knowledge graph, plus a Vite + React graph dashboard that renders it. It is the
template's strongest model-routing showcase — one run uses **four different
routes** (nano, mini, gpt-5.4, and pure code). The pipeline is a standalone
Python script (not a Kilo skill); Kilo is the assistant you use to extend it.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `analyze.py` | Interactive entrypoint: pick target → run stages → write `knowledge-graph.json` |
| `pipeline/clone.py` | Resolve target (GitLab clone / local / sample) — handles `GITLAB_PAT` |
| `pipeline/files.py` | Deterministic file enumeration, ignore rules, file cap |
| `pipeline/scan.py` | Stage: project description from README/manifests |
| `pipeline/analyze_files.py` | Stage: per-file summary, tags, import edges |
| `pipeline/merge.py` | Deterministic graph assembly (dedup, prune dangling edges) |
| `pipeline/architecture.py` | Stage: classify files into layers |
| `pipeline/schema.py` | KnowledgeGraph data contract + `validate()` |
| `pipeline/llm.py` | Azure client + the stage→model routing table |
| `prompts/*.md` | The three stage system prompts (edit these to tune behavior) |
| `sample-repo/` | Tiny bundled target so the demo runs with zero credentials |
| `dashboard/` | Vite + React 18 (plain JS) + cytoscape; reads `public/knowledge-graph.json` |
| `tests/` | Pytest for the deterministic core (files, merge, schema, clone) |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command | Env vars |
|------|---------|----------|
| Analyze a repo | `uv run python demos/codebase-analyzer/analyze.py` | `AZURE_OPENAI_*` (+ `GITLAB_PAT` for option 1) |
| View the graph | `cd dashboard && npm install && npm run dev` → http://localhost:5174 | — |
| Run the tests | `uv run --with pytest python -m pytest demos/codebase-analyzer/tests -q` | — |

The dashboard port (5174) is pre-forwarded in `devfile.yaml`.
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Stage | Role / model | Why |
|-------|--------------|-----|
| Enumerate files, merge graph | *no model* — Python | Deterministic transforms stay in code |
| Scan (project description) | `summarizer` → `gpt-5.4-nano` | Cheap, classification-grade summarization |
| Analyze each file (the bulk) | `everyday-dev` → `gpt-5.4-mini` | High-volume workhorse — runs once per file, never the orchestrator |
| Classify architecture | `orchestrator` → `gpt-5.4` | The one step needing whole-project reasoning earns the expensive model |

The lesson in one line: **the expensive model runs once; the cheap model runs
often; the deterministic work runs for free.** Keep `pipeline/llm.py`'s
`ROLE_MODELS` in lockstep with `.kilo/kilo.jsonc`.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.11+, PEP 8, type hints on signatures. Small, focused modules (one stage per file).
- Stage prompts live in `prompts/*.md`, not inline — edit prompts there.
- LLM output is untrusted input: parse defensively and `validate()` the final graph.
- Dashboard is **plain JavaScript + JSX (no TypeScript)**, mirroring the `react-ui` demo; theme via CSS variables; one component per file.
<!-- AGENTS-GENERATED:END code-style -->

## Boundaries (delta from root)
- **Never** log or print `GITLAB_PAT`; it is injected into the clone URL only and scrubbed from errors (`clone.py`). Keep it that way.
- **Never** clone or reach a GitLab host outside the Playbox-approved internal instance.
- **Always** report truncation when the file cap is hit — never silently analyze a subset.
- **Ask first** before adding a dependency: keep Python to `openai`/`python-dotenv`, and the dashboard to React + Vite + cytoscape.
- **Never** add tree-sitter or native parsers — extraction is deliberately pure-LLM and language-agnostic.

## When stuck
- Empty dashboard → run `analyze.py` first, or check `dashboard/public/knowledge-graph.json` exists and is valid.
- Disconnected nodes → the file-analyzer guessed import paths that didn't resolve; `merge.py` prunes them by design (see its tests).
- Credentials missing → `analyze.py` fails loud; set `AZURE_OPENAI_ENDPOINT`/`AZURE_OPENAI_API_KEY` (see `.env.example`).
- Root conventions: repo-root `AGENTS.md`. Roles + limits: `.kilo/agents/`, `.kilo/kilo.jsonc`.

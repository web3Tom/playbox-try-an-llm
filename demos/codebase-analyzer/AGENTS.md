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

The per-file analyze stage also extracts each file's top-level **functions and
classes**, emitted as `function`/`class` nodes sharing the file's path; the
dashboard nests them inside their file as compound "boxes". The same per-file
response carries each member's `calls`/`extends` names, which a deterministic
post-pass resolves into `calls`/`inherits` edges — a real call map at **no extra
API cost**. A final **`tour` stage** (gpt-5.4) emits an ordered reading path
through the files. Per-file analysis runs **concurrently** under a bounded
thread pool. Before any of that, enumeration drops generated/boilerplate files
and caps per-directory counts, and a cheap **`select`** stage (nano) picks the
most architecturally significant files when a repo exceeds the budget — so the
budget isn't wasted on migrations or generated clients. When a repo's README is a
generic template (no real purpose/stack), a `describe` stage infers the project
description from the analyzed file summaries instead of giving up.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `analyze.py` | Interactive entrypoint: pick target → run stages → write `knowledge-graph.json` |
| `pipeline/clone.py` | Resolve target (GitLab clone / local / sample) — handles `GITLAB_PAT` |
| `pipeline/files.py` | Deterministic enumeration: ignore rules, boilerplate/**generated-file** skip, **per-directory cap**, candidate pool for `select` |
| `pipeline/scan.py` | Stage: project description from README/manifests (+ an `informative` flag) |
| `pipeline/select.py` | Stage: triage which candidate files are worth analyzing (with a deterministic fallback) |
| `pipeline/analyze_files.py` | Stage: per-file summary, tags, import edges, member (function/class) nodes, **and `calls`/`inherits` member edges**; runs files concurrently (bounded pool) |
| `pipeline/merge.py` | Deterministic graph assembly (dedup, prune dangling edges) |
| `pipeline/architecture.py` | Stage: classify files into layers |
| `pipeline/describe.py` | Stage: infer the project description from code when the README is uninformative |
| `pipeline/tour.py` | Stage: ordered, file-anchored guided reading path |
| `pipeline/schema.py` | KnowledgeGraph data contract (nodes, edges, layers, `tour`) + `validate()` |
| `pipeline/llm.py` | Azure client + the stage→model routing table |
| `prompts/*.md` | The six stage system prompts (scan, select, file-analyzer, architecture, describe, tour) — edit these to tune behavior |
| `sample-repo/` | Tiny bundled target so the demo runs with zero credentials |
| `dashboard/` | Vite + React 18 (plain JS) + cytoscape; **compound nodes** (files contain their functions/classes), colour-coded edges (imports/calls/inherits), search, module toggle, layer filter, guided-tour card, PNG/JSON export; reads `public/knowledge-graph.json` |
| `tests/` | Pytest for the deterministic core (files, merge, schema, clone, member-edge resolution, tour) |
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
| Scan (project description) | `summarizer` → `gpt-5-nano` | Cheap, classification-grade summarization |
| Select files to analyze | `summarizer` → `gpt-5-nano` | When candidates exceed the budget, "which files matter" is a judgment call — cheap triage over paths only, with a deterministic fallback if it errors. Deterministic guards (generated-file skip, per-dir cap) do the rote filtering first |
| Analyze each file (the bulk) | `code` → `gpt-5-mini` | High-volume workhorse — runs once per file (concurrently), never the Plan agent. The same call also returns the file's functions/classes **and their call/inheritance names**, so members and member edges cost no extra request |
| Classify architecture | `plan` → `gpt-5.4` | Whole-project reasoning earns the expensive model |
| Describe from code (deterministic fallback) | `summarizer` → `gpt-5-nano` | Only runs when the README was uninformative — infers the project description from the analyzed file summaries (summarizing summaries is classification-grade) |
| Build guided tour | `plan` → `gpt-5.4` | Designing a reading order is the same whole-project judgment, so it shares the Plan agent route |

The lesson in one line: **the expensive model runs only for whole-project
reasoning (architecture + tour); the cheap model runs often; the deterministic
work — including the member call graph — runs for free.** Keep `pipeline/llm.py`'s
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
- **Ask first** before adding a dependency: keep Python to `openai`/`python-dotenv`, and the dashboard to React + Vite + cytoscape (+ `cytoscape-fcose` for the compound-aware layout).
- **Never** add tree-sitter or native parsers — extraction is deliberately pure-LLM and language-agnostic.
- Member (function/class) nodes **and** their `calls`/`inherits` edges reuse types `schema.py` already defines and come from the existing per-file `analyze` call — **don't add a separate extraction pass or per-member API calls.** Edge targets are resolved deterministically (same-file first, then unambiguous global match) in `analyze_files._member_edges`; ambiguous names are dropped, never guessed.
- The per-file pool is **bounded on purpose** (`DEFAULT_MAX_WORKERS`) to respect the APIM rate limit — don't unbound it.
- The `tour` stage must only reference real file paths; `build_tour` drops unknown ones and `validate()` flags them — keep both guards.
- File **selection is layered**: deterministic guards in `files.py` (generated-file skip via name + content sniff, per-directory cap) do the rote filtering; the `select` stage (nano) only makes the final judgment call when candidates exceed the budget, and **must keep its deterministic fallback** — it discards hallucinated paths and never aborts the run. Don't push the rote filtering into the model (Rule 5), and don't let `select` become load-bearing without the fallback.

## When stuck
- Empty dashboard → run `analyze.py` first, or check `dashboard/public/knowledge-graph.json` exists and is valid.
- Disconnected nodes → the file-analyzer guessed import paths that didn't resolve; `merge.py` prunes them by design (see its tests).
- Credentials missing → `analyze.py` fails loud; set `AZURE_OPENAI_ENDPOINT`/`AZURE_OPENAI_API_KEY` (see `.env.example`).
- Root conventions: repo-root `AGENTS.md`. Roles + limits: `.kilo/agents/`, `.kilo/kilo.jsonc`.

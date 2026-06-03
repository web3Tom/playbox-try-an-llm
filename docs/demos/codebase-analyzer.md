# Demo: Codebase Analyzer

The flagship demo. Point it at a repository and it runs a small **multi-stage LLM pipeline** to build a knowledge graph of the codebase, then serves an interactive graph dashboard. It is the clearest illustration of the template's core lesson — **route each task to the cheapest model that can do it**.

## What It Does

A standalone Python script (not a Kilo skill) runs the pipeline below, each stage on a deliberately chosen model:

| Stage | Work | Routes to |
|-------|------|-----------|
| Enumerate / resolve target | clone or resolve; drop noise + generated files; cap per directory | *no model* |
| Scan | one-paragraph project description from the README/manifests | `gpt-5-nano` |
| Select | rank candidate files by significance, keep the most important (deterministic fallback) | `gpt-5-nano` |
| Analyze each file | per-file summary, tags, import edges, top-level functions/classes, and the `calls`/`inherits` between them | `gpt-5-mini` |
| Merge graph | deduplicate nodes, prune dangling edges | *no model* |
| Classify architecture | group files into layers | `gpt-5.4` (Plan agent) |
| Describe from code | *(only if the README was uninformative)* infer the description from file summaries | `gpt-5-nano` |
| Build guided tour | ordered, file-anchored reading path | `gpt-5.4` (Plan agent) |

One run exercises **nano → mini → gpt-5.4 → pure code**. The expensive model runs only for the two steps that need whole-project reasoning (layer classification and the guided tour); everything else routes cheaper or to plain code. The per-file analyze stage runs **concurrently** (a small, bounded pool — capped to respect the APIM rate limit), and the function/class **call graph is derived from the same per-file response**, so it adds no API requests.

## How to Run

**1. Run the analyzer** (interactive — it asks what to analyze):

```bash
uv run python demos/codebase-analyzer/analyze.py
```

Choose a target:

| # | Target | Needs |
|---|--------|-------|
| 1 | Internal GitLab repo (shallow-cloned to `/tmp`) | `GITLAB_PAT` + Azure creds |
| 2 | A local directory path | Azure creds |
| 3 | Bundled sample repo *(default)* | Azure creds only |

It writes `dashboard/public/knowledge-graph.json`.

**2. View the graph:**

```bash
cd demos/codebase-analyzer/dashboard
npm install
npm run dev      # http://localhost:5174 (pre-forwarded in devfile.yaml)
```

The dashboard ships with a committed sample graph, so `npm run dev` renders something immediately even before you run the analyzer.

Each file is rendered as a **box containing its top-level functions (circles) and classes (hexagons)**. Edges are colour-coded — grey **imports** between files, blue **calls** and dashed-purple **inherits** between members. Search to highlight nodes, use the **Show modules** toggle to collapse to file level, click a **layer** in the legend to hide/show it, follow the **Guided Tour** card to walk the codebase in reading order, and use **Export PNG/JSON** to save the graph. Click any file or module for details.

## The Routing Lesson

This demo is the template's thesis in one pipeline:

- **Enumerating files and merging the graph are deterministic** — they run in plain Python, no model. A file walk, a generated-file filter, a per-directory cap, or a dedup is not a judgment call.
- **Choosing *which* files to read, when there are too many, IS a judgment call** — so the `select` stage spends a cheap `gpt-5-nano` call on it (with a deterministic fallback), rather than letting a flood of migrations crowd out the real code.
- **The per-file analysis is high-volume**, so it runs on the `gpt-5-mini` workhorse — never the Plan agent, even though it executes once per file.
- **Classifying architecture and designing the guided tour need to see the whole project at once** — genuine multi-file reasoning — so those two stages use the Plan agent (`gpt-5.4`).
- **The member call graph is free**: the analyze call already returns each member's call/inheritance names, so a deterministic post-pass turns them into edges with no extra requests.

The expensive model runs only for whole-project reasoning; the cheap model runs often; the deterministic work runs for free.

## Notes

- Structure extraction is **pure-LLM** (works on any language) — there is no tree-sitter or language-specific parser to install.
- **File selection is layered.** Deterministic guards in `pipeline/files.py` skip boilerplate/config (`__init__.py`, `*.config.js`, …) and machine-generated files (DB migrations, `*_pb2.py`, `*.generated.*`, `@generated` content), and cap how many files come from any one directory so a folder like `alembic/versions/` can't eat the whole budget. When candidates still exceed the cap, the `select` stage (`gpt-5-nano`) ranks them by architectural significance — with a deterministic fallback so it can never break the run.
- The description comes from the README/manifests, but when those are a generic template the `describe` stage (`gpt-5-nano`) infers it from the analyzed file summaries instead — an undocumented repo still gets a useful summary rather than "cannot be determined."
- Analysis is **capped at 30 files** by default (prompted at runtime). When a repo is larger, the cap is reported, never silently applied.
- The temporary clone is removed automatically when the run finishes.
- The `GITLAB_PAT` is injected into the clone URL only and is never logged.

## Extending It

The dashboard is a Vite + React 18 (plain JS) app — the same stack as the React UI demo — so extending it is a natural `react-frontend` role task:

```
@react-frontend In demos/codebase-analyzer/dashboard, add a filter that hides
nodes below a chosen complexity. Keep it consistent with the existing theme.
```

---

Next: [Orchestrator Demo](orchestrator.md) to see agents planning and delegating.

# Demo: Codebase Analyzer

The flagship demo. Point it at a repository and it runs a small **multi-stage LLM pipeline** to build a knowledge graph of the codebase, then serves an interactive graph dashboard. It is the clearest illustration of the template's core lesson — **route each task to the cheapest model that can do it**.

## What It Does

A standalone Python script (not a Kilo skill) runs the pipeline below, each stage on a deliberately chosen model:

| Stage | Work | Routes to |
|-------|------|-----------|
| Clone / resolve target | GitLab repo, local path, or bundled sample | *no model* |
| Scan | one-paragraph project description from the README/manifests | `gpt-5.4-nano` |
| Analyze each file | per-file summary, tags, and import edges | `gpt-5.4-mini` |
| Merge graph | deduplicate nodes, prune dangling edges | *no model* |
| Classify architecture | group files into layers | `gpt-5.4` |

One run exercises **nano → mini → gpt-5.4 → pure code**. The expensive model runs exactly once, for the single step (layer classification) that needs whole-project reasoning.

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

## The Routing Lesson

This demo is the template's thesis in one pipeline:

- **Enumerating files and merging the graph are deterministic** — they run in plain Python, no model. A file walk or a dedup is not a judgment call.
- **The per-file analysis is high-volume**, so it runs on the `gpt-5.4-mini` workhorse — never the orchestrator, even though it executes once per file.
- **Classifying architecture needs to see the whole project at once** — genuine multi-file reasoning — so it, and only it, earns `gpt-5.4`.

The expensive model runs once; the cheap model runs often; the deterministic work runs for free.

## Notes

- Structure extraction is **pure-LLM** (works on any language) — there is no tree-sitter or language-specific parser to install.
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

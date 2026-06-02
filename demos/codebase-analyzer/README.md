# Codebase Analyzer

The flagship demo: point it at a repository and it runs a small **multi-stage
LLM pipeline** to build a knowledge graph of the codebase, then serves an
interactive graph dashboard. It is the clearest illustration of the template's
core idea — **route each task to the cheapest model that can do it**.

## What it does

```
clone / resolve target        [no model]   GitLab repo, local path, or bundled sample
  └─ scan                      gpt-5-nano  one-paragraph project description
  └─ analyze each file         gpt-5-mini  summary, tags, imports + functions/classes and their calls/inheritance
  └─ merge graph               [no model]    dedup nodes, prune dangling edges
  └─ classify architecture     gpt-5.4       group files into layers
  └─ build guided tour         gpt-5.4       ordered reading path through the files
  └─ write knowledge-graph.json -> dashboard renders it
```

One run exercises **nano → mini → gpt-5.4 → pure code**. The expensive model is
reserved for the two steps that genuinely need whole-project reasoning
(architecture + tour); everything else routes to a cheaper one. The per-file
analyze stage runs **concurrently** (a small, bounded thread pool — deliberately
capped so the demo stays under the APIM rate limit), and the function/class call
graph is derived from data the same per-file call already returned, so it costs
**no extra API requests**.

## How to run

**1. Run the analyzer** (interactive — it asks what to analyze):

```bash
uv run python demos/codebase-analyzer/analyze.py
```

You'll be asked to choose a target:

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

The dashboard ships with a committed sample graph, so `npm run dev` shows
something immediately even before you run the analyzer.

In the graph, each file is a **box containing its top-level functions (circles)
and classes (hexagons)**. Edges are colour-coded by kind: grey **imports**
between file boxes, blue **calls** and dashed-purple **inherits** between
members. The sidebar adds:

- **Search** to highlight nodes and the **Show modules** toggle to collapse to file level.
- A clickable **Layers** legend — click a layer to hide/show it in the graph.
- A **Guided Tour** card (the `tour` stage's output): an ordered walkthrough where
  each step jumps the inspector to its file.
- **Export PNG / Export JSON** buttons to save the current graph.

Click any file or module to inspect it in the sidebar.

## Environment variables

- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` — required for the LLM stages
- `GITLAB_PAT` — only for target option 1 (cloning a private GitLab repo)

## Notes

- Boilerplate and tooling-config files (`__init__.py`, `setup.py`, `conftest.py`,
  `*.config.js`, `.eslintrc.*`, …) are **skipped before any LLM call** — they
  carry little logic and would just burn tokens. Edit `IGNORE_FILES` /
  `_is_insignificant` in `pipeline/files.py` to adjust the list.
- Analysis is **capped at 30 files** by default (prompted at runtime). When a
  repo is larger, the cap is reported, never silently applied.
- The temp clone is removed automatically when the run finishes.
- Structure extraction is **pure-LLM** (works on any language); there is no
  tree-sitter or language-specific parser to install.

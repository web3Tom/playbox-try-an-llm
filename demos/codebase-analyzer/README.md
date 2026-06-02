# Codebase Analyzer

The flagship demo: point it at a repository and it runs a small **multi-stage
LLM pipeline** to build a knowledge graph of the codebase, then serves an
interactive graph dashboard. It is the clearest illustration of the template's
core idea — **route each task to the cheapest model that can do it**.

## What it does

```
clone / resolve target        [no model]   GitLab repo, local path, or bundled sample
  └─ scan                      gpt-5-nano  one-paragraph project description
  └─ analyze each file         gpt-5-mini  per-file summary, tags, imports, functions/classes
  └─ merge graph               [no model]    dedup nodes, prune dangling edges
  └─ classify architecture     gpt-5.4       group files into layers
  └─ write knowledge-graph.json -> dashboard renders it
```

One run exercises **nano → mini → gpt-5.4 → pure code**. The expensive model is
used exactly once, for the one step that needs whole-project reasoning.

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
and classes (hexagons)**; import edges connect the boxes. Use the search field
to highlight nodes, the **Show modules** toggle to collapse to file level, and
click any file or module to inspect it in the sidebar.

## Environment variables

- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` — required for the LLM stages
- `GITLAB_PAT` — only for target option 1 (cloning a private GitLab repo)

## Notes

- Analysis is **capped at 30 files** by default (prompted at runtime). When a
  repo is larger, the cap is reported, never silently applied.
- The temp clone is removed automatically when the run finishes.
- Structure extraction is **pure-LLM** (works on any language); there is no
  tree-sitter or language-specific parser to install.

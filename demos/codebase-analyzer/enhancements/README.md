# Codebase Analyzer — Module Enrichment (additive enhancement)

An **optional, fully additive** layer on top of the base codebase analyzer. It
adds two things the base demo doesn't have:

1. **Modules per file** — each file's top-level **functions and classes**, shown
   as child nodes nested inside their file (cytoscape compound "boxes").
2. **A nicer dashboard** — search, a module toggle, a files navigator, complexity
   badges, and a cleaner visual design.

> **Nothing in the base demo is modified.** This folder adds new files only —
> no edits to `analyze.py`, `pipeline/`, `prompts/`, or the original `dashboard/`.
> Delete this `enhancements/` folder and the base demo is exactly as it was.

## How it works

The base pipeline emits only `file` nodes. `schema.py` already permits
`function`/`class` node types, so enrichment is purely **additive data**:

```
analyze.py  ─────────────►  dashboard/public/knowledge-graph.json   (base; file nodes)
                                        │  (read, never written)
                                        ▼
enrich_modules.py  ──────►  enhancements/dashboard/public/knowledge-graph.json  (+ member nodes)
```

For each `file` node, `enrich.py` re-reads the source and asks **gpt-5.4-mini**
(the same `everyday-dev` role the base `analyze` stage uses) for the file's
top-level functions and classes. Each becomes a `function`/`class` node that
shares the file's `filePath`. The enhanced dashboard parents a member to the
file with the matching path — so containment needs **no schema or edge change**.

## Run it

```bash
# 1. Produce a base graph as usual (pick the SAME target in step 2).
uv run python demos/codebase-analyzer/analyze.py

# 2. Enrich it with per-file modules (re-resolves the source; the base run
#    deletes its temp clone, so this re-clones / re-opens the same target).
uv run python demos/codebase-analyzer/enhancements/enrich_modules.py

# 3. View the enriched graph.
cd demos/codebase-analyzer/enhancements/dashboard
npm install && npm run dev      # http://localhost:5175
```

The enhanced dashboard ships with an **enriched sample graph** already in
`dashboard/public/`, so step 3 renders compound boxes immediately — even before
you run steps 1–2 against a real repo.

## DevPod port

The enhanced dashboard runs on **5175** (the base one uses 5174) so both can run
side by side. Expose it the same way 5174 is exposed — add to your devfile:

```yaml
- name: codebase-analyzer-enhanced
  targetPort: 5175
```

## Files

| Path | What it is |
|------|-----------|
| `enrich.py` | Core enrichment logic (imports `pipeline/` — never edits it) |
| `enrich_modules.py` | Interactive entrypoint (mirrors `analyze.py`) |
| `prompts/module-extractor.md` | Editable prompt for top-level function/class extraction |
| `dashboard/` | Enhanced Vite/React app (port 5175, same 3-dependency stack) |
| `dashboard/public/knowledge-graph.json` | Enriched **sample** for out-of-the-box preview |

## Cost & scope notes

- Enrichment is **one extra gpt-5.4-mini call per analyzed file** — it roughly
  doubles the token cost of an analysis run. Skip it if you only need the
  file-level map.
- Extraction is **top-level only** (methods inside a class are not listed; the
  class is one node). This keeps the graph readable and the prompt cheap.
- Languages: extraction is LLM-based and language-agnostic, but quality tracks
  the model's familiarity with the language.

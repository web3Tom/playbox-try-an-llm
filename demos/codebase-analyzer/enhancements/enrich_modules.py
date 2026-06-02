"""Module enrichment — interactive entrypoint (additive; nothing existing changes).

Run it AFTER analyze.py, pointed at the SAME target you analyzed:

    uv run python demos/codebase-analyzer/enhancements/enrich_modules.py

It reads the graph the base analyzer produced, re-resolves the source (the base
run deletes its temp clone, so this re-clones / re-opens it), asks gpt-5.4-mini
for each file's top-level functions and classes, and writes an ENRICHED graph
into the enhanced dashboard's public dir:

    base graph:     dashboard/public/knowledge-graph.json        (untouched)
    enriched graph: enhancements/dashboard/public/knowledge-graph.json  (written here)

Then view it:

    cd demos/codebase-analyzer/enhancements/dashboard && npm install && npm run dev
    -> http://localhost:5175
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Make the sibling `pipeline/` package importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import clone  # noqa: E402
from pipeline.llm import init_client  # noqa: E402

from enrich import enrich  # noqa: E402  (local module, same dir)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("enrich")

HERE = Path(__file__).resolve().parent
ANALYZER_DIR = HERE.parent

# The base analyzer writes here; we read it as our input.
BASE_GRAPH = ANALYZER_DIR / "dashboard" / "public" / "knowledge-graph.json"
# We write the enriched graph into the enhanced dashboard's own public dir.
ENRICHED_GRAPH = HERE / "dashboard" / "public" / "knowledge-graph.json"


def prompt_target() -> clone.Target:
    """Same target selection as analyze.py, so enrichment hits the same repo."""
    print("\nWhich source should I read members from?")
    print("  1) Internal GitLab repo (clones via GITLAB_PAT)")
    print("  2) A local directory path")
    print("  3) Bundled sample repo  [default]")
    choice = input("Choose [1/2/3] (default 3): ").strip() or "3"

    if choice == "1":
        url = input("GitLab repo URL: ").strip()
        return clone.resolve_gitlab(url)
    if choice == "2":
        path = input("Local directory path: ").strip()
        return clone.resolve_local(path)
    return clone.resolve_sample()


def load_base_graph(path: Path) -> dict:
    """Load the base analyzer output. Fail loud if it isn't there yet."""
    if not path.is_file():
        raise FileNotFoundError(
            f"No base graph at {path}. Run analyze.py first, then enrich."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    load_dotenv()
    print("=" * 60)
    print("  Polestar Playbox — Codebase Analyzer · Module Enrichment")
    print("=" * 60)

    graph = load_base_graph(BASE_GRAPH)
    file_count = sum(1 for n in graph["nodes"] if n.get("type") == "file")
    print(f"\nLoaded base graph: {file_count} file node(s) from {BASE_GRAPH.name}")

    target = prompt_target()

    client = init_client()
    if client is None:
        clone.cleanup(target)
        raise RuntimeError(
            "Azure OpenAI credentials missing. Set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_API_KEY (see .env.example)."
        )

    try:
        enriched = enrich(graph, client, target.path)
    finally:
        clone.cleanup(target)

    member_count = sum(
        1 for n in enriched["nodes"] if n.get("type") in ("function", "class")
    )

    ENRICHED_GRAPH.parent.mkdir(parents=True, exist_ok=True)
    ENRICHED_GRAPH.write_text(json.dumps(enriched, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"  Added {member_count} module node(s) across {file_count} file(s).")
    print(f"  Wrote {ENRICHED_GRAPH.relative_to(Path.cwd())}"
          if ENRICHED_GRAPH.is_relative_to(Path.cwd()) else f"  Wrote {ENRICHED_GRAPH}")
    print("\n  View the enriched graph:")
    print("    cd demos/codebase-analyzer/enhancements/dashboard && npm install && npm run dev")
    print("    -> http://localhost:5175")
    print("=" * 60)


if __name__ == "__main__":
    main()

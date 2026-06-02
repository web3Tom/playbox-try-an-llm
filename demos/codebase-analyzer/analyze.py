"""Codebase analyzer — interactive entrypoint.

Run it:
    uv run python demos/codebase-analyzer/analyze.py

Asks what to analyze (internal GitLab repo / local path / bundled sample), then
runs the lean pipeline and writes a knowledge graph the dashboard can render:

    clone/resolve [no model]
      -> scan         [gpt-5-nano]   project description
      -> analyze      [gpt-5-mini]   per-file nodes + import/call/inherit edges
      -> merge        [no model]       dedup + prune dangling edges
      -> architecture [gpt-5.4]        group files into layers
      -> tour         [gpt-5.4]        ordered guided reading path
      -> write knowledge-graph.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from pipeline import clone
from pipeline.architecture import classify_layers
from pipeline.analyze_files import analyze_files
from pipeline.files import enumerate_source_files
from pipeline.llm import init_client
from pipeline.merge import assemble
from pipeline.scan import scan_project
from pipeline.schema import KnowledgeGraph, Project, validate
from pipeline.tour import build_tour

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("analyzer")

# Where the dashboard reads its data from (Vite serves /public at the web root).
GRAPH_OUTPUT = Path(__file__).resolve().parent / "dashboard" / "public" / "knowledge-graph.json"


def prompt_target() -> clone.Target:
    """Interactive target selection. Enter = bundled sample (zero setup)."""
    print("\nWhat should I analyze?")
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


def run_pipeline(target: clone.Target, max_files: int) -> KnowledgeGraph:
    """Execute the four stages against an already-resolved target directory."""
    scan = enumerate_source_files(target.path, max_files=max_files)
    if not scan.files:
        raise RuntimeError(f"No analysable source files found in {target.path}")
    if scan.truncated:
        logger.warning(
            "Analyzing %d of %d files (capped at %d). Increase the cap to cover the rest.",
            len(scan.files), scan.total_found, max_files,
        )

    client = init_client()
    if client is None:
        raise RuntimeError(
            "Azure OpenAI credentials missing. Set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_API_KEY (see .env.example)."
        )

    logger.info("[scan] summarizing project (gpt-5-nano)")
    description = scan_project(client, target.path, target.name)

    logger.info("[analyze] %d files (gpt-5-mini)", len(scan.files))
    node_groups, edge_groups = analyze_files(client, str(target.path), scan.files)

    logger.info("[merge] assembling graph (no model)")
    nodes, edges = assemble(node_groups, edge_groups)

    logger.info("[architecture] classifying layers (gpt-5.4)")
    layers = classify_layers(client, nodes)

    logger.info("[tour] building guided reading order (gpt-5.4)")
    tour = build_tour(client, description, nodes)

    project = Project(
        name=target.name,
        description=description,
        languages=scan.languages,
        fileCount=scan.total_found,
        analyzedFileCount=len([n for n in nodes if n.type == "file"]),
        truncated=scan.truncated,
    )
    return KnowledgeGraph(project=project, nodes=nodes, edges=edges, layers=layers, tour=tour)


def main() -> None:
    load_dotenv()
    print("=" * 60)
    print("  Polestar Playbox — Codebase Analyzer")
    print("=" * 60)

    target = prompt_target()
    raw_cap = input("Max files to analyze (default 30): ").strip()
    max_files = int(raw_cap) if raw_cap.isdigit() and int(raw_cap) > 0 else 30

    try:
        graph = run_pipeline(target, max_files)
    finally:
        clone.cleanup(target)

    problems = validate(graph)
    if problems:
        logger.warning("Graph validation found %d issue(s):", len(problems))
        for p in problems[:10]:
            logger.warning("  - %s", p)

    GRAPH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_OUTPUT.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"  Analyzed {graph.project.analyzedFileCount} files into "
          f"{len(graph.nodes)} nodes, {len(graph.edges)} edges, "
          f"{len(graph.layers)} layers, {len(graph.tour)} tour steps.")
    print(f"  Wrote {GRAPH_OUTPUT.relative_to(Path.cwd())}"
          if GRAPH_OUTPUT.is_relative_to(Path.cwd()) else f"  Wrote {GRAPH_OUTPUT}")
    print("\n  View the graph:")
    print("    cd demos/codebase-analyzer/dashboard && npm install && npm run dev")
    print("    -> http://localhost:5174")
    print("=" * 60)


if __name__ == "__main__":
    main()

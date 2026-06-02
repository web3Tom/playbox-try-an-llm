"""Analyze stage [gpt-5.4-mini] — the high-volume per-file work.

For each file we build one graph node deterministically (so every analyzed file
is guaranteed a node) and ask the model only for the judgment parts: summary,
complexity, tags, which sibling files it imports, and the file's top-level
members (functions and classes). Import targets are the model's best guess at
repo-relative paths; merge.py later prunes the ones that don't resolve. Members
become `function`/`class` nodes sharing the file's path, so the dashboard can
nest them inside their file. This is the workhorse, so it routes to mini — never
the orchestrator, even though it runs once per file.
"""

from __future__ import annotations

import logging

from openai import AzureOpenAI

from .files import read_text
from .llm import call_json, load_prompt
from .schema import Edge, Node, normalize_complexity

logger = logging.getLogger(__name__)


def file_node_id(rel_path: str) -> str:
    return f"file:{rel_path}"


# Member types the analyzer is allowed to emit (a subset of schema.NODE_TYPES).
_MEMBER_TYPES = {"function", "class"}


def _member_nodes(rel_path: str, raw_members: list) -> list[Node]:
    """Build `function`/`class` nodes for a file's top-level members.

    Each member shares the file's ``filePath`` (the dashboard's grouping key) and
    gets a stable, unique id like ``function:app.py::create_app``. Malformed
    entries (missing name / bad type) are dropped, never allowed to poison the
    graph. Layer is assigned later, inherited from the file in the architecture
    stage.
    """
    nodes: list[Node] = []
    taken: set[str] = set()
    for raw in raw_members or []:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name", "")).strip()
        mtype = str(raw.get("type", "")).strip().lower()
        if not name or mtype not in _MEMBER_TYPES:
            continue
        base = f"{mtype}:{rel_path}::{name}"
        node_id, n = base, 2
        while node_id in taken:  # keep ids unique if a name repeats in the file
            node_id, n = f"{base}#{n}", n + 1
        taken.add(node_id)
        nodes.append(
            Node(
                id=node_id,
                type=mtype,
                name=name,
                filePath=rel_path,
                summary=str(raw.get("summary", "")).strip(),
                tags=[mtype],
                complexity=normalize_complexity(raw.get("complexity")),
            )
        )
    return nodes


def analyze_files(
    client: AzureOpenAI, root: str, rel_paths: list[str]
) -> tuple[list[list[Node]], list[list[Edge]]]:
    """Analyze each file. Returns per-file node groups and edge groups for merge().

    A single file failing is logged and skipped rather than aborting the whole
    run — but the failure is surfaced, never swallowed silently.
    """
    system = load_prompt("file-analyzer")
    node_groups: list[list[Node]] = []
    edge_groups: list[list[Edge]] = []

    for i, rel in enumerate(rel_paths, start=1):
        logger.info("Analyzing (%d/%d) %s", i, len(rel_paths), rel)
        try:
            source = read_text(root, rel)
            result = call_json(client, "analyze", system, f"Path: {rel}\n\n```\n{source}\n```")
        except RuntimeError as exc:
            logger.warning("Skipping %s: %s", rel, exc)
            continue

        node = Node(
            id=file_node_id(rel),
            type="file",
            name=rel.rsplit("/", 1)[-1],
            filePath=rel,
            summary=result.get("summary", "").strip(),
            tags=[str(t) for t in result.get("tags", [])][:5],
            complexity=normalize_complexity(result.get("complexity")),
        )
        edges = [
            Edge(source=node.id, target=file_node_id(imp.strip().lstrip("./")), type="imports")
            for imp in result.get("imports", [])
            if isinstance(imp, str) and imp.strip()
        ]
        # The file node plus its top-level members share one group; merge() keeps
        # them together and dedups by id.
        node_groups.append([node, *_member_nodes(rel, result.get("members", []))])
        edge_groups.append(edges)

    return node_groups, edge_groups

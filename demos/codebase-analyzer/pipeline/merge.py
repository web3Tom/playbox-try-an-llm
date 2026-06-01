"""Deterministic graph assembly — the [no model] core step.

The file-analyzer stage emits one little graph per file. Merging them is pure
data work: deduplicate nodes by id, deduplicate edges, and drop edges that point
at a node nobody produced (a "dangling" edge — common when the LLM references a
symbol in a file we didn't analyse). A model would be slower, costlier, and less
reliable than this. Adapted/trimmed from Understand-Anything's merge-batch-graphs.py.
"""

from __future__ import annotations

import logging

from .schema import Edge, Node, normalize_complexity

logger = logging.getLogger(__name__)


def merge_nodes(node_groups: list[list[Node]]) -> list[Node]:
    """Flatten per-file node lists, keeping the first occurrence of each id."""
    seen: dict[str, Node] = {}
    for group in node_groups:
        for node in group:
            node.complexity = normalize_complexity(node.complexity)
            if node.id not in seen:
                seen[node.id] = node
    return list(seen.values())


def merge_edges(edge_groups: list[list[Edge]], node_ids: set[str]) -> tuple[list[Edge], int]:
    """Deduplicate edges and drop any whose endpoints are not real nodes.

    Returns ``(edges, dropped_count)`` so the caller can surface how many
    dangling references were pruned rather than hiding them.
    """
    kept: dict[tuple[str, str, str], Edge] = {}
    dropped = 0
    for group in edge_groups:
        for edge in group:
            if edge.source not in node_ids or edge.target not in node_ids:
                dropped += 1
                continue
            if edge.source == edge.target:  # self-loops add noise to the graph
                dropped += 1
                continue
            key = (edge.source, edge.target, edge.type)
            kept.setdefault(key, edge)
    return list(kept.values()), dropped


def assemble(node_groups: list[list[Node]], edge_groups: list[list[Edge]]) -> tuple[list[Node], list[Edge]]:
    """Merge per-file node/edge lists into a single deduplicated graph."""
    nodes = merge_nodes(node_groups)
    node_ids = {n.id for n in nodes}
    edges, dropped = merge_edges(edge_groups, node_ids)
    if dropped:
        logger.info("Dropped %d dangling/self edge(s) during merge", dropped)
    return nodes, edges

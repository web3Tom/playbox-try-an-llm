"""Knowledge-graph data contract.

This is the single interchange format between the Python pipeline and the React
dashboard. The pipeline builds a `KnowledgeGraph` and writes it to
`knowledge-graph.json`; the dashboard reads that file and renders it.

Adapted (and heavily trimmed) from Understand-Anything's `schema.ts`. We keep
four entities — Project, Node, Edge, Layer — and drop everything else
(tour, domain, diff, fingerprints).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

# Allowed enum values. We validate against these so a malformed LLM response
# fails loud here rather than silently producing a broken dashboard.
NODE_TYPES = ("file", "function", "class")
EDGE_TYPES = ("imports", "calls", "related", "inherits")
COMPLEXITY = ("simple", "moderate", "complex")

# Maps the loose values models tend to emit onto our canonical set.
_COMPLEXITY_ALIASES = {
    "low": "simple",
    "medium": "moderate",
    "high": "complex",
}


def normalize_complexity(value: str | None) -> str:
    """Coerce a model-supplied complexity onto the canonical set.

    Defaults to ``moderate`` for anything unrecognised — never raises, because a
    fuzzy complexity label should not abort a whole analysis run.
    """
    if not value:
        return "moderate"
    v = value.strip().lower()
    v = _COMPLEXITY_ALIASES.get(v, v)
    return v if v in COMPLEXITY else "moderate"


@dataclass
class Node:
    id: str
    type: str
    name: str
    filePath: str
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    complexity: str = "moderate"
    layer: str | None = None  # assigned in the architecture stage


@dataclass
class Edge:
    source: str
    target: str
    type: str


@dataclass
class Layer:
    id: str
    name: str
    description: str
    nodeIds: list[str] = field(default_factory=list)


@dataclass
class Project:
    name: str
    description: str = ""
    languages: list[str] = field(default_factory=list)
    fileCount: int = 0
    analyzedFileCount: int = 0
    truncated: bool = False  # True when fileCount was capped — surfaced, not hidden


@dataclass
class KnowledgeGraph:
    project: Project
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    layers: list[Layer] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return asdict(self)


def validate(graph: KnowledgeGraph) -> list[str]:
    """Return a list of human-readable problems. Empty list == valid.

    We validate rather than trust: the nodes/edges come from an LLM, so we
    check enum membership and that every edge endpoint is a real node.
    """
    problems: list[str] = []
    node_ids = {n.id for n in graph.nodes}

    if len(node_ids) != len(graph.nodes):
        problems.append("duplicate node ids present")

    for n in graph.nodes:
        if n.type not in NODE_TYPES:
            problems.append(f"node {n.id!r} has invalid type {n.type!r}")
        if n.complexity not in COMPLEXITY:
            problems.append(f"node {n.id!r} has invalid complexity {n.complexity!r}")

    for e in graph.edges:
        if e.type not in EDGE_TYPES:
            problems.append(f"edge {e.source}->{e.target} has invalid type {e.type!r}")
        if e.source not in node_ids:
            problems.append(f"edge source {e.source!r} is not a known node")
        if e.target not in node_ids:
            problems.append(f"edge target {e.target!r} is not a known node")

    return problems

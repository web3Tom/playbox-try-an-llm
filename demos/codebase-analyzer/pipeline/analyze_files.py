"""Analyze stage [gpt-5-mini] — the high-volume per-file work.

For each file we build one graph node deterministically (so every analyzed file
is guaranteed a node) and ask the model only for the judgment parts: summary,
complexity, tags, which sibling files it imports, and the file's top-level
members (functions and classes) plus the calls/inheritance between them. Import
targets and member relationships are the model's best guess; merge.py later
prunes any that don't resolve. Members become `function`/`class` nodes sharing
the file's path (so the dashboard can nest them inside their file), and
member->member `calls`/`inherits` edges turn the graph into a real call map.

This is the workhorse, so it routes to mini — never the orchestrator, even
though it runs once per file. The per-file calls are independent blocking I/O,
so we fan them out across a small thread pool (bounded to stay under the APIM
rate limit) instead of running them strictly one at a time. The member-
relationship edges are resolved AFTER all files are analyzed, from a global name
index, at zero extra API cost — the model already returned the call/extends
names in the same per-file response.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from openai import AzureOpenAI

from .files import read_text
from .llm import call_json, load_prompt
from .schema import Edge, Node, normalize_complexity

logger = logging.getLogger(__name__)

# How many per-file analyze calls run concurrently. Kept small on purpose: the
# Playbox APIM enforces a per-deployment requests-per-minute quota, and a demo
# that hammers it teaches the wrong lesson. Bounded fan-out > unbounded.
DEFAULT_MAX_WORKERS = 4

# Member types the analyzer is allowed to emit (a subset of schema.NODE_TYPES).
_MEMBER_TYPES = {"function", "class"}


def file_node_id(rel_path: str) -> str:
    return f"file:{rel_path}"


def _member_nodes(rel_path: str, raw_members: list) -> list[tuple[Node, dict]]:
    """Build ``(node, raw)`` pairs for a file's top-level members.

    Each member shares the file's ``filePath`` (the dashboard's grouping key) and
    gets a stable, unique id like ``function:app.py::create_app``. The raw dict is
    carried alongside so a later pass can resolve its ``calls``/``extends`` into
    edges. Malformed entries (missing name / bad type) are dropped, never allowed
    to poison the graph. Layer is assigned later, inherited from the file.
    """
    pairs: list[tuple[Node, dict]] = []
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
        node = Node(
            id=node_id,
            type=mtype,
            name=name,
            filePath=rel_path,
            summary=str(raw.get("summary", "")).strip(),
            tags=[mtype],
            complexity=normalize_complexity(raw.get("complexity")),
        )
        pairs.append((node, raw))
    return pairs


def _as_names(value) -> list[str]:
    """Coerce a model-supplied calls/extends field into a clean list of names."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _member_edges(pairs: list[tuple[Node, dict]]) -> list[Edge]:
    """Resolve member ``calls``/``extends`` names into `calls`/`inherits` edges.

    Resolution is deterministic: a name is matched first against members defined
    in the SAME file, then against a global name index but only if that name is
    unambiguous (exactly one member repo-wide). Ambiguous or unknown names are
    dropped here; merge.py prunes anything that still dangles. No model is
    involved — the names were already returned by the per-file analyze call.
    """
    global_index: dict[str, list[str]] = {}
    by_file: dict[str, dict[str, str]] = {}
    for node, _raw in pairs:
        global_index.setdefault(node.name, []).append(node.id)
        by_file.setdefault(node.filePath, {})[node.name] = node.id

    def resolve(name: str, file_path: str) -> str | None:
        local = by_file.get(file_path, {})
        if name in local:
            return local[name]
        ids = global_index.get(name, [])
        return ids[0] if len(ids) == 1 else None

    edges: list[Edge] = []
    for node, raw in pairs:
        for callee in _as_names(raw.get("calls")):
            target = resolve(callee, node.filePath)
            if target and target != node.id:
                edges.append(Edge(source=node.id, target=target, type="calls"))
        if node.type == "class":
            for base in _as_names(raw.get("extends")):
                target = resolve(base, node.filePath)
                if target and target != node.id:
                    edges.append(Edge(source=node.id, target=target, type="inherits"))
    return edges


def _analyze_one(
    client: AzureOpenAI, root: str, system: str, rel: str
) -> tuple[Node, list[tuple[Node, dict]], list[Edge]]:
    """Analyze a single file. Raises RuntimeError on read/model/parse failure."""
    source = read_text(root, rel)
    result = call_json(client, "analyze", system, f"Path: {rel}\n\n```\n{source}\n```")

    node = Node(
        id=file_node_id(rel),
        type="file",
        name=rel.rsplit("/", 1)[-1],
        filePath=rel,
        summary=result.get("summary", "").strip(),
        tags=[str(t) for t in result.get("tags", [])][:5],
        complexity=normalize_complexity(result.get("complexity")),
    )
    import_edges = [
        Edge(source=node.id, target=file_node_id(imp.strip().lstrip("./")), type="imports")
        for imp in result.get("imports", [])
        if isinstance(imp, str) and imp.strip()
    ]
    members = _member_nodes(rel, result.get("members", []))
    return node, members, import_edges


def analyze_files(
    client: AzureOpenAI,
    root: str,
    rel_paths: list[str],
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> tuple[list[list[Node]], list[list[Edge]]]:
    """Analyze each file concurrently. Returns node/edge groups for merge().

    Files are analyzed in a bounded thread pool (each call is independent
    blocking I/O), with results kept in input order so output stays
    deterministic. A single file failing is logged and skipped rather than
    aborting the whole run — surfaced, never swallowed. After every file is in,
    one extra pass turns the members' call/extends names into member->member
    edges at no additional API cost.
    """
    system = load_prompt("file-analyzer")
    total = len(rel_paths)

    def work(item: tuple[int, str]):
        i, rel = item
        logger.info("Analyzing (%d/%d) %s", i + 1, total, rel)
        try:
            return _analyze_one(client, root, system, rel)
        except RuntimeError as exc:
            logger.warning("Skipping %s: %s", rel, exc)
            return None

    workers = max(1, min(max_workers, total or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(work, enumerate(rel_paths)))

    node_groups: list[list[Node]] = []
    edge_groups: list[list[Edge]] = []
    all_pairs: list[tuple[Node, dict]] = []
    for res in results:
        if res is None:
            continue
        file_node, member_pairs, import_edges = res
        node_groups.append([file_node, *(node for node, _ in member_pairs)])
        edge_groups.append(import_edges)
        all_pairs.extend(member_pairs)

    # Member-relationship edges are computed once, after the global member set is
    # known, so cross-file calls/inheritance can resolve. Zero extra model calls.
    edge_groups.append(_member_edges(all_pairs))
    return node_groups, edge_groups

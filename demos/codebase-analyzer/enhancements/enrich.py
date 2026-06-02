"""Module-level enrichment — additive second pass over an existing graph.

The base pipeline emits only `file` nodes. This pass re-reads each analyzed
file and asks the everyday-dev model (gpt-5.4-mini) for the file's TOP-LEVEL
functions and classes, then appends them as `function`/`class` nodes that share
the file's `filePath`. The enhanced dashboard groups members under their file by
that shared path (cytoscape compound nodes) — so no schema or edge changes are
needed, and the original pipeline/dashboard are left completely untouched.

Nothing here mutates the input graph: `enrich()` returns a NEW dict.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Make the sibling `pipeline/` package importable when run from enhancements/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.files import read_text  # noqa: E402  (path bootstrap must run first)
from pipeline.llm import call_json  # noqa: E402
from pipeline.schema import NODE_TYPES, normalize_complexity  # noqa: E402

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "module-extractor.md"

# Member extraction is per-file, high-volume, structured work — the everyday-dev
# role, exactly like the base analyze stage. We reuse that routing deliberately.
ENRICH_ROLE = "analyze"

# Member node types this pass is allowed to create (a subset of NODE_TYPES).
_MEMBER_TYPES = {"function", "class"}


def load_prompt() -> str:
    """Load the editable extractor prompt."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def _member_id(file_path: str, type_: str, name: str, taken: set[str]) -> str:
    """Build a stable, unique id like ``function:app.py::create_app``.

    If a name repeats within a file (overloads, re-defs), a numeric suffix keeps
    the id unique so the graph never has duplicate node ids.
    """
    base = f"{type_}:{file_path}::{name}"
    candidate, n = base, 2
    while candidate in taken:
        candidate = f"{base}#{n}"
        n += 1
    taken.add(candidate)
    return candidate


def extract_members(
    client, root: str | Path, file_node: dict, prompt: str, taken_ids: set[str]
) -> list[dict]:
    """Return member nodes (as dicts) for one file node, or [] on any problem.

    Failures here are per-file and non-fatal: one unreadable file or a model
    hiccup must not abort enrichment of the rest. We log and skip.
    """
    file_path = file_node["filePath"]
    try:
        source = read_text(root, file_path)
    except OSError as exc:
        logger.warning("skip %s — could not read source (%s)", file_path, exc)
        return []

    user = f"PATH: {file_path}\n\nCONTENTS:\n{source}"
    try:
        result = call_json(client, ENRICH_ROLE, prompt, user)
    except RuntimeError as exc:
        logger.warning("skip %s — extraction failed (%s)", file_path, exc)
        return []

    members: list[dict] = []
    for raw in result.get("members", []):
        name = (raw.get("name") or "").strip()
        type_ = (raw.get("type") or "").strip().lower()
        if not name or type_ not in _MEMBER_TYPES:
            continue  # drop malformed entries rather than poison the graph
        members.append(
            {
                "id": _member_id(file_path, type_, name, taken_ids),
                "type": type_,
                "name": name,
                "filePath": file_path,           # shared path == dashboard grouping key
                "summary": (raw.get("summary") or "").strip(),
                "tags": [type_],
                "complexity": normalize_complexity(raw.get("complexity")),
                "layer": file_node.get("layer"),  # inherit the file's layer colour
            }
        )
    logger.info("%s -> %d member(s)", file_path, len(members))
    return members


def enrich(graph: dict, client, root: str | Path) -> dict:
    """Return a NEW graph dict with `function`/`class` member nodes appended.

    Only `file` nodes are expanded. The project, edges, and layers are carried
    through unchanged; member nodes are added to `nodes` only.
    """
    prompt = load_prompt()
    file_nodes = [n for n in graph["nodes"] if n.get("type") == "file"]
    taken_ids: set[str] = {n["id"] for n in graph["nodes"]}

    new_members: list[dict] = []
    for fn in file_nodes:
        new_members.extend(extract_members(client, root, fn, prompt, taken_ids))

    enriched_nodes = [*graph["nodes"], *new_members]
    logger.info(
        "enrichment added %d member node(s) across %d file(s)",
        len(new_members), len(file_nodes),
    )

    # Shallow-copy the top level; replace nodes with the extended list. Inputs
    # are not mutated (immutability rule) — callers keep the original graph.
    return {**graph, "nodes": enriched_nodes}


def _is_supported_node_types(graph: dict) -> bool:
    """Sanity check that every node type we emit is in the canonical set."""
    return all(n.get("type") in NODE_TYPES for n in graph["nodes"])

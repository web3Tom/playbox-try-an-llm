"""Architecture stage [gpt-5.4] — the one step that earns the expensive model.

Classifying files into layers requires seeing the whole project at once and
reasoning about how the pieces relate — genuine multi-file reasoning, not the
per-file pattern-matching of the analyze stage. That is why this single step,
and only this step, routes to the orchestrator model.
"""

from __future__ import annotations

import json
import logging

from openai import AzureOpenAI

from .analyze_files import file_node_id
from .llm import call_json, load_prompt
from .schema import Layer, Node

logger = logging.getLogger(__name__)


def classify_layers(client: AzureOpenAI, nodes: list[Node]) -> list[Layer]:
    """Group file nodes into architectural layers and stamp each node's `layer`.

    Mutates `nodes` in place to set `node.layer`. Returns the Layer list. Any
    file the model forgot is logged (fail loud) but does not abort the run.
    """
    file_nodes = [n for n in nodes if n.type == "file"]
    catalog = [{"path": n.filePath, "summary": n.summary} for n in file_nodes]
    user = "Files:\n" + json.dumps(catalog, indent=2)

    result = call_json(client, "architecture", load_prompt("architecture"), user)

    layers: list[Layer] = []
    by_path = {n.filePath: n for n in file_nodes}
    assigned: set[str] = set()

    for i, raw in enumerate(result.get("layers", [])):
        name = str(raw.get("name", f"Layer {i + 1}"))
        layer_id = f"layer:{i}"
        node_ids: list[str] = []
        for path in raw.get("files", []):
            node = by_path.get(path)
            if node is None:
                continue
            node.layer = layer_id
            node_ids.append(file_node_id(path))
            assigned.add(path)
        layers.append(Layer(id=layer_id, name=name, description=str(raw.get("description", "")), nodeIds=node_ids))

    missing = set(by_path) - assigned
    if missing:
        logger.warning("Architecture stage left %d file(s) unassigned: %s", len(missing), sorted(missing))

    return layers

"""Tour stage [gpt-5.4] — the orchestrator builds a guided reading order.

Designing a good first-read path through an unfamiliar codebase means holding
the whole project in view at once and reasoning about dependencies and intent —
the same holistic judgment that earns the architecture stage the orchestrator
model. So the tour routes to gpt-5.4 too. The output is a short ordered list of
steps, each anchored to one real file, that the dashboard renders as a
click-through walkthrough.
"""

from __future__ import annotations

import json
import logging

from openai import AzureOpenAI

from .llm import call_json, load_prompt
from .schema import Node, TourStep

logger = logging.getLogger(__name__)


def build_tour(client: AzureOpenAI, description: str, nodes: list[Node]) -> list[TourStep]:
    """Produce an ordered, file-anchored walkthrough of the project.

    Only file nodes are offered to the model. Any step pointing at a path we do
    not recognise is dropped (and logged — fail loud, not silent) so the
    dashboard never links a tour step to a node that does not exist.
    """
    file_nodes = [n for n in nodes if n.type == "file"]
    catalog = [{"path": n.filePath, "summary": n.summary} for n in file_nodes]
    user = f"Project: {description}\n\nFiles:\n" + json.dumps(catalog, indent=2)

    result = call_json(client, "tour", load_prompt("tour"), user)

    known = {n.filePath for n in file_nodes}
    steps: list[TourStep] = []
    for raw in result.get("steps", []):
        if not isinstance(raw, dict):
            continue
        path = str(raw.get("filePath", "")).strip()
        if path not in known:
            logger.warning("Tour step references unknown file %r — dropping", path)
            continue
        steps.append(
            TourStep(
                order=len(steps) + 1,
                title=str(raw.get("title", path)).strip() or path,
                filePath=path,
                explanation=str(raw.get("explanation", "")).strip(),
            )
        )
    return steps

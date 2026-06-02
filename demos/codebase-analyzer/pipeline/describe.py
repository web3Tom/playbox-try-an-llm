"""Describe stage [gpt-5-nano] — infer the project description from code.

The `scan` stage reads the README/manifests, but a generic template or empty
README tells you nothing — and a description that says "purpose cannot be
determined" is worse than useless on the dashboard. The real signal is in the
code, which only exists after `analyze`. So when `scan` reports its result is
uninformative, this stage synthesizes a description from the EVIDENCE the
analysis already produced: each file's one-line summary, its role tags, and the
project's languages. Summarizing already-summarized content is classification-
grade work, so it routes to nano. It never raises — a failure just leaves the
(weak) scan description in place.
"""

from __future__ import annotations

import logging

from openai import AzureOpenAI

from .llm import call_json, load_prompt
from .schema import Node

logger = logging.getLogger(__name__)

_MAX_FILES = 40           # cap the digest so the prompt stays cheap
_MAX_DIGEST_CHARS = 4000


def synthesize_description(
    client: AzureOpenAI, name: str, languages: list[str], nodes: list[Node]
) -> str:
    """Infer a project description from analyzed file summaries. ``""`` if it can't."""
    file_nodes = [n for n in nodes if n.type == "file" and n.summary]
    if not file_nodes:
        return ""

    lines = []
    for n in file_nodes[:_MAX_FILES]:
        tags = ", ".join(n.tags) if n.tags else ""
        lines.append(f"- {n.filePath} [{tags}]: {n.summary}")
    digest = "\n".join(lines)[:_MAX_DIGEST_CHARS]
    langs = ", ".join(languages) if languages else "unknown"

    user = f"Project name: {name}\nLanguages: {langs}\n\nFile summaries:\n{digest}"
    try:
        result = call_json(client, "describe", load_prompt("describe"), user)
    except RuntimeError as exc:
        logger.warning("Describe stage failed (%s) — keeping the scan description", exc)
        return ""
    return result.get("description", "").strip()

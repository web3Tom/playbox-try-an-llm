"""Scan stage [gpt-5-nano] — summarize the project from its README/manifests.

Reading the files is deterministic; turning prose into a one-paragraph
description is the genuine (cheap) judgment call, so it routes to nano.
"""

from __future__ import annotations

import logging
from pathlib import Path

from openai import AzureOpenAI

from .llm import call_json, load_prompt

logger = logging.getLogger(__name__)

# Files worth feeding to the scanner, in priority order.
_CONTEXT_FILES = [
    "README.md", "README.rst", "README.txt", "readme.md",
    "pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml",
]
_MAX_CONTEXT_CHARS = 6000


def scan_project(client: AzureOpenAI, root: str | Path, name: str) -> str:
    """Return a short project description. Empty string if no context found."""
    root = Path(root)
    chunks: list[str] = []
    for fname in _CONTEXT_FILES:
        fpath = root / fname
        if fpath.is_file():
            chunks.append(f"--- {fname} ---\n{fpath.read_text(encoding='utf-8', errors='replace')}")
        if sum(len(c) for c in chunks) > _MAX_CONTEXT_CHARS:
            break

    if not chunks:
        logger.info("No README/manifest found; skipping description")
        return ""

    context = "\n\n".join(chunks)[:_MAX_CONTEXT_CHARS]
    user = f"Project name: {name}\n\n{context}"
    result = call_json(client, "scan", load_prompt("scan"), user)
    return result.get("description", "").strip()

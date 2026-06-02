"""Select stage [gpt-5-nano] — triage which files are worth analysing.

When a repo has more analysable files than the budget, *which* ones to read is a
genuine judgment call, not a transform — so a cheap nano call ranks them by
architectural significance, over paths ALONE (never file contents). The
deterministic guards in ``files.py`` already stripped the obvious noise
(generated code, configs, vendored deps) and capped per-directory counts; this
stage makes the final pick from what's left.

It can never break the run: an empty/garbage response or an API error falls back
to the deterministic selection, and any path the model invents is discarded.
This is the routing lesson in miniature — a cheap model does the triage so the
pricier per-file ``analyze`` calls are spent only on files worth reading.
"""

from __future__ import annotations

import logging

from openai import AzureOpenAI

from .llm import call_json, load_prompt

logger = logging.getLogger(__name__)


def _as_paths(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def select_files(
    client: AzureOpenAI,
    description: str,
    candidates: list[str],
    fallback: list[str],
    max_files: int,
) -> list[str]:
    """Choose up to ``max_files`` paths from ``candidates`` by significance.

    Returns ``fallback`` (the deterministic dir-capped pick) unchanged when there
    is nothing to triage, or whenever the model errors or returns no usable
    paths. Paths not present in ``candidates`` are dropped (no hallucinated
    files), and the result is backfilled from ``fallback`` if the model
    under-selects — so the budget is always used.
    """
    if len(candidates) <= max_files:
        return candidates

    user = (
        f"Project: {description}\n\n"
        f"Choose the {max_files} most important files for understanding this "
        f"codebase's architecture, from these {len(candidates)} candidates:\n"
        + "\n".join(candidates)
    )
    try:
        result = call_json(client, "select", load_prompt("select"), user)
    except RuntimeError as exc:
        logger.warning("Select stage failed (%s) — using deterministic selection", exc)
        return fallback

    allowed = set(candidates)
    chosen = [p for p in _as_paths(result.get("files")) if p in allowed]
    if not chosen:
        logger.warning("Select stage returned no valid paths — using deterministic selection")
        return fallback

    # De-dup while preserving the model's order, then cap.
    seen: set[str] = set()
    ordered = [p for p in chosen if not (p in seen or seen.add(p))][:max_files]

    # Backfill from the deterministic pick if the model under-selected.
    if len(ordered) < max_files:
        for path in fallback:
            if path not in seen:
                ordered.append(path)
                seen.add(path)
                if len(ordered) >= max_files:
                    break
    return ordered

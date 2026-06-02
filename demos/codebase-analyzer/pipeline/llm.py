"""Shared Azure OpenAI access + the model-routing table.

This is where the template's central lesson lives in code: each pipeline stage
maps to a SPECIFIC model, mirroring `.kilo/kilo.jsonc`. The cheap classification
(scan) runs on nano; the high-volume per-file work runs on mini; the one
holistic-reasoning step (architecture) earns gpt-5.4. Nothing routes to a bigger
model than its job needs.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from openai import AzureOpenAI, OpenAIError

logger = logging.getLogger(__name__)

# Stage -> model. Keep these in lockstep with `.kilo/kilo.jsonc` profiles.
ROLE_MODELS = {
    "scan": "gpt-5-nano",          # summarizer role: cheap, classification-grade
    "analyze": "gpt-5-mini",       # everyday-dev role: the high-volume workhorse
    "architecture": "gpt-5.4",       # orchestrator role: holistic reasoning
}

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def init_client() -> AzureOpenAI | None:
    """Build the Azure client from env, or None if credentials are absent."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        logger.warning("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
        return None
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
    return AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)


def load_prompt(name: str) -> str:
    """Load a stage's system prompt from prompts/<name>.md (editable without code changes)."""
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def call_json(client: AzureOpenAI, role: str, system: str, user: str) -> dict:
    """Run a stage via the Responses API and parse its JSON object response.

    Routes to ``ROLE_MODELS[role]``. The prompt mandates a JSON object and
    ``_parse_json`` strips any code fences, so we rely on that rather than a
    provider-specific structured-output param. Raises on API failure (fail loud)
    and on a response that isn't parseable JSON.
    """
    model = ROLE_MODELS[role]
    logger.info("[%s] calling %s", role, model)
    try:
        resp = client.responses.create(
            model=model,
            instructions=system,
            input=user,
        )
    except OpenAIError as exc:
        raise RuntimeError(f"{role} stage ({model}) failed: {exc}") from exc

    return _parse_json(resp.output_text)


def _parse_json(content: str | None) -> dict:
    """Parse a model's JSON, tolerating ```json fences some models still add."""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"model did not return valid JSON: {exc}") from exc

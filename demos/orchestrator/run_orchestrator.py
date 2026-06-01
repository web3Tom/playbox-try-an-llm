"""
Orchestrator demo: reasoning model (gpt-5.4) plans, then delegates to gpt-5.4-mini.

Demonstrates the orchestrator pattern where:
  1. gpt-5.4 (reasoning model) reads the spec and produces a numbered implementation plan
  2. Plan is printed for inspection
  3. (In a full pipeline) gpt-5.4-mini would implement from the plan

Env vars:
  AZURE_OPENAI_ENDPOINT: Azure OpenAI deployment endpoint
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
"""

import logging
import os

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAIError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_azure_client() -> AzureOpenAI | None:
    """Initialize Azure OpenAI client from environment variables."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        logger.error("Missing Azure credentials: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set")
        return None

    try:
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
        )
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None


def read_spec(spec_file: str = "demos/orchestrator/spec.md") -> str:
    """Read specification from file."""
    try:
        with open(spec_file, "r") as f:
            spec = f.read()
        logger.info(f"Loaded spec from {spec_file}")
        return spec
    except FileNotFoundError:
        logger.error(f"Spec file not found: {spec_file}")
        raise


def generate_plan(client: AzureOpenAI, spec: str) -> str:
    """Use gpt-5.4 (reasoning model) to generate implementation plan."""
    try:
        logger.info("Generating plan with gpt-5.4...")
        response = client.responses.create(
            model="gpt-5.4",
            instructions="You are an expert architect. Read the spec and produce a concise, numbered implementation plan.",
            input=f"Specification:\n\n{spec}\n\nProduce a numbered plan for implementation.",
        )
        plan = response.output_text
        logger.info("Plan generated successfully")
        return plan
    except OpenAIError as e:
        logger.error(f"API error during planning: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during planning: {e}")
        raise


def main():
    """Run orchestrator demo."""
    load_dotenv()
    client = init_azure_client()
    if not client:
        logger.error("Cannot proceed without Azure OpenAI client.")
        return

    try:
        spec = read_spec()
        plan = generate_plan(client, spec)

        print("\n" + "="*70)
        print("IMPLEMENTATION PLAN (from gpt-5.4)")
        print("="*70)
        print(plan)
        print("="*70 + "\n")

        logger.info("Orchestrator demo complete. Plan ready for delegation to gpt-5.4-mini.")

    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        raise


if __name__ == "__main__":
    main()

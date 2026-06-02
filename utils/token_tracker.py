"""
Token usage and cost tracking utility for Azure OpenAI API calls.

Logs token consumption and estimates sandbox costs based on model pricing.
Integrates with standard Python logging for monitoring and billing.
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Pricing in USD per 1K tokens (sandbox/demonstration rates)
COST_RATES = {
    "gpt-5.4": {"prompt": 0.01, "completion": 0.03},
    "gpt-5-mini": {"prompt": 0.001, "completion": 0.002},
    "gpt-5-nano": {"prompt": 0.0005, "completion": 0.001},
    "gpt-5.2": {"prompt": 0.001, "completion": 0.002},
    "text-embedding-3-large": {"prompt": 0.00013, "completion": 0.0}
}


def log_token_usage(model_name: str, usage_object) -> None:
    """
    Log token usage and estimated cost for an API call.

    Args:
        model_name: Model identifier (e.g., "gpt-5.4", "text-embedding-3-large")
        usage_object: OpenAI usage object with prompt_tokens, completion_tokens, total_tokens

    Returns:
        None (logs to stdout via logging)
    """
    if not usage_object:
        logger.warning("No usage object provided, skipping token logging")
        return

    try:
        prompt_tokens = getattr(usage_object, 'prompt_tokens', 0) or 0
        completion_tokens = getattr(usage_object, 'completion_tokens', 0) or 0
        total_tokens = getattr(usage_object, 'total_tokens', 0) or 0

        rates = COST_RATES.get(model_name, {"prompt": 0.0, "completion": 0.0})

        prompt_cost = (prompt_tokens / 1000.0) * rates["prompt"]
        completion_cost = (completion_tokens / 1000.0) * rates["completion"]
        total_cost = prompt_cost + completion_cost

        logger.info(
            f"Model: {model_name} | "
            f"Tokens: {prompt_tokens}+{completion_tokens}={total_tokens} | "
            f"Est. Sandbox Cost: ${total_cost:.6f}"
        )
    except Exception as e:
        logger.error(f"Error logging token usage: {e}")

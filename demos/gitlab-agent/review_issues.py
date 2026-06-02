"""
GitLab API integration demo: fetch project issues and summarize with gpt-5-mini.

Demonstrates enterprise API integration for issue triage and summarization workflows.
Requires authentication via GitLab PAT and project configuration.

Env vars:
  GITLAB_PAT: GitLab Personal Access Token (read_api scope minimum)
  GITLAB_PROJECT_ID: Numeric GitLab project ID
  GITLAB_API_URL: GitLab API base URL (e.g., https://gitlab.com/api/v4)
  AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
"""

import logging
import os

import httpx
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAIError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_gitlab_config() -> tuple[str, str, str] | None:
    """Load GitLab config from environment variables."""
    pat = os.getenv("GITLAB_PAT")
    project_id = os.getenv("GITLAB_PROJECT_ID")
    api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")

    if not pat or not project_id:
        logger.error("Missing GitLab config: GITLAB_PAT and GITLAB_PROJECT_ID required")
        return None

    logger.info(f"GitLab config loaded (project={project_id}, api={api_url})")
    return pat, project_id, api_url


def get_azure_client() -> AzureOpenAI | None:
    """Initialize Azure OpenAI client."""
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
        logger.error(f"Failed to initialize Azure OpenAI: {e}")
        return None


def fetch_issues(pat: str, project_id: str, api_url: str, page: int = 1) -> list[dict]:
    """Fetch issues from GitLab project with pagination support."""
    headers = {"PRIVATE-TOKEN": pat}
    issues_url = f"{api_url}/projects/{project_id}/issues"

    try:
        logger.info(f"Fetching issues (page={page})...")
        response = httpx.get(
            issues_url,
            headers=headers,
            params={"page": page, "per_page": 5}
        )
        response.raise_for_status()
        issues = response.json()
        logger.info(f"Retrieved {len(issues)} issues")
        return issues
    except httpx.HTTPError as e:
        logger.error(f"GitLab API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching issues: {e}")
        raise


def summarize_issues(client: AzureOpenAI, issues: list[dict]) -> str:
    """Summarize issues using gpt-5-mini."""
    if not issues:
        logger.warning("No issues to summarize")
        return "No issues found."

    issue_text = "\n\n".join([
        f"Issue #{issue['iid']}: {issue['title']}\n{issue.get('description', 'No description')}"
        for issue in issues
    ])

    try:
        logger.info(f"Summarizing {len(issues)} issues with gpt-5-mini...")
        response = client.responses.create(
            model="gpt-5-mini",
            instructions="You are a project manager. Summarize the given issues concisely.",
            input=f"Summarize these issues:\n\n{issue_text}",
        )
        summary = response.output_text
        logger.info("Issues summarized successfully")
        return summary
    except OpenAIError as e:
        logger.error(f"Summarization API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        raise


def main():
    """Run GitLab issue review demo."""
    load_dotenv()
    gitlab_config = get_gitlab_config()
    if not gitlab_config:
        logger.error("Cannot proceed without GitLab configuration.")
        return

    azure_client = get_azure_client()
    if not azure_client:
        logger.error("Cannot proceed without Azure OpenAI client.")
        return

    pat, project_id, api_url = gitlab_config

    try:
        issues = fetch_issues(pat, project_id, api_url)
        summary = summarize_issues(azure_client, issues)
        print("\nIssue Summary:")
        print("=" * 70)
        print(summary)
        print("=" * 70)
    except Exception as e:
        logger.error(f"Issue review failed: {e}")
        raise


if __name__ == "__main__":
    main()

# GitLab Agent Demo

## Goal

Demonstrates enterprise API integration: fetch GitLab project issues and summarize them using `gpt-5-mini`. Illustrates how LLMs can be embedded in DevOps workflows for issue triage.

## How to Run

```bash
uv run python demos/gitlab-agent/review_issues.py
```

## Environment Variables

- `GITLAB_PAT`: GitLab Personal Access Token (scope: `read_api` minimum)
- `GITLAB_PROJECT_ID`: Numeric GitLab project ID (e.g., `12345`)
- `GITLAB_API_URL`: GitLab API base URL (default: `https://gitlab.com/api/v4`)
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI deployment endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

## Workflow

1. **Authenticate**: Use PAT to authenticate with GitLab
2. **Fetch Issues**: Retrieve issues from specified project (paginated)
3. **Summarize**: Pass issue list to `gpt-5-mini` for summarization
4. **Output**: Print concise issue summary

## Pagination

Supports paginated retrieval via the `page` parameter. Default fetch size: 5 issues per page.

## Notes

- **Internal GitLab Only**: This demo assumes access to a GitLab instance (GitLab.com or self-hosted)
- **Token Security**: Never commit PAT to version control; use environment variables or secret management

# Demo: GitLab Issue Summarizer

Integrate with **internal GitLab APIs** to read issues, summarize them, and categorize by priority. This demonstrates real-world API integration with model routing.

## What It Does

This demo:
1. Authenticates with GitLab via PAT
2. Fetches open issues from your project
3. Sends each issue to **gpt-5-mini** (Code agent) for summarization and priority tagging
4. Groups issues by priority (Critical, High, Medium, Low)
5. Outputs a **summary report** you can share with the team

### Example Report Output

```
# GitLab Issue Summary Report
Generated: 2026-05-31

## Critical (2 issues)
1. **Login API returns 500 on invalid tokens** [#342]
   Summary: Authentication endpoint fails gracefully...
   
2. **Database connection pool exhausted in prod** [#339]
   Summary: High-load scenarios drain connection pool...

## High (5 issues)
... (grouped similarly)

## Medium (8 issues)
... (grouped similarly)

## Low (3 issues)
... (grouped similarly)
```

## Goal

Learn:
- How to authenticate with GitLab API using a Personal Access Token
- When to use a fast summarization model (gpt-5-nano or gpt-5-mini)
- How to batch API requests efficiently
- Organizing agent output into actionable reports

## Environment Variables

Before running, ensure your `.env` has:

| Variable | Value |
|----------|-------|
| `GITLAB_PAT` | Your GitLab Personal Access Token (scope: `api`, `read_api`) |
| `GITLAB_PROJECT_ID` | Your target project's numeric ID (e.g., `12345`) |
| `GITLAB_API_URL` | Your internal GitLab API base (e.g., `https://<your-internal-gitlab>/api/v4`) |

### Getting a GitLab PAT

1. Log into your internal GitLab
2. Go to *Profile → Access Tokens* (or Settings → Tokens)
3. Create a new token with scopes: `api`, `read_api`
4. Copy and paste into `.env`

## How to Run

```bash
uv run python demos/gitlab-agent/review_issues.py
```

The script will:
1. Authenticate using `GITLAB_PAT`
2. Fetch all open issues in project `GITLAB_PROJECT_ID`
3. Send each to the Code agent (gpt-5-mini) for summarization (in parallel batches)
4. Print a summary report to the console

### Sample Execution

```bash
$ uv run python demos/gitlab-agent/main.py

Fetching issues from <your-internal-gitlab>/api/v4/projects/12345...
✓ Found 18 open issues
Summarizing issues (batch 1/3)...
✓ Processed 6 issues
Summarizing issues (batch 2/3)...
✓ Processed 6 issues
Summarizing issues (batch 3/3)...
✓ Processed 6 issues

Report saved to: output_gitlab_summary.md
Total cost: ~1 credit (gpt-5-mini, parallelized)
```

## Code Structure

```
demos/gitlab-agent/
├── review_issues.py         # Entry point: fetch + summarize
└── README.md                # Walkthrough
```

## The Routing Lesson

This demo shows **why gpt-5-nano or gpt-5-mini is perfect for summarization**:

- You need to classify many issues quickly (18 issues, ~1 second each)
- Reasoning is not needed (no decomposition or complex logic)
- Cost savings are dramatic: gpt-5.4 would cost 50× more and add 30s latency

**Avoid:** Using the Plan agent (gpt-5.4) to summarize all issues (expensive, slow).
**Prefer:** Code agent (gpt-5-mini) in parallel batches (fast, cheap, same quality).

## Network Isolation

Remember: your DevPod can **only** reach internal GitLab and your whitelisted Azure endpoint. You cannot fetch from public GitHub or other external APIs. This demo works entirely within the private network.

## Extending This Demo

To extend the demo:

1. Edit `demos/gitlab-agent/review_issues.py` to add filtering or grouping
2. Extend the summarization prompt in the system prompt
3. Re-run the demo with your changes

---

Next: [RAG with Embeddings](rag-embeddings.md) to see semantic search in action.

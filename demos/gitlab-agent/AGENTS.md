<!-- FOR AI AGENTS. Scoped to demos/gitlab-agent/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — gitlab-agent demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
Enterprise API integration: authenticate to GitLab with a PAT, fetch a project's issues over
`httpx`, and summarize them with `gpt-5.4-mini`. Demonstrates embedding an LLM into a real DevOps
workflow (issue triage) — and that the LLM is used *only* for the summarization judgment call.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `review_issues.py` | Entry point. `get_gitlab_config` + `get_azure_client` → `fetch_issues` (httpx) → `summarize_issues` (`gpt-5.4-mini`) |
| `README.md` | Human-facing walkthrough |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command |
|------|---------|
| Fetch + summarize issues | `uv run python demos/gitlab-agent/review_issues.py` |

Required env vars (from `.env`):
- `GITLAB_PAT` — PAT, `read_api` scope minimum
- `GITLAB_PROJECT_ID` — numeric project ID
- `GITLAB_API_URL` — defaults to `https://gitlab.com/api/v4`
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Job | Role / model | Why |
|-----|--------------|-----|
| Fetch issues (HTTP) | *no model* — plain `httpx` | A status code already answers it; deterministic work stays in code |
| Summarize the issue list | `everyday-dev` → `gpt-5.4-mini` | Summarization is the genuine judgment call — the workhorse is the right fit |

Do **not** route summarization to `gpt-5.4`: there is no multi-step reasoning here. If you only need
one-line classification of each issue, `gpt-5.4-nano` (`summarizer` role) is cheaper still.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.10+, PEP 8, type hints (`-> list[dict]`, `-> tuple[str, str, str] | None`).
- `httpx` with `raise_for_status()`; catch `httpx.HTTPError` explicitly.
- Pagination via `page` / `per_page` params (default 5 per page).
<!-- AGENTS-GENERATED:END code-style -->

## Security & boundaries (delta from root)
- **Never** commit or log the PAT — read it from `.env` only; it is never printed.
- **Never** reach a GitLab host outside the Playbox-approved internal instance (the public
  `gitlab.com` default is illustrative; the live demo points at internal GitLab).
- **Ask first** before widening the PAT scope beyond `read_api` — this demo never writes.

## When stuck
- `401/403` → PAT scope or `GITLAB_PROJECT_ID`. `404` → wrong `GITLAB_API_URL`.
- Root conventions: repo-root `AGENTS.md`. Role + limits: `.kilo/agents/everyday-dev.md`, `.kilo/kilo.jsonc`.

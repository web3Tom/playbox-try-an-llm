# Environment Setup

The Polestar Playbox runs inside **DevPod**, a containerized development environment accessible via browser-based VSCode. This section covers bootstrap, environment variables, and the Kilo Code agent setup.

## Network Isolation

Your DevPod workspace is network-restricted:
- ✅ **Reachable:** Internal GitLab APIs, whitelisted Azure OpenAI endpoints (via your assigned DevPod container)
- ❌ **Not reachable:** Public internet (GitHub, PyPI, npm registries, external APIs)

All model requests route through your organization's **Azure OpenAI Private Endpoint** (`https://<your-playbox-apim-endpoint>/...`).

## Bootstrap Flow

When you start a new DevPod workspace:

1. **DevPod container launches** — based on `.devpod/Dockerfile`
2. **Kilo Code is auto-installed** — via `.devpod/install-kilo-code.sh` on workspace start
3. **`scripts/init.sh` runs** (manual or on first login):
   - Copies `.env.example` → `.env` in your workspace root
   - Creates a `sandbox/<username>-<timestamp>` branch off `main`
   - You work in isolation without affecting others
4. **Install Python dependencies** — `uv sync`
5. **Ready to run** — demos and agents are available

## Environment Variables

Configure these in `.env` (created by `scripts/init.sh`):

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your org's Azure OpenAI Private Endpoint | `https://<your-playbox-apim-endpoint>/` |
| `AZURE_OPENAI_API_KEY` | Authentication token for the endpoint | `your-api-key-here` |
| `GITLAB_PAT` | Personal Access Token for GitLab API reads | `glpat-your-pat-here` |
| `GITLAB_PROJECT_ID` | Your target GitLab project numeric ID | `12345` |
| `GITLAB_API_URL` | Internal GitLab API base URL | `https://<your-internal-gitlab>/api/v4` |

### Generating Credentials

- **AZURE_OPENAI_API_KEY**: Request from your cloud platform team (Azure IAM)
- **GITLAB_PAT**: In GitLab, go to *Profile → Access Tokens* → create `api` scope token
- **GITLAB_PROJECT_ID**: Found in your project's settings (numeric, not slug)

## Installing Dependencies

Once `.env` is configured:

```bash
uv sync
```

This installs all Python dependencies pinned in `pyproject.toml`, including:
- LangChain / LangGraph for agent orchestration
- Pydantic for schema validation
- Streamlit for the PM UI demo
- ChromaDB for in-memory RAG
- And others (see `pyproject.toml`)

## Kilo Code Agent

**Kilo Code** is automatically installed in your DevPod workspace and is the primary AI agent for this Playbox.

### What Is Kilo Code?

Kilo Code is an agent that:
- Lives in your VSCode editor (browser-based in DevPod)
- Reads `.kilo/` configuration (agent roles, rules, skills)
- Invokes models via your Azure OpenAI endpoint with intelligent routing
- Executes shell commands and writes code with your approval

### Invoking Kilo Code

In VSCode:
1. Open the Kilo Code panel (sidebar icon or `Ctrl+Shift+K`)
2. Type your task or question
3. Kilo Code reads your agent role from `.kilo/agents/<role>.md` and routes to the appropriate model
4. Review and approve any edits or shell commands before they execute

### Configuration Location

All Kilo Code configuration is in `.kilo/`:

```
.kilo/
├── agents/               # Role definitions (each pins one model)
│   ├── orchestrator.md
│   ├── developer.md
│   ├── react-frontend.md
│   └── ...
├── rules/                # Global, always-on rules
├── skills/               # Reusable task patterns
├── commands/             # Custom CLI extensions
└── kilo.jsonc            # Provider config (Azure OpenAI endpoints)
```

### Alternative Agents

While Kilo Code is the scaffolded primary, **Cline** and **Codex** are supported alternatives in the Playbox if your team prefers them. Note that each extension reads its own configuration directory — only `.kilo/` is scaffolded here, so Cline/Codex users would need to port the role and routing config to that extension's format. Kilo Code is the recommended interface.

## Verification Checklist

After setup, verify everything works:

- [ ] DevPod workspace is running and VSCode is accessible
- [ ] `echo $AZURE_OPENAI_ENDPOINT` returns your endpoint URL
- [ ] `uv sync` completed without errors
- [ ] Kilo Code panel opens in VSCode
- [ ] You can run `uv run streamlit run demos/pm-ui/run_ui_playground.py` (see [PM UI Demo](../demos/pm-ui.md))

---

Next: [Agents as Code](agents.md) to understand how role definitions and model routing work.

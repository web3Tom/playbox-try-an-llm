# Polestar Playbox — Try an LLM

The canonical **"Try an LLM"** starter template for the **Polestar Playbox**, our internal,
network-restricted enterprise AI sandbox. Launch it in a DevPod (browser VSCode) from GitLab
and you have a working, opinionated starting point instead of a blank chat box.

It is built for two audiences:

- **Product Managers** — a local chat UI and a copy-paste prompt library, no IDE knowledge required.
- **Developers** — executable demos showing agent configuration, model routing, and how to bridge
  the sandbox to real infrastructure (GitLab API, RAG, orchestration).

## What it teaches

1. **Agent Configuration as Code (`.kilo/`)** — rules, roles, and skills live in a
   version-controlled directory, not in throwaway web chats.
2. **Task-specific model routing** — *the point of this template*. Match the model to the job;
   never default everything to `gpt-5.4`. See `docs/models.md` and `docs/adr/ADR-0001.md`.
3. **Show, don't tell** — every concept ships as a runnable demo under `demos/`.

> **Kilo Code** is the only agent configuration scaffolded here. Cline and Codex are supported
> alternatives in the Playbox, but this template targets `.kilo/`.

## Quick start

```bash
bash scripts/init.sh                 # copies .env.example -> .env, moves you off main, runs uv sync
# fill in .env with your Playbox endpoint + tokens
uv run streamlit run demos/pm-ui/run_ui_playground.py   # PM chat UI on port 8501
```

## Read the guide as you go

This template ships its own documentation site. **Launch it and keep it open in a browser tab
while you work through the demos** — each demo page explains the *why* behind the code you're
running, the model it routes to, and the concept it teaches.

```bash
uv run mkdocs serve            # serves the guide at http://localhost:8000
# in DevPod the port is pre-forwarded (see devfile.yaml); open the forwarded URL
```

Suggested path: **Home → Getting Started (Environment, Agents) → Models & Routing → Demos**.
PMs can jump straight to the *PM UI* demo and `PROMPTS.md`; developers should read *Models &
Routing* first, since matching the model to the job is the whole point of the template.

## The demos

Every demo runs from the repo root, reads credentials from `.env`, and has its own `README.md`
plus a matching page in the docs site. They are ordered roughly easiest → most advanced:

| Demo | What it shows | Routes to | Run it |
|------|---------------|-----------|--------|
| **pm-ui** | Non-technical Streamlit chat UI — pick a model, send a prompt, see a reply | model picker (5.4 / mini / nano / 5.2) | `uv run streamlit run demos/pm-ui/run_ui_playground.py` (port 8501) |
| **orchestrator** | The planning pattern: a reasoning model plans, then delegates code-gen down to a cheaper model | `gpt-5.4` → delegates to `gpt-5.4-mini` | `uv run python demos/orchestrator/run_orchestrator.py` |
| **gitlab-agent** | Enterprise API integration — read & summarize project issues via a GitLab PAT | `gpt-5.4-mini` | `uv run python demos/gitlab-agent/review_issues.py` |
| **rag-embeddings** | Ground answers in your own docs with an in-memory vector store (no external DB) | `text-embedding-3-large` | `uv run python demos/rag-embeddings/rag_query.py` |
| **data-analysis** | Agent-written pandas over a mock CSV; produces `output_chart.png` | `gpt-5.4` (to generate logic) | `uv run python demos/data-analysis/analyze_data.py` |
| **transcription** | Audio diarization/transcription *(endpoint not yet deployed — illustrative)* | `gpt-4o-transcribe-diarize` | `uv run python demos/transcription/transcribe.py` |
| **react-ui** | Dev-track exercise: scaffold a Vite+React app governed by a Kilo role file | `gpt-5.4-mini` (`react-frontend` role) | see `demos/react-ui/README.md` |

> Some demos call models that are **not yet deployed** (`gpt-5.4-mini`, `gpt-5.4-nano`,
> `gpt-4o-transcribe-diarize`, `text-embedding-3-large`). The scripts target the *intended* route
> to teach correct routing; until those land, use the documented fallbacks in `docs/models.md`.

## Layout

| Path | What's there |
|------|--------------|
| `.kilo/` | Kilo Code agent config — roles (`agents/`), global rules, `kilo.jsonc` model routing |
| `demos/` | Executable use cases: `pm-ui`, `orchestrator`, `gitlab-agent`, `rag-embeddings`, `data-analysis`, `transcription`, `react-ui` |
| `docs/` | MkDocs guide (PM track + dev track) and architecture decision records (`docs/adr/`) |
| `utils/` | `token_tracker.py` — per-call token/cost logging |
| `scripts/init.sh` | DevPod bootstrap |
| `PROMPTS.md` | Copy-paste prompt library for PMs |
| `AGENTS.md` | Working contract for AI agents in this repo |

## Constraints (read before running anything)

- **Network is restricted.** Only internal GitLab APIs and whitelisted Azure model endpoints
  (via the Playbox APIM gateway) are reachable. Everything else is blocked.
- **No secrets in git.** Credentials live in `.env` (gitignored); commit `.env.example` only.
- **Never push to `main`.** `scripts/init.sh` moves you to a `sandbox/<user>-<timestamp>`
  branch; integrate via merge request.

Some models (`gpt-5.4-mini`, `gpt-5.4-nano`, `gpt-4o-transcribe-diarize`, `text-embedding-3-large`)
are **not yet deployed** — the routing config falls back to deployed equivalents and notes the
substitution. See `docs/models.md`.

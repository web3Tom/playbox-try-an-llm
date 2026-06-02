<!-- FOR AI AGENTS - Human readability is a side effect, not a goal -->
<!-- Precedence: the closest AGENTS.md to the files you're changing wins. -->

# AGENTS.md

## What this repo is

The canonical **"Try an LLM"** starter template for the **Polestar Playbox** — an internal,
network-restricted enterprise AI sandbox accessed via DevPod (browser VSCode) inside GitLab.
It teaches three concepts by example: agent-configuration-as-code (`.kilo/`), task-specific
**model routing**, and show-don't-tell executable demos. Dual audience: non-technical PMs and
developers. **Kilo Code is the only agent config scaffolded;** Cline and Codex are documented
as supported alternatives only.

## Commands

> Verify before claiming any of these worked — endpoints are not live in this local mirror.

| Task | Command | ~Time |
|------|---------|-------|
| Bootstrap workspace | `bash scripts/init.sh` | ~5s |
| Install Python deps | `uv sync` | ~30s |
| Run codebase analyzer | `uv run python demos/codebase-analyzer/analyze.py` | varies |
| Run orchestrator demo | `uv run python demos/orchestrator/run_orchestrator.py` | varies |
| Run RAG demo | `uv run python demos/rag-embeddings/rag_query.py` | varies |
| React demo | `cd demos/react-ui && npm install && npm run dev` | ~30s |
| Serve docs | `uv run mkdocs serve` | ~3s |

## Response Style

- Answer first, elaborate only if needed. No sycophantic openers.
- For yes/no or status questions, lead with the answer.

## Workflow

1. **Before coding:** read this file, then the relevant `.kilo/agents/<role>.md` for the role
   you're acting as, plus `.kilo/system_prompt.md` for the global constraints.
2. **Match the model to the job** (see Heuristics) — do not default to the most powerful model.
3. **After each change:** run the smallest relevant demo/check.
4. **Before claiming done:** paste command output as evidence — never say "should work".

## File Map (on disk)

```
playbox-try-an-llm/
├── .kilo/                  -> Kilo Code agent config (the only scaffolded agent surface)
│   ├── agents/             -> per-role definitions, each pinned to a model
│   │   ├── orchestrator.md     -> gpt-5.4 (planning/delegation, reasoning)
│   │   ├── everyday-dev.md     -> gpt-5-mini (workhorse)
│   │   ├── summarizer.md       -> gpt-5-nano
│   │   └── react-frontend.md   -> gpt-5.2 (fallback gpt-5-mini)
│   ├── rules/              -> always-on global rules (general.md)
│   ├── skills/             -> deterministic tool definitions (SWE-agent / agent-skills patterns)
│   ├── commands/           -> reusable slash commands
│   ├── kilo.jsonc          -> provider/model config + per-role limits (see ADR-0001)
│   └── system_prompt.md    -> global rules + network constraints
├── demos/                  -> executable use cases (one subdir each, each with a README)
│   ├── codebase-analyzer/ -> repo→graph pipeline + React dashboard (flagship routing demo)
│   ├── orchestrator/       -> planner + sub-agent delegation
│   ├── gitlab-agent/       -> GitLab API integration via PAT
│   ├── react-ui/           -> Vite+React frontend generation (scaffold exercise)
│   ├── transcription/      -> gpt-4o-transcribe-diarize (audio / diarization)
│   └── rag-embeddings/     -> local in-memory vector search (text-embedding-3-large)
├── specs/                  -> Spec-Kit-style specs (Constitution -> Spec -> Plan -> Impl)
├── docs/                   -> MkDocs source (PM track + dev track) + adr/
├── utils/token_tracker.py  -> per-call token/cost logging
├── scripts/init.sh         -> DevPod bootstrap: copy .env.example, move off main, uv sync
├── .devpod/install-kilo-code.sh -> installs Kilo Code extension on workspace start
├── .env.example            -> endpoint URLs + PAT placeholders
├── devfile.yaml            -> DevPod spec (ports pre-forwarded for all demo services)
├── mkdocs.yml              -> MkDocs (material theme)
├── pyproject.toml          -> Python tooling, uv-managed (no requirements.txt)
├── PROMPTS.md              -> copy-paste prompt library for PMs
└── README.md
```

## Heuristics — model routing (the core lesson)

| When | Use | Note |
|------|-----|------|
| Multi-step planning / orchestration | `gpt-5.4` (reasoning) | High cost — route sparingly |
| Everyday dev / coding (workhorse) | `gpt-5-mini` | Default for routine implementation |
| UI / frontend work | `gpt-5.2` | Fallback `gpt-5-mini` for harder reasoning |
| Summarization / quick classification | `gpt-5-nano` | Lowest latency / cost |
| Audio / transcription demo | `gpt-4o-transcribe-diarize` | Specialized audio / diarization model |
| RAG / embeddings demo | `text-embedding-3-large` | Retrieval embeddings |
| Adding a dependency | Ask first — keep the template lean | — |

> Routing is the point of this template: never default to `gpt-5.4` for everything. `gpt-5.4`
> is a reasoning model — reasoning tokens share the per-request output budget, so its output
> cap is raised to 32,768 (see `docs/adr/ADR-0001.md`).

## Boundaries

### Always Do
- Work on a `sandbox/<user>-<timestamp>` branch (created by `scripts/init.sh`) — never `main`.
- Pin an explicit model in every `.kilo/agents/*.md` role file.
- Use env vars from `.env` for all Azure / GitLab auth.
- Show command output as evidence before claiming a demo works.

### Ask First
- Adding any Python or Node dependency (the template is deliberately minimal).
- Adding a new demo or model route.
- Changing `devfile.yaml` port forwarding or the DevPod bootstrap.

### Never Do
- **Access any external internet endpoint** — only internal GitLab APIs and whitelisted Azure
  model endpoints are reachable; assume anything else is blocked.
- Commit secrets, PATs, or `.env` (commit `.env.example` only).
- Push directly to `main` — open a merge request.
- Connect a demo to an external database — RAG/vector stores stay in-memory or local.
- Present an unverified command as tested.

## Terminology

| Term | Means |
|------|-------|
| Polestar Playbox | Internal network-restricted enterprise AI sandbox |
| DevPod | Browser-based VSCode workspace launched inside a GitLab project |
| APIM | Azure API Management gateway fronting the approved model endpoints |
| Kilo Code | The agent extension this template scaffolds for (`.kilo/`) |
| Model routing | Matching task complexity/latency/cost to a specific deployed model |

<!-- FOR AI AGENTS. Scoped to demos/orchestrator/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — orchestrator demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
The reference **orchestrator pattern**: a reasoning model (`gpt-5.4`) reads a spec and emits a
numbered implementation plan, which is then ready to hand off to a cheaper coding model. It exists
to demonstrate *separation of planning from implementation* — the foundation of model routing.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `run_orchestrator.py` | Entry point. `init_azure_client` → `read_spec` → `generate_plan` (calls `gpt-5.4`) → prints plan |
| `spec.md` | The software requirement the planner reads (group-names-by-letter task) |
| `README.md` | Human-facing walkthrough |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command | Env vars |
|------|---------|----------|
| Run the planner | `uv run python demos/orchestrator/run_orchestrator.py` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` |

Run from the **repo root** — `read_spec()` defaults to the path `demos/orchestrator/spec.md`.
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
This is the canonical case for the `plan` agent.

| Job | Role / model | Why |
|-----|--------------|-----|
| Read the spec, produce the plan | `plan` → `gpt-5.4` (reasoning) | Planning is the *only* job worth the reasoning premium |
| Implement from the plan | `code` → `gpt-5-mini` | Mechanical translation of an existing plan — the workhorse handles it |

The point: **don't run the whole pipeline on `gpt-5.4`.** Use it for the plan, then delegate. See
the root `AGENTS.md` Heuristics table and `.kilo/kilo.jsonc` for the Plan agent definition.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.10+, PEP 8, type hints on signatures (e.g. `-> AzureOpenAI | None`).
- One responsibility per function; log each step via the module `logger`.
- Errors are raised, not swallowed — `generate_plan` re-raises `OpenAIError`.
<!-- AGENTS-GENERATED:END code-style -->

## Boundaries (delta from root)
- **Always** keep `spec.md` the single source the planner reads — edit the spec, not the prompt, to change the task.
- **Ask first** before wiring the optional implementation step (a second model call) — keep the demo a single hop unless asked.
- **Never** hard-code the plan or the model name anywhere but the role config.

## When stuck
- Empty/blank plan output → the `gpt-5.4` output cap; reasoning tokens share the budget (see `docs/adr/ADR-0001.md`).
- Root conventions: repo-root `AGENTS.md`. Plan agent config: `.kilo/kilo.jsonc`.

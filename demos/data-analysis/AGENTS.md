<!-- FOR AI AGENTS. Scoped to demos/data-analysis/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — data-analysis demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
Reads transaction metrics with pandas, computes a 7-day rolling average, and renders a chart with
matplotlib. **This demo makes no LLM call** — it is the deliberate counter-example: deterministic
data work belongs in plain code, not a model.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `analyze_data.py` | `generate_report`: read CSV → rolling mean → save `output_chart.png` |
| `transaction_metrics.csv` | Input data (`date`, `transaction_volume_usd` columns) |
| `README.md` | Human-facing walkthrough |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command | Output |
|------|---------|--------|
| Generate the chart | `uv run python demos/data-analysis/analyze_data.py` | `output_chart.png` (written to CWD) |

No env vars, no network, no credentials. Requires `pandas` and `matplotlib`.
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Job | Role / model | Why |
|-----|--------------|-----|
| Compute rolling average + plot | *no model* — pandas/matplotlib | A rolling mean is a deterministic transform; a model would be slower, costlier, and wrong |
| Extend/refactor this script in Kilo | `everyday-dev` → `gpt-5.4-mini` | *Writing* the code is the judgment call; *running* it is not |

The lesson: **not every demo calls a model, and that is the right answer.** Use the LLM to author or
modify the analysis; never to perform the arithmetic. (Root rule: deterministic transforms stay in code.)

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- Python 3.10+, PEP 8, type hints on signatures.
- Keep matplotlib figure construction explicit (`fig, ax = plt.subplots(...)`); always `tight_layout()` before save.
- Fail loud on a missing input file (`FileNotFoundError` is re-raised).
<!-- AGENTS-GENERATED:END code-style -->

## Boundaries (delta from root)
- **Never** route the numeric computation through a model "for convenience".
- **Ask first** before adding a charting/analytics dependency beyond pandas + matplotlib.

## When stuck
- `KeyError` → the CSV must have `date` and `transaction_volume_usd` columns.
- Root conventions: repo-root `AGENTS.md`. Role + limits: `.kilo/agents/everyday-dev.md`.

# Data Analysis Demo

## Goal

Demonstrates data analysis and visualization using Pandas. Reads transaction metrics, computes rolling averages, and generates a chart suitable for PM dashboards or reports.

## How to Run

```bash
uv run python demos/data-analysis/analyze_data.py
```

## Output

Generates `output_chart.png` showing:
- Daily transaction volume
- 7-day rolling average for trend identification

## Dependencies

- `pandas` — data manipulation
- `matplotlib` — visualization

## Integration with Kilo Code

This script can be executed by Kilo Code as part of larger analysis workflows, or invoked directly for standalone reporting.

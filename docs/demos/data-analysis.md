# Demo: Data Analysis

Generate **Python analysis code** from a natural-language request, execute it on a mock CSV dataset, and produce charts.

## What It Does

This demo:
1. Takes a natural-language request (e.g., "Analyze sales trends by region")
2. Uses **gpt-5.2** to generate Pandas analysis code
3. Executes the code in a sandboxed environment
4. Generates charts (Matplotlib/Seaborn) and saves them as PNG
5. Returns insights and visualizations

### Example

**Request:** "Show me the top 5 regions by revenue and create a bar chart."

**Generated Code (by gpt-5.2):**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/sales.csv')
top_regions = df.groupby('region')['revenue'].sum().nlargest(5)
top_regions.plot(kind='bar', figsize=(10, 6))
plt.title('Top 5 Regions by Revenue')
plt.xlabel('Region')
plt.ylabel('Revenue ($)')
plt.savefig('output_chart.png', dpi=300, bbox_inches='tight')
print(f"Chart saved. Top region: {top_regions.index[0]} (${top_regions.iloc[0]:,.0f})")
```

**Output:**
```
Chart saved. Top region: North America ($2.1M)
```

And a PNG file: `output_chart.png`

## Goal

Learn:
- How LLMs can generate executable code from natural language
- Safe code execution patterns (sandboxing, allowlists)
- Visualization best practices
- When to use gpt-5.2 (coding) vs gpt-5.4-mini (quick fixes) for analysis tasks

## How to Run

```bash
uv run python demos/data-analysis/main.py
```

Interactive mode:
```bash
$ uv run python demos/data-analysis/main.py --interactive

Loading sample dataset (data/sales.csv)...
✓ Loaded 1000 rows, 5 columns

Describe what you want to analyze:
> Top 5 regions by revenue with a bar chart

Generating analysis code with gpt-5.2...
✓ Code generated
Running analysis...
✓ Execution successful
✓ Chart saved to output_chart.png

Summary:
North America: $2,100,000 (36% of total)
Europe: $1,850,000 (31%)
...
```

Batch mode (predefined analyses):
```bash
uv run python demos/data-analysis/main.py --batch
```

## Code Structure

```
demos/data-analysis/
├── main.py                  # Entry point
├── data_analyzer.py         # gpt-5.2 code generation
├── executor.py              # Safe code execution sandbox
├── visualizer.py            # Chart rendering (Matplotlib/Seaborn)
├── data/
│   └── sales.csv            # Mock dataset
└── sample_analyses.txt      # Example requests
```

## Safe Code Execution

The executor uses several safety measures:

1. **Allowlist imports:** Only trusted libraries (pandas, numpy, matplotlib)
2. **Timeout:** Code execution is capped at 30 seconds
3. **Isolation:** Runs in a subprocess with restricted file access
4. **Output capture:** Chart files are written to a designated output directory

```python
# In executor.py
ALLOWED_IMPORTS = {'pandas', 'numpy', 'matplotlib', 'seaborn', 'datetime'}

def execute(code: str) -> dict:
    # Validate imports
    if has_unsafe_imports(code):
        raise ValueError("Unsafe import detected")
    
    # Run with timeout
    try:
        result = run_in_subprocess(code, timeout=30)
    except TimeoutError:
        raise ValueError("Execution timeout (30s exceeded)")
    
    return result
```

## The Routing Lesson

For data analysis, **gpt-5.2 is the right choice**:

- Reasoning is not needed (code generation is deterministic)
- Speed matters (users expect quick results)
- Cost is moderate (synthesis of structured output)

**Avoid:** gpt-5.4 for routine data analysis (expensive reasoning for non-reasoning tasks).
**Avoid:** gpt-5-mini (sometimes too fast, may miss edge cases).
**Prefer:** gpt-5.2 (balanced speed, strong code quality).

## Extending This Demo

### Add Your Own Dataset

Replace `data/sales.csv` with your own CSV:

```bash
cp your-dataset.csv demos/data-analysis/data/sales.csv
uv run python demos/data-analysis/main.py --interactive
```

The system will auto-detect the schema and adapt.

### Add Visualization Types

Extend `visualizer.py` to support additional charts:

```python
chart_types = {
    'bar': lambda data: data.plot(kind='bar'),
    'line': lambda data: data.plot(kind='line'),
    'scatter': lambda data: data.plot(kind='scatter'),
    'heatmap': lambda data: sns.heatmap(data),
    # Add more as needed
}
```

### Statistical Analysis

Have gpt-5.2 generate correlation matrices, hypothesis tests, or regression models:

```
Request: "Find the correlation between spend and region, and test if it's significant."

Generated Output:
- Correlation matrix
- P-values
- Visualization (heatmap)
```

---

Next: [Audio Transcription](transcription.md) to see multimodal model capabilities.

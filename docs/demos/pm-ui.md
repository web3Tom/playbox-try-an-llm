# Demo: PM UI Playground

A **non-technical chat interface** for product managers, marketers, and executives to experiment with LLMs without touching code.

## What It Does

The PM UI is a Streamlit application that:
- Provides a simple chat window
- Exposes multiple models side-by-side (gpt-5.4, gpt-5.2, gpt-4o, etc.)
- Links to the **PROMPTS library** — curated examples for each model
- Shows model behavior and cost differences in real time
- Requires **no coding or terminal knowledge**

## Goal

Let non-technical stakeholders:
1. Directly experience the difference between reasoning models (gpt-5.4) and fast models (gpt-5.4-mini)
2. Explore the PROMPTS library to understand how to write effective AI requests
3. Justify model routing decisions with live examples ("Why we don't use gpt-5.4 for summaries")

## How to Run

In your DevPod terminal:

```bash
uv run streamlit run demos/pm-ui/run_ui_playground.py
```

The app starts on **http://localhost:8501** (DevPod forwards the port automatically).

### Inside the UI

1. Select a model from the dropdown (default: gpt-5.4)
2. Type a task or question in the chat box
3. Click **Send** or press `Enter`
4. View the response, cost, and reasoning tokens (if applicable)
5. Click **Show PROMPTS** to see curated examples for this model
6. Switch models and compare results side-by-side

## Models Available

| Model | In UI | Use Case |
|-------|-------|----------|
| gpt-5.4 | Yes | Planning, reasoning, high-stakes decisions |
| gpt-5.2 | Yes | Balanced coding and analysis |
| gpt-5.4-mini | Yes | Fast implementation, fallback if not deployed |
| gpt-4o | Yes | Multimodal (images, text) |
| gpt-4o-mini | Yes | Quick image analysis |

## PROMPTS Library

The PROMPTS feature links to `.kilo/skills/pm-ui-prompts.md`, which contains:
- **System prompts** for each model (e.g., "You are a planning expert")
- **Example questions** for common tasks
- **Expected response patterns** (what good output looks like)
- **Cost estimates** for typical requests

Selecting a prompt pre-fills the chat input, teaching best practices for each model.

## Technical Notes

- **Backend:** FastAPI (defined in `demos/pm-ui/app.py`)
- **Frontend:** Streamlit (defined in `demos/pm-ui/run_ui_playground.py`)
- **Auth:** Uses `${AZURE_OPENAI_API_KEY}` from your `.env`
- **Network:** Requests route through `${AZURE_OPENAI_ENDPOINT}`

## Example Session

**PM:** "I want to understand why we should use different models."

1. **Model:** gpt-5.4, **Task:** "Explain the business case for reasoning models"
   - **Result:** Long, detailed breakdown; reasoning tokens visible
   - **Cost:** ~2 credits (assuming your cost model)

2. **Model:** gpt-5.4-mini, **Task:** "Explain the business case for reasoning models"
   - **Result:** Shorter but complete; reasoning tokens: 0
   - **Cost:** ~0.1 credits

3. **Takeaway:** "For a PM-facing summary, gpt-5.4-mini is 20× cheaper and fast enough."

---

Next: [Orchestrator Demo](orchestrator.md) to see agents planning and delegating.

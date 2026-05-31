# Polestar Playbox — Chat Interface

## Goal

Provides a non-technical entry point for product managers to explore different GPT-5 series models via an interactive Streamlit chat interface. No code execution required — just select a model and chat.

## How to Run

```bash
uv run streamlit run demos/pm-ui/run_ui_playground.py
```

The app runs on **port 8501** by default:
```
http://localhost:8501
```

## Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI deployment endpoint (e.g., `https://<your-org>.openai.azure.com/`)
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

If either variable is missing, the UI displays a warning and does not crash.

## Model Selection

Choose from:
- `gpt-5.4` — Full reasoning model (planning, orchestration)
- `gpt-5.4-mini` — Lightweight reasoning (everyday-dev workhorse)
- `gpt-5.4-nano` — Ultra-lightweight (summarization, quick classification)
- `gpt-5.2` — Standard model (UI/frontend work, general tasks)

## Conversation History

Chat messages are stored in Streamlit session state. Refresh the page or restart the app to clear history.

# React UI Demo (Scaffold)

## Goal

Template for a Vite+React frontend that integrates with the Polestar Playbox backend services. This directory is a placeholder for frontend development using modern tooling.

## Setup

Scaffold a new Vite+React app:

```bash
npm create vite@latest . -- --template react
npm install
npm run dev
```

Runs on `http://localhost:5173` by default.

## Development

The `.kilo/agents/react-frontend.md` role governs frontend development patterns and conventions for this project.

## Integration

The React app can call backend demos via:
- Chat UI → `demos/pm-ui/run_ui_playground.py` (Streamlit)
- Data visualization → `demos/data-analysis/analyze_data.py`
- RAG queries → `demos/rag-embeddings/rag_query.py`

## Notes

- Use `npm run build` for production bundling
- Environment variables for API endpoints go in `.env.local`
- No code yet — this is a development track exercise

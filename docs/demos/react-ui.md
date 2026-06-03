# Demo: React UI Generation

A small, **runnable Vite + React app** that doubles as the frontend-generation playground. It's
governed by the Kilo Code `react-frontend` role (`gpt-5.2`, variant: high) — the place
to practice driving a UI specialist agent against a real codebase.

## What It Does

The app (in `demos/react-ui/`) renders:

1. A header — **"Polestar Playbox — Model Router"**.
2. A **dark / light theme toggle** — `useState` + `useEffect`, persisted to `localStorage`,
   honouring the system preference on first load.
3. A **model-routing reference card** — a table of the routing rules, rendered from a static
   data module (`src/data/models.js`), so you can see the routing lesson in the UI itself.

It is intentionally small and self-contained: no network calls, no external dependencies beyond
React and Vite. The point is to give the `react-frontend` agent a real, running app to extend.

## How to Run

```bash
cd demos/react-ui
npm install
npm run dev
```

Visit `http://localhost:5173` (the port is pre-forwarded in `devfile.yaml`).

## Structure

```
demos/react-ui/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx                 # React 18 entry point
    ├── App.jsx                  # Header + ThemeToggle + RoutingTable + footer
    ├── index.css                # Light/dark CSS variables, table styling
    ├── components/
    │   ├── ThemeToggle.jsx       # Dark/light toggle, localStorage-persisted
    │   └── RoutingTable.jsx      # Renders the static routing rules
    └── data/
        └── models.js            # The routing rules (static, illustrative)
```

## The Agent: `.kilo/agents/react-frontend.md`

This role is pinned to `gpt-5.2`, with `variant: high` for complex logic. It owns frontend work in `demos/react-ui/`. To extend the app, invoke it in Kilo Code:

```
@react-frontend Add a third panel to the app that shows a bar chart of relative model cost,
using the data in src/data/models.js. Keep it consistent with the existing theme variables.
```

Kilo Code reads `.kilo/agents/react-frontend.md`, loads the global rules, and routes the work to
`gpt-5.2`. For particularly complex logic, escalate to the Plan agent (gpt-5.4).

## The Routing Lesson

Routine UI work — components, styling, wiring hooks — is a great fit for `gpt-5.2`. It's capable
and cheaper than the Plan agent, with `variant: high` for complex logic. You would **not** route this to `gpt-5.4` by default: spending reasoning
tokens on a theme toggle is exactly the waste this template teaches you to avoid. Escalate only
when genuinely needed.

---

## Next Steps

You've now seen all six demos:

1. **Codebase Analyzer** — multi-stage repo analysis + graph dashboard
2. **Orchestrator** — reasoning + delegation
3. **GitLab Agent** — API integration + summarization
4. **RAG** — semantic search + synthesis
5. **Transcription** — multimodal audio processing
6. **React UI** — a runnable frontend to extend with the `react-frontend` role

Each emphasizes **task-specific model routing**. Return to [Models & Routing](../models.md) to
review the decision matrix, or explore [Agents as Code](../getting-started/agents.md).

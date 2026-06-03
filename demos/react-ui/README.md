# Polestar Playbox — Model Router

## Overview

A minimalist React + Vite frontend demo showcasing the **Polestar Playbox model routing reference**. This app demonstrates basic React patterns (hooks, state, side effects, component composition) and is governed by the **Kilo Code `react-frontend` role** (gpt-5.2, variant: high for complex logic).

**Goal:** Serve as a working template for rapid frontend iteration in the Polestar enterprise agentic automation reference.

## Features

- **Dark/Light Mode Toggle** — Persists theme preference to localStorage; responds to system preference on first load.
- **Static Model Routing Table** — Reference card of AI model assignments by task type.
- **Responsive Design** — Clean CSS with CSS variables for theming; mobile-friendly layout.
- **No External Dependencies** — Entirely self-contained; no network calls, no external API dependencies.

## Run Locally

### Install dependencies
```bash
cd demos/react-ui
npm install
```

### Start dev server
```bash
npm run dev
```

Server opens at **http://localhost:5173**. Hot Module Replacement (HMR) enabled.

### Build for production
```bash
npm run build
```

Output in `dist/`. Preview with `npm run preview`.

## Architecture

**File structure:**
```
demos/react-ui/
├── package.json           # Dependencies, scripts
├── vite.config.js         # Vite config (port 5173, React plugin)
├── index.html             # Root HTML template
├── src/
│   ├── main.jsx           # React 18 entry point
│   ├── App.jsx            # Root component (layout, composition)
│   ├── index.css          # Global styles, CSS variables
│   ├── components/
│   │   ├── ThemeToggle.jsx # Dark/light toggle with localStorage
│   │   └── RoutingTable.jsx # Static routing reference table
│   └── data/
│       └── models.js      # Hardcoded routing rules
└── README.md              # This file
```

**Component hierarchy:**
- `App` (layout + composition)
  - `ThemeToggle` (header button, localStorage sync)
  - `RoutingTable` (table rendering static data from models.js)

**Key patterns:**
- **useState** for theme state.
- **useEffect** for localStorage read on mount, system preference fallback.
- **CSS variables** (`--color-bg`, `--color-text`, etc.) toggled by `[data-theme]` attribute on `<html>`.
- **Immutable props** to child components; no prop drilling.

## Extend It

To add features (e.g., filter by task, copy model name, add description popovers):

1. Invoke the **Kilo Code `react-frontend` role** (gpt-5.2, variant: high).
2. Describe the new feature in natural language.
3. The role generates or modifies components; you review & iterate.
4. For complex logic, escalate to the Plan agent (gpt-5.4).

**Example prompt:**
> Add a search filter to the routing table so users can filter by task name. Debounce the input and highlight matches in the task column.

## Technologies

- **React 18.3.1** — UI library.
- **Vite 5.4.0** — Lightning-fast dev server & build.
- **JavaScript (ES Modules)** — No TypeScript. Plain, readable code.

## Notes

- No external UI framework (Bootstrap, Tailwind, etc.). Hand-written CSS using CSS variables.
- No environment variables or secrets. Entirely static.
- Pre-configured for port 5173 (mapped in parent DevPod devfile.yaml).
- All model names in the routing table are for reference only; actual deployment status is outside scope.

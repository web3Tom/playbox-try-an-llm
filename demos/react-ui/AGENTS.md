<!-- FOR AI AGENTS. Scoped to demos/react-ui/ — the closest AGENTS.md wins. -->
<!-- Generated with the agent-rules skill (scoped). Edit content, not structure. -->

# AGENTS.md — react-ui demo

<!-- AGENTS-GENERATED:START overview -->
## Overview
A small, runnable **Vite + React 18** app (theme toggle + static model-routing reference card). It
is the live playground for the `react-frontend` role — a real, running UI to extend rather than a
blank canvas. Plain JavaScript (no TypeScript), hand-written CSS, zero network calls.
<!-- AGENTS-GENERATED:END overview -->

<!-- AGENTS-GENERATED:START filemap -->
## Key Files
| File | Purpose |
|------|---------|
| `package.json` | Deps (react 18.3, vite 5.4) + scripts (`dev`/`build`/`preview`) |
| `vite.config.js` | Vite + React plugin; dev server on port 5173 |
| `index.html` | Root template, mounts `#root` |
| `src/main.jsx` | React 18 `createRoot` entry (StrictMode) |
| `src/App.jsx` | Layout: header + `ThemeToggle` + `RoutingTable` + footer |
| `src/components/ThemeToggle.jsx` | Dark/light toggle; `localStorage` + `prefers-color-scheme` |
| `src/components/RoutingTable.jsx` | Renders the routing rows from `data/models.js` |
| `src/data/models.js` | Static routing rules (source of truth for the table) |
| `src/index.css` | CSS variables themed by `[data-theme]` on `<html>` |
<!-- AGENTS-GENERATED:END filemap -->

<!-- AGENTS-GENERATED:START commands -->
## Run it
| Task | Command |
|------|---------|
| Install deps | `cd demos/react-ui && npm install` |
| Dev server (HMR) | `npm run dev` → http://localhost:5173 (pre-forwarded in `devfile.yaml`) |
| Production build | `npm run build` → `dist/`, preview with `npm run preview` |

No env vars, no secrets — entirely static.
<!-- AGENTS-GENERATED:END commands -->

## Routing lesson (why this demo exists)
| Job | Role / model | Why |
|-----|--------------|-----|
| Build/extend components, styling, hooks | `react-frontend` → `gpt-5.2` | Capable and cheaper than the orchestrator for routine UI |
| Trickier component logic | fallback → `gpt-5-mini` | Deliberate escalation when reasoning is needed |

The lesson: **do not route a theme toggle to `gpt-5.4`.** Spending reasoning tokens on routine UI is
exactly the waste this template teaches against. Invoke the role with `@react-frontend …`; Kilo reads
`.kilo/agents/react-frontend.md`, loads the global rules, and routes to `gpt-5.2`.

<!-- AGENTS-GENERATED:START code-style -->
## Code style
- **JavaScript + JSX only — no TypeScript.** Keep it plain and readable.
- Naming: `camelCase` for variables/functions, `PascalCase` for components; one component per `.jsx` file.
- Theme via CSS variables toggled by `[data-theme]`; do **not** introduce a CSS framework (no Tailwind/Bootstrap).
- Immutable props down to children; no prop drilling, no global state library.
- Keep routing data in `src/data/models.js` — the table renders from it, so edit data there, not JSX.
<!-- AGENTS-GENERATED:END code-style -->

## Boundaries (delta from root)
- **Never** add a network call or external API dependency — this demo is deliberately self-contained.
- **Ask first** before adding any npm dependency beyond React + Vite (keep the template lean).
- **Always** keep `models.js` consistent with the root `AGENTS.md` routing table.

## When stuck
- Blank page → check the browser console; verify `#root` in `index.html` and the `main.jsx` mount.
- Root conventions: repo-root `AGENTS.md`. Role + limits: `.kilo/agents/react-frontend.md`, `.kilo/kilo.jsonc`.

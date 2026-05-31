# Demo: React UI Generation

Use **gpt-5.4-mini** to generate a React/Vite frontend scaffold from a natural-language specification. This demonstrates generative AI applied to full-stack development.

## What It Does

This demo:
1. Takes a UI specification (e.g., "Build a task management dashboard with filters and search")
2. Uses **gpt-5.4-mini** (or fallback gpt-5.2) to generate React components
3. Creates a Vite project structure with:
   - Component hierarchy
   - State management (hooks)
   - Styling (Tailwind CSS)
   - API integration stubs
4. Outputs a runnable dev server

### Example

**Specification:** "Create a user profile page with avatar, bio, follow button, and stats (posts, followers)."

**Generated React Components:**

```jsx
// src/components/UserProfile.jsx
import { useState } from 'react';

export function UserProfile({ userId }) {
  const [isFollowing, setIsFollowing] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Fetch user data (API stub)
    fetchUser(userId).then(setUser);
  }, [userId]);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex items-center gap-6">
        <img src={user.avatar} alt={user.name} className="w-24 h-24 rounded-full" />
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{user.name}</h1>
          <p className="text-gray-600">{user.bio}</p>
          <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded">
            {isFollowing ? 'Following' : 'Follow'}
          </button>
        </div>
      </div>
      {/* Stats section */}
      <div className="mt-8 grid grid-cols-3 gap-4">
        <Stat label="Posts" value={user.postCount} />
        <Stat label="Followers" value={user.followerCount} />
        <Stat label="Following" value={user.followingCount} />
      </div>
    </div>
  );
}
```

**Output:** A fully runnable Vite development server with hot reload.

## Goal

Learn:
- How to specify UI requirements in natural language
- Code generation workflows for frontend development
- Why gpt-5.4-mini is cost-effective for scaffold generation
- Integration with Vite for rapid iteration

## How to Run

### Option 1: Generate a New Project from Scratch

```bash
uv run python demos/react-ui/scaffold.py \
  --spec "Dashboard with user list, search, and detail view"
```

This creates:
```
react-scaffold-<timestamp>/
├── index.html
├── src/
│   ├── App.jsx
│   ├── components/
│   │   ├── UserList.jsx
│   │   ├── SearchBar.jsx
│   │   └── UserDetail.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

### Option 2: Use Kilo Code Directly

In VSCode Kilo Code:

```
@react-frontend Create a task management dashboard with:
- Task list with checkboxes
- Priority indicators (High, Medium, Low)
- Filter by priority
- Search by title
- Add/delete tasks
```

Kilo Code reads `.kilo/agents/react-frontend.md` and generates the same output.

### Option 3: Run the Dev Server

Once generated:

```bash
cd react-scaffold-<timestamp>
npm install
npm run dev
```

Visit `http://localhost:5173` to see the generated UI.

## Code Structure

```
demos/react-ui/
├── scaffold.py              # Main entry point
├── spec_parser.py           # Parse natural-language specification
├── code_generator.py        # gpt-5.4-mini code generation
├── project_builder.py       # Create Vite project structure
├── templates/
│   ├── package.json.template
│   ├── vite.config.template
│   └── main.jsx.template
└── examples/
    ├── dashboard_spec.txt
    ├── chat_app_spec.txt
    └── ecommerce_spec.txt
```

## The Agent: `.kilo/agents/react-frontend.md`

This role is configured specifically for frontend generation:

```markdown
# React Frontend

Model: gpt-5.4-mini

## Purpose
Generate React component scaffolds from natural-language specifications.
You excel at creating component hierarchies, hooks usage, and Tailwind styling.

## When to Use
- Creating new frontend modules
- Generating initial component structure
- Rapid prototyping of UIs

## Rules
- Use React hooks (useState, useEffect, useContext)
- Prefer functional components
- Include TypeScript JSDoc comments
- Use Tailwind CSS for styling
- Create API integration stubs (not real calls)
- Follow component composition best practices

## Skills
- skills/react-patterns.md
- skills/tailwind-guidelines.md
```

## The Routing Lesson

React scaffold generation is **perfect for gpt-5.4-mini**:

- No reasoning needed (component structure is deterministic)
- Code quality matters (but mistakes are easy to fix in dev mode)
- Speed is essential (developers want fast iteration)
- Cost is low (compared to gpt-5.4)

**Avoid:** gpt-5.4 for routine scaffold generation (wasteful reasoning tokens).
**Prefer:** gpt-5.4-mini (fast, cheap, component generation is its strength).

## Extending This Demo

### Add TypeScript Support

Update `scaffold.py` to support TypeScript:

```bash
uv run python demos/react-ui/scaffold.py \
  --spec "..." \
  --typescript
```

Generated files: `UserProfile.tsx` instead of `UserProfile.jsx`.

### Add CSS Framework Options

Support styled-components, CSS Modules, or plain CSS alongside Tailwind:

```bash
uv run python demos/react-ui/scaffold.py \
  --spec "..." \
  --css-framework styled-components
```

### Component Testing

Have gpt-5.4-mini also generate Jest tests:

```bash
uv run python demos/react-ui/scaffold.py \
  --spec "..." \
  --include-tests
```

Generates `UserProfile.test.jsx` alongside components.

### E2E Testing with Playwright

Generate Playwright specs for generated components:

```
// Generated from spec
describe('Task Dashboard', () => {
  test('Can add and filter tasks', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.fill('[data-testid="task-input"]', 'Buy milk');
    await page.click('[data-testid="add-button"]');
    await page.selectOption('[data-testid="priority-filter"]', 'high');
    // ... assertions
  });
});
```

---

## Next Steps

You've now seen all seven demos:

1. **PM UI** — non-technical experimentation
2. **Orchestrator** — reasoning + delegation
3. **GitLab Agent** — API integration + summarization
4. **RAG** — semantic search + synthesis
5. **Data Analysis** — code generation + visualization
6. **Transcription** — multimodal audio processing
7. **React UI** — frontend scaffold generation

Each emphasizes **task-specific model routing**. Return to [Models & Routing](../models.md) to review the decision matrix, or explore [Agents as Code](../getting-started/agents.md) to build your own agent patterns.

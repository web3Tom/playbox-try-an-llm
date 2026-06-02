# Agents as Code

The Playbox treats agent configuration as **declarative, version-controlled code**. Your agent behavior lives in `.kilo/`, not scattered across config files or environment variables.

## The `.kilo/` Directory Structure

```
.kilo/
├── agents/
│   ├── orchestrator.md          # Planner role (gpt-5.4)
│   ├── everyday-dev.md          # Everyday coding (gpt-5-mini)
│   ├── react-frontend.md        # React scaffold role (gpt-5.2, fallback gpt-5-mini)
│   ├── summarizer.md            # Quick classification (gpt-5-nano)
│   └── ...
├── rules/
│   ├── coding-style.md          # Global code quality rules
│   ├── git-workflow.md          # Commit message conventions
│   ├── testing.md               # Test coverage requirements
│   └── security.md              # Input validation, secret handling
├── skills/
│   ├── prompt-library.md       # Curated prompt templates (mirrors PROMPTS.md)
│   ├── gitlab-integration.md    # GitLab API patterns
│   ├── rag-retrieval.md         # RAG best practices
│   └── ...
├── commands/
│   └── (custom CLI extensions, if any)
└── kilo.jsonc
    # Provider/model endpoint config:
    # Maps "gpt-5.4" → Azure OpenAI deployment name
    # Verified against your APIM endpoint at startup
```

## Role Definitions

Each file in `.kilo/agents/` defines a role by:
1. **Setting a single model** at the top (e.g., `Model: gpt-5.4`)
2. **Listing role-specific instructions** (how this agent approaches tasks)
3. **Linking global rules** (which rules apply to this role)
4. **Indicating skill availability** (which domain skills are available)

### Example: Orchestrator Role

```markdown
# Orchestrator

Model: gpt-5.4

## Purpose
You are the orchestrator: you receive high-level requests, reason about
decomposition, and delegate subtasks to specialized agents (developer,
summarizer, etc.). You do not implement directly.

## When to Use
- Complex planning and architecture decisions
- Multi-step feature planning
- Choosing which specialist agent to invoke next

## Always-On Rules
- rules/git-workflow.md
- rules/testing.md
- rules/security.md

## Available Skills
- skills/prompt-library.md

## Cost Notes
gpt-5.4 is expensive and uses reasoning tokens. Use this role sparingly
for orchestration only. Route everyday coding to the developer role.
```

### Example: Developer Role

```markdown
# Developer

Model: gpt-5-mini

## Purpose
You implement features, write tests, fix bugs, and refactor code.
You work within the scope defined by the orchestrator's plan.

## When to Use
- Feature implementation
- Bug fixes
- Code review and refactoring
- Writing tests

## Always-On Rules
- rules/coding-style.md
- rules/git-workflow.md
- rules/testing.md
- rules/security.md

## Available Skills
- skills/prompt-library.md
```

## Global Rules

Files in `.kilo/rules/` apply to all agents by reference. These encode your org's standards:

- **coding-style.md** — immutability, file organization, error handling
- **git-workflow.md** — commit message format, feature branch workflow
- **testing.md** — coverage floor, test types (unit, integration, E2E)
- **security.md** — secret management, input validation, no hardcoded credentials

Any time an agent reads its role definition, these rules are automatically in context.

## Skills

Reusable patterns and domain knowledge live in `.kilo/skills/`. Examples:

- **prompt-library.md** — curated prompt templates (mirrors PROMPTS.md)
- **gitlab-integration.md** — best practices for PAT-based GitLab reads
- **rag-retrieval.md** — ChromaDB query patterns and embedding best practices

Skills are opt-in per role (listed in the role file), keeping context tight.

## Provider Configuration: `kilo.jsonc`

The `.kilo/kilo.jsonc` file maps logical model names to your Azure OpenAI deployment:

```jsonc
{
  "provider": "azure-openai",
  "endpoint": "${AZURE_OPENAI_ENDPOINT}",
  "apiKey": "${AZURE_OPENAI_API_KEY}",
  "deployments": {
    "gpt-5.4": "your-org-gpt-54-deployment",
    "gpt-5-mini": "your-org-gpt-5-mini-deployment",
    "gpt-5-nano": "your-org-gpt-5-nano-deployment",
    "gpt-5.2": "your-org-gpt-52-deployment",
    "gpt-4o": "your-org-gpt-4o-deployment",
    "gpt-4o-mini": "your-org-gpt-4o-mini-deployment"
  }
}
```

At startup, Kilo Code verifies that each deployment name resolves to a live endpoint. A role can
also declare a deliberate fallback — a second model to escalate to (the `react-frontend` role uses
`gpt-5.2` with a `gpt-5-mini` fallback):

```jsonc
{
  "profiles": {
    "react-frontend": {
      "model": "gpt-5.2",
      "fallback": "gpt-5-mini"
    }
  }
}
```

## Invoking Agents in Kilo Code

### From the UI

1. Open Kilo Code panel in VSCode
2. Type your task or question
3. **Select an agent role** (dropdown or inline mention)
   - E.g., `@orchestrator Plan a React component refactor`
   - E.g., `@developer Implement the dashboard fix`
4. Kilo Code reads the role file, loads global rules and skills, and routes to the pinned model
5. Review the model's response, approve code changes and commands

### From the Command Line

Some organizations expose Kilo Code via CLI:

```bash
kilo --agent orchestrator --task "Plan the data analysis pipeline"
kilo --agent developer --task "Implement the GitLab API integration"
```

(Exact CLI varies by your org's Kilo Code setup.)

## The Routing Lesson

This structure enforces a key principle: **each agent role has one model**.

Why?
- **Predictability** — you know which model will run (no surprise expensive calls)
- **Cost control** — gpt-5.4 is routed only to orchestrator; everyday work uses gpt-5-mini
- **Auditability** — commit history shows who changed which agent's model assignment
- **Testability** — you can swap a role's model (e.g., developer: gpt-5.4 → gpt-5.2) and re-run the same workflow

Never default everything to gpt-5.4. Read [Models & Routing](../models.md) for the full decision matrix.

## Extending the System

To add a new agent role:

1. Create `.kilo/agents/your-role.md` with Model, Purpose, Rules, Skills
2. Update `.kilo/kilo.jsonc` if new models are needed
3. Commit and push to your sandbox branch
4. In Kilo Code, type `@your-role your-task`

To add a new global rule or skill, follow the same pattern in `.kilo/rules/` or `.kilo/skills/`.

---

Next: [Models & Routing](../models.md) to understand the cost/capability tradeoffs driving your model choices.

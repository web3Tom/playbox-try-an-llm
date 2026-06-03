# Models & Routing

The Playbox exposes a curated suite of OpenAI models via Azure. This page covers deployment status, routing decisions, and cost/capability tradeoffs.

## Deployed Now

These models are live and ready to use:

| Model | Capability | Cost (per 1M in tokens) | Best For |
|-------|-----------|------------------------|----------|
| **gpt-5.4** | Reasoning (extended thinking) | High | Orchestration, planning, architecture |
| **gpt-5.2** | Advanced reasoning, coding | Medium-High | Feature implementation, debugging |
| **gpt-5.1** | Balanced reasoning + speed | Medium | Quick problem-solving, code review |
| **gpt-5-nano** | Fast, lightweight reasoning | Low-Medium | Summarization, classification |
| **gpt-5-mini** | Fast, compact | Low | Lightweight tasks, quick edits |
| **gpt-5** | General-purpose | Low-Medium | Conversational, exploratory work |
| **gpt-4o** | Multimodal (text, images, audio) | Medium | Chat, image analysis |
| **gpt-4o-mini** | Lightweight multimodal | Low | Quick image analysis, small tasks |

## Specialized Models

These task-specific models are also live:

| Model | Capability | Use Case |
|-------|-----------|----------|
| `gpt-5-mini` | Fast reasoning + cost savings | The default Code agent workhorse |
| `gpt-5-nano` | Ultra-fast, lowest cost | Summarization, quick classification |
| `gpt-4o-transcribe-diarize` | Audio transcription with speaker tracking | The transcription demo |
| `text-embedding-3-large` | High-dimensional embeddings | RAG with semantic search |

## Routing Decision Matrix

**Use this table to choose the right model for your task:**

| Task Type | Primary Model | Reasoning | Cost |
|-----------|---------------|-----------|------|
| **Orchestration, Planning** | gpt-5.4 (Plan agent) | Reasoning model; breaks down complex problems | High |
| **Feature Implementation** | gpt-5-mini (Code agent) | Fast coding, still strong at logic | Medium |
| **Bug Fixes, Code Review** | gpt-5.2 | Balanced speed and reasoning | Medium-High |
| **UI / Frontend Work** | gpt-5.2 (variant: high) | Component generation; escalate to Plan for complex logic | Medium |
| **Documentation** | gpt-5-mini | Fast doc updates | Low |
| **Quick Classification** | gpt-5-nano | Fast summarization, no deep reasoning needed | Low |
| **General Chat, Exploration** | gpt-5 | Conversational, exploratory | Low-Medium |
| **Images, Charts, Mockups** | gpt-4o | Sees visual context; generates designs | Medium |
| **Quick Image Checks** | gpt-4o-mini | Lightweight vision | Low |
| **Audio Transcription** | gpt-4o-transcribe-diarize | Speaker detection, timestamps | Medium |
| **RAG Document Retrieval** | text-embedding-3-large | Semantic search over stored documents | Low-Medium |

## Why gpt-5.4 is Special: Reasoning Tokens

**gpt-5.4 is a reasoning model.** It uses "extended thinking" to reason internally before responding. This costs **reasoning tokens** in addition to normal input/output tokens.

### Cost Implication

A single gpt-5.4 request might consume:
- 50,000 reasoning tokens (internal thinking)
- 1,000 input tokens
- 5,000 output tokens

All three count toward your quota. Because reasoning tokens are expensive, gpt-5.4 is **not suitable for every task**. Use it only for:
- High-stakes orchestration decisions
- Complex architectural problems
- Planning multi-step workflows

For everyday coding, summarization, and quick fixes, use gpt-5.2 or gpt-5-mini.

### Output Cap with Reasoning

When using gpt-5.4, the response output budget is raised to **32,768 tokens** (vs. the usual 4,096–8,192). This allows the reasoning process to produce longer, more thorough responses. See [ADR-0001](adr/ADR-0001.md) for the detailed design rationale.

## Real-World Routing Example

You want to build a feature: "Summarize all open GitLab issues, group by team, and suggest a priority order."

**Wrong approach:**
```
Use gpt-5.4 for everything (too expensive, overkill for summarization).
```

**Right approach:**

1. **Plan agent (gpt-5.4)** — "Plan the steps to summarize and prioritize issues"
   - Output: Breakdown of the task, team categories, prioritization criteria
   - Cost: High, but only runs once

2. **Code agent (gpt-5-mini)** — "Fetch issues from GitLab and group by team"
   - Output: Python code using the GitLab API
   - Cost: Medium, efficient implementation

3. **Summarizer agent (gpt-5-nano)** — "Summarize each issue group and extract priorities"
   - Output: Summary text, bullet-point priorities
   - Cost: Low, fast classification

**Total cost:** ~70% less than routing all to gpt-5.4, **same result**.

## Reasoning Variants

A role can specify a reasoning variant for deeper analysis when the primary model needs it.
The `react-frontend` role uses `variant: high` for complex logic, which adds extra reasoning
effort. If still insufficient, escalate to the Plan agent.

```jsonc
// In .kilo/kilo.jsonc
"react-frontend": {
  "model": "gpt-5.2",
  "variant": "high"
}
```

This is a routing choice, not a deployment workaround — every model in the suite is live.

## Checking Your Endpoint

Before you run a demo, you can verify your endpoint is reachable:

```bash
curl -H "Authorization: Bearer ${AZURE_OPENAI_API_KEY}" \
  "${AZURE_OPENAI_ENDPOINT}/openai/deployments?api-version=2024-08-01-preview"
```

This returns a list of active deployments so you can confirm the model your role pins is present.

---

**Key Takeaway:** Routing is the point. Don't use gpt-5.4 for everything. Match the model to the task, save costs, and deliver faster results. See [Agents as Code](getting-started/agents.md) to understand how roles enforce this discipline.

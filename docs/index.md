# Polestar Playbox — Try an LLM

Welcome to the internal, network-restricted enterprise AI sandbox for LLM experimentation and integration.

## What Is This?

The **Polestar Playbox** is a self-contained, DevPod-based environment where you can:
- Safely experiment with cutting-edge reasoning and coding models
- Learn how to route requests to the right model for the right task
- Execute real agent workflows: orchestration, RAG, data analysis, and more
- See AI agents as a practical engineering pattern, not a buzzword

This repo is scaffolded around **GitLab CI/CD** and **Azure OpenAI** endpoints, confined to internal network access only.

## The "Try an LLM" Learning Path

The Playbox teaches three interconnected concepts:

### 1. Agent Configuration as Code
Your agents live in `.kilo/` — role definitions, model assignments, global rules, and skills. This declarative approach means:
- Every role pins one model (e.g., `orchestrator → gpt-5.4`, `developer → gpt-5.4-mini`)
- Global rules apply consistently across all agent invocations
- You version-control your agent behavior just like code
- See [Agents as Code](getting-started/agents.md) for the structure

### 2. Task-Specific Model Routing
This is **the core lesson**. Models are tools with different cost/capability tradeoffs:
- **gpt-5.4** is a reasoning model — expensive, use it only for orchestration and planning
- **gpt-5.4-mini** / **gpt-5.2** handle everyday coding and problem-solving
- **gpt-5.4-nano** does quick summarization and classification
- **gpt-4o** handles multimodal tasks (images, audio)

Learn routing patterns in [Models & Routing](models.md); see them in action across the demos.

### 3. Show-Don't-Tell Executable Demos
Seven runnable examples cover:
- **PM UI** — non-technical chat interface with direct model exposure
- **Orchestrator** — reasoning model plans, coding model executes
- **GitLab Integration** — read and summarize issues via PAT
- **RAG + Embeddings** — retrieval-augmented generation with in-memory store
- **Data Analysis** — pandas workflows with chart output
- **Audio Transcription** — multimodal transcription and diarization
- **React UI Generation** — generative AI scaffold for frontend development

Each demo emphasizes the routing decision and demonstrates a real-world pattern.

## Dual Audience

### For Product Managers & Non-Technical Leads
Start with the **PM UI** demo to see the models in action. The PROMPTS library (inside the UI) shows how to prompt each model effectively.

### For Developers & Engineers
Jump to [Getting Started](getting-started/environment.md) to set up your environment, then explore the demos in order. The routing lessons are essential background before you use the orchestrator or extend the agent system.

## Next Steps

1. **New to the Playbox?** → Read [Environment Setup](getting-started/environment.md)
2. **Need model routing guidance?** → See [Models & Routing](models.md)
3. **Ready to run code?** → Pick a [Demo](demos/pm-ui.md) and follow along
4. **Want to extend agents?** → Understand [Agents as Code](getting-started/agents.md)

---

**Questions?** Check the [Models & Routing](models.md) section or review the [Architectural Decision Record](adr/ADR-0001.md) for reasoning behind key choices.

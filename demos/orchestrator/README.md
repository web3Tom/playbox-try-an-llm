# Orchestrator Demo

## Goal

Demonstrates the orchestrator pattern: `gpt-5.4` (reasoning model) reads a specification and produces an implementation plan, which is then ready for delegation to `gpt-5.4-mini` or a code agent.

This illustrates **model routing** where the planning and coding responsibilities are separated:
- **gpt-5.4**: Deep reasoning, architectural planning
- **gpt-5.4-mini**: Implementation from plan

## How to Run

```bash
uv run python demos/orchestrator/run_orchestrator.py
```

## What Happens

1. Reads `demos/orchestrator/spec.md` (the software requirement)
2. Sends spec to `gpt-5.4` with instructions to generate a numbered plan
3. Prints the plan
4. (Optional next step) Pass plan to gpt-5.4-mini or Kilo Code for implementation

## Model Routing

This demo illustrates the Polestar principle: **different models for different jobs**.
- Heavy reasoning → `gpt-5.4`
- Implementation from plan → `gpt-5.4-mini`
- Lightweight tasks → `gpt-5.4-nano`

## Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI deployment endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

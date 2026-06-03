# Demo: Orchestrator (Planning + Delegation)

See **task-specific model routing in action**: a reasoning model plans, a coding model executes.

## What It Does

This demo implements a classic agent pattern:

1. **Plan agent (gpt-5.4)** receives a high-level request
2. Breaks it into subtasks and decides which specialist should handle each
3. **Delegates to Code agent (gpt-5-mini)** for implementation
4. Returns the final result

### Example Flow

**Task:** "Build a function to analyze log files and return error frequencies by type."

1. **Plan agent thinks:**
   - "The user wants log parsing and aggregation."
   - "Subtask 1: Write a parser function (code agent's job)"
   - "Subtask 2: Implement error grouping (code agent's job)"
   - "Subtask 3: Return a summary (code agent's job)"

2. **Plan agent delegates to Code agent:**
   - "Write a Python function that parses syslog, groups errors by type, and returns a dict of {error_type: count}"

3. **Code agent delivers:** Working Python function with tests.

4. **Plan agent approves** and returns to the user.

**Cost breakdown:** ~1 reasoning request (expensive) + ~1 coding request (cheap) = **optimal**.

## Goal

Understand:
- How reasoning models excel at decomposition, not implementation
- Why you route sparingly to gpt-5.4 (orchestration only)
- How to structure agent workflows for cost and speed

## How to Run

```bash
uv run python demos/orchestrator/run_orchestrator.py
```

This script:
1. Defines the Plan agent (gpt-5.4) with a set of delegation rules
2. Defines the Code agent (gpt-5-mini) with implementation instructions
3. Submits a sample task from `demos/orchestrator/spec.md`
4. Prints the Plan agent's plan

### Sample Output

```
=== Plan Agent Output ===
Task: Group CSV names by first letter

Plan:
1. Read CSV file with names
2. Parse each row and extract the first character
3. Group names by first letter (A-Z)
4. Write output as JSON

Implementation ready for Code agent...
```

## Code Structure

```
demos/orchestrator/
├── run_orchestrator.py      # Entry point
├── spec.md                  # The software requirement
└── README.md                # Walkthrough
```

## The Routing Lesson

**Key insight:** You use the Plan agent's reasoning tokens only for decisions that require it.

- **Use Plan agent (gpt-5.4) for:** Decomposing a complex problem, routing between teams, architectural decisions
- **Use Code agent (gpt-5-mini) for:** Writing the actual code, fixing bugs, refactoring

In this demo, you see why blindly using gpt-5.4 for everything would waste money and add latency.

## Extending This Demo

To add a new task:

1. Edit `demos/orchestrator/spec.md` with a new software requirement
2. Run `uv run python demos/orchestrator/run_orchestrator.py`

The Plan agent will generate a fresh plan for your new task.

---

Next: [GitLab Agent](gitlab-agent.md) to see real API integration.

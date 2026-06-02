# Demo: Orchestrator (Planning + Delegation)

See **task-specific model routing in action**: a reasoning model plans, a coding model executes.

## What It Does

This demo implements a classic agent pattern:

1. **Orchestrator (gpt-5.4)** receives a high-level request
2. Breaks it into subtasks and decides which specialist should handle each
3. **Delegates to Developer (gpt-5-mini)** for implementation
4. Returns the final result

### Example Flow

**Task:** "Build a function to analyze log files and return error frequencies by type."

1. **Orchestrator thinks:**
   - "The user wants log parsing and aggregation."
   - "Subtask 1: Write a parser function (developer's job)"
   - "Subtask 2: Implement error grouping (developer's job)"
   - "Subtask 3: Return a summary (developer's job)"

2. **Orchestrator delegates to Developer:**
   - "Write a Python function that parses syslog, groups errors by type, and returns a dict of {error_type: count}"

3. **Developer delivers:** Working Python function with tests.

4. **Orchestrator approves** and returns to the user.

**Cost breakdown:** ~1 reasoning request (expensive) + ~1 coding request (cheap) = **optimal**.

## Goal

Understand:
- How reasoning models excel at decomposition, not implementation
- Why you route sparingly to gpt-5.4 (orchestration only)
- How to structure agent workflows for cost and speed

## How to Run

```bash
uv run python demos/orchestrator/main.py
```

This script:
1. Defines an orchestrator agent (gpt-5.4) with a set of delegation rules
2. Defines a developer agent (gpt-5-mini) with implementation instructions
3. Submits a sample task: "Implement a CI/CD status checker"
4. Prints the orchestrator's plan and the developer's output

### Sample Output

```
=== Orchestrator Plan ===
Task: Implement a CI/CD status checker
Subtasks:
1. Fetch the latest CI/CD run from GitLab API (use GITLAB_PAT)
2. Parse the job status and extract pass/fail counts
3. Generate a summary report in Markdown

Delegating to developer...

=== Developer Output ===
def check_ci_status(project_id, token):
    """Fetch and summarize CI/CD run status."""
    import requests
    
    url = f"https://<your-internal-gitlab>/api/v4/projects/{project_id}/pipelines"
    ...
    (working code here)

=== Final Result ===
✓ Orchestrator approved the implementation
✓ Total cost: ~2 credits (vs 10+ if all routed to gpt-5.4)
```

## Code Structure

```
demos/orchestrator/
├── main.py                  # Entry point
├── agents.py                # Orchestrator + Developer definitions
├── delegator.py             # Routing logic
└── sample_tasks.py          # Example tasks
```

## The Routing Lesson

**Key insight:** You use gpt-5.4's reasoning tokens only for decisions that require it.

- **Use gpt-5.4 for:** Decomposing a complex problem, routing between teams, architectural decisions
- **Use gpt-5-mini for:** Writing the actual code, fixing bugs, refactoring

In this demo, you see why blindly using gpt-5.4 for everything would waste money and add latency.

## Extending This Demo

To add a new task:

1. Edit `demos/orchestrator/sample_tasks.py`
2. Add a dict with `{"description": "...", "expected_subtasks": [...]}`
3. Run `python demos/orchestrator/main.py`

The orchestrator will re-plan for your new task.

---

Next: [GitLab Agent](gitlab-agent.md) to see real API integration.

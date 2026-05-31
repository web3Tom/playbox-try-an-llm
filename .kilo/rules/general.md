# Always-on rules (all agents)

These rules apply to every Kilo Code agent in this repo, regardless of role.

- **Network:** only internal GitLab and whitelisted Azure (Playbox APIM) endpoints are
  reachable. Never call the public internet.
- **Secrets:** read all credentials from `.env`. Never hardcode or commit secrets; commit
  `.env.example` only.
- **Branching:** never commit to `main`. Work on the `sandbox/<user>-<timestamp>` branch that
  `scripts/init.sh` creates, and integrate via merge request.
- **Routing:** pick the cheapest model that fits the task (see `.kilo/system_prompt.md`). Do
  not default to `gpt-5.4`.
- **Evidence:** show command/test output before claiming a demo works. "Should work" is not done.
- **Scope:** change only what the task asks for. Flag unrelated issues; do not fix them silently.

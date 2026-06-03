# Agent Extensions

The Playbox is agent-tool agnostic. **Kilo Code** is the primary, fully-scaffolded
extension; **Codex** is scaffolded as an alternative; **Cline** is documented as a
supported alternative. All three follow the same two-tier model — a machine-wide
**global** config and a repo-local **project** config, where the project config wins.

## Quick comparison

| Dimension | **Kilo Code** | **Codex** | **Cline** |
|---|---|---|---|
| Form factor | VS Code / JetBrains ext + CLI | CLI-first (+ IDE integration) | VS Code / JetBrains ext |
| Global config | `~/.config/kilo/kilo.jsonc` | `~/.codex/config.toml` (`$CODEX_HOME`) | VS Code globalStorage (UI-managed) |
| Project config | `.kilo/kilo.jsonc` | `.codex/config.toml` — project keys only (model/reasoning/approval/sandbox) | `.clinerules/` |
| Rules | `.kilo/rules/*.md` (+ `rules-{mode}/`) | `AGENTS.md` (global + nested, closest wins) | `.clinerules/*.md\|.txt`; global `~/Documents/Cline/Rules/` |
| Skills | `.kilo/skills/` > `~/.kilo/skills/` | `~/.codex/skills/` | — (none native) |
| Agents / modes | `.kilo/agents/*.md` + `agent{}` in config | per-role `~/.codex/<name>.config.toml` (no `[profiles.*]` since v0.134) | built-in **Plan / Act** only |
| System prompt | `.kilo/system_prompt.md` | system prompt + `AGENTS.md` | rules overlay |
| Workflows | (skills / modes) | `~/.codex/prompts/` | `.clinerules/workflows/`; global `~/Documents/Cline/Workflows/` |
| MCP | `mcp{}` in `kilo.jsonc` | `[mcp_servers.*]` in config.toml | `cline_mcp_settings.json` (globalStorage) |
| Precedence | project > global | nested AGENTS.md, closest wins | project > global |
| Cross-tool | reads `AGENTS.md` | `AGENTS.md` is native | reads `~/.agents/AGENTS.md` |

## Kilo Code (primary)

- **Global:** `~/.config/kilo/kilo.jsonc` — machine-wide provider + `agent{}` defaults and global `instructions`.
- **Project:** `.kilo/kilo.jsonc` — provider connection, agent/mode overrides, `mcp{}`.
- **Rules:** `.kilo/rules/*.md` for all modes; `.kilo/rules-{mode}/` to scope rules to one mode. Loaded via the `instructions` key. → here: `.kilo/rules/general.md`.
- **Skills:** `.kilo/skills/` (project) overrides `~/.kilo/skills/` (global); re-scanned each session.
- **Agents / modes:** `.kilo/agents/*.md` (frontmatter + markdown prompt) **and** the global-config `agent{}` block. Built-ins (`code`, `plan`, `debug`, `ask`, `orchestrator`, `explore`, `general`) are overridable by slug. → here: `code` (default) and `plan` are overridden in `kilo.jsonc`; `doc-writer`, `react-frontend`, `summarizer` are `.md` files; the deprecated `orchestrator` is disabled.
- **System prompt:** `.kilo/system_prompt.md`.

> The global config root (`~/.config/kilo/`) and global skills root (`~/.kilo/`) differ across
> docs — verify the exact global skills path against Kilo's `file-locations.md` for your version.

## Codex (alternative, scaffolded)

- **Global (user/system):** `~/.codex/config.toml` (override root via `$CODEX_HOME`). Holds the **provider/auth** (`model_provider`, `[model_providers.*]`), `[mcp_servers.*]`, sandbox/approval policy, and `[projects."..."]` trust levels. The APIM provider block **must** live here, not in the project file.
- **Project:** `.codex/config.toml` is read for **project-scoped keys only** — `model`, `model_reasoning_effort`, `approval_policy`, `sandbox_mode`. Provider, auth, and profile config are **ignored** in project-local files. The repo ships placeholders only; the DevPod harness supplies the real provider block in user/system config.
- **Rules / instructions:** `AGENTS.md` — global `~/.codex/AGENTS.md` plus nested repo `AGENTS.md` (closest wins). This is Codex's native instruction format.
- **Prompts (slash commands):** `~/.codex/prompts/`.
- **Skills:** `~/.codex/skills/`.
- **"Roles":** Codex ≥ 0.134 no longer reads `[profiles.*]` from `config.toml`; role switching (where supported) uses separate user-level files such as `~/.codex/orchestrator.config.toml`.
- **MCP:** `[mcp_servers.<name>]` blocks in user/system `config.toml`.

## Cline (alternative, documented)

- **Global:** managed via the Cline UI (VS Code globalStorage); global rules in `~/Documents/Cline/Rules/`, global workflows in `~/Documents/Cline/Workflows/`.
- **Project:** `.clinerules/` at repo root — Cline merges **all** `.md`/`.txt` files inside (numeric prefixes like `01-…` order them). A single `.clinerules` file also works.
- **Rules management:** a sidebar panel (v3.13+) toggles individual global/workspace rule files.
- **Workflows:** `.clinerules/workflows/` (project).
- **Modes:** built-in **Plan** and **Act** only — no custom modes/agents, so the Kilo roster does not map 1:1. The closest equivalent is project rule files.
- **Skills:** none native.
- **MCP:** `cline_mcp_settings.json` under the extension's globalStorage (`saoudrizwan.claude-dev/settings/…`); in the DevPod, under the code-server user dir.
- **Cross-tool:** reads `~/.agents/AGENTS.md`, so shared instructions can be tool-agnostic.

## How this repo uses each

| | Kilo (primary) | Codex (scaffolded) | Cline (alternative) |
|---|---|---|---|
| Config in repo | `.kilo/kilo.jsonc` | `.codex/config.toml` | — (would be `.clinerules/`) |
| Roster | `code` / `plan` + 3 `.md` agents | per-role user configs | Plan / Act + rules |
| Rules | `.kilo/rules/general.md` | repo `AGENTS.md` (+ nested) | `AGENTS.md` |
| Secrets guard | `.env` denied per-agent | sandbox + no `env_key` | rule-based |

## Sources

- Kilo Code: [Skills](https://kilo.ai/docs/customize/skills), [Custom Rules](https://kilo.ai/docs/customize/custom-rules), [Custom Modes](https://kilo.ai/docs/customize/custom-modes), [file-locations](https://github.com/Kilo-Org/kilocode-legacy/blob/main/docs/file-locations.md)
- Cline: [Rules](https://docs.cline.bot/customization/cline-rules), [Rules vs Workflows](https://cline.bot/blog/stop-adding-rules-when-you-need-workflows)
- Codex: [Config reference](https://developers.openai.com/codex/config-reference)

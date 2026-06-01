---
created: 2026-05-13
updated: 2026-05-31
description: Overview of the Try-an-LLM task for the Polestar Playbox
---
# SYSTEM HANDOVER CONTEXT: POLESTAR PLAYBOX TEMPLATE PROJECT

> [!note] Reconciled 2026-05-31
> This brief was originally drafted around Roo Code (`.roo/` / `.ai/`). It has been reconciled
> to the locked project decisions: **Kilo Code is the only agent config scaffolded** (`.kilo/`),
> with Cline and Codex documented as supported alternatives; **role files live in `.kilo/agents/`**
> (Kilo renamed Roo "custom modes" → "agents"); `gpt-5.4` is treated as a **reasoning model**
> with per-role output limits per [ADR-0001](docs/adr/ADR-0001.md); Python tooling is **`uv` / `pyproject.toml`** (no
> `requirements.txt`). The on-disk scaffold lives at `workspace/playbox-try-an-llm/` and is
> mirrored publicly at https://github.com/web3Tom/playbox-try-an-llm. See the project spec
> §8 for the decision log.

> [!note] Demo #1 superseded 2026-05-31
> The first demo was changed from `pm-ui` (a Streamlit chat UI on port 8501) to `codebase-analyzer`
> (a multi-stage repo→graph analyzer with a React dashboard on port 5174). The Epic, sub-issues,
> and embedded skeleton code below describe the ORIGINAL plan and are retained as a record; the
> current first demo is `demos/codebase-analyzer/`.

## 1. Project Overview

The target initiative is the "Polestar Playbox," an internal-facing enterprise AI Sandbox providing a secure, network-controlled environment for developers and non-technical Product Managers to experiment with agentic workflows. The immediate goal is to develop a `devpod`-ready template repository serving as the "Try an LLM" entry point.

## 2. Technical Environment & Constraints

- **Infrastructure:** Deployed via DevPod (browser-based VSCode) within a GitLab project directory.

- **Network:** Highly restricted ingress/egress. Agents can only access approved internal GitLab APIs and whitelisted Azure model endpoints.

- **Approved Models (Azure deployments):**

    - `gpt-5.4` (Orchestration / planning — **reasoning model**)

    - `gpt-5.4-mini` (Everyday dev)

    - `gpt-5.4-nano` (Summarization)

    - `gpt-4o-transcribe-diarize` (Audio processing)

    - `text-embedding-3-large` (RAG / embeddings)

    > **All models are deployed and live:** `gpt-5.4`, `gpt-5.2`, `gpt-5.1`, `gpt-5-nano`,
    > `gpt-5-mini`, `gpt-5`, `gpt-4o`, `gpt-4o-mini`, `gpt-5.4-mini`, `gpt-5.4-nano`,
    > `gpt-4o-transcribe-diarize`, and `text-embedding-3-large`.

- **IDE Extension:** **Kilo Code** is the scaffolded agent surface (`.kilo/`). **Cline** and
  **Codex** are documented as supported alternatives only — each reads its own config directory,
  so only `.kilo/` is provided here.

- **Core Architectural Concepts:**

    - Agent Configuration as Code (the `.kilo/` directory holds rules, agents/roles, skills, and model routing).

    - Task-specific model routing (the point — never default everything to `gpt-5.4`).

    - Executable enterprise demos bridging sandbox experimentation with production value.


## 3. Spec-Driven Development Strategy

The development of this template utilizes a GitLab-issue-driven, spec-driven workflow. The architecture incorporates concepts from the following evaluated frameworks:

- **SWE-agent (`princeton-nlp/SWE-agent`):** Adapting its Agent-Computer Interface (ACI) commands for precise, limited file viewer/linter tools within the `.kilo/skills/` directory.

- **GitHub Spec-Kit (`github/spec-kit`):** Utilizing its `specify-cli` pipeline (Constitution $\rightarrow$ Spec $\rightarrow$ Plan $\rightarrow$ Implementation) to bridge PM-generated markdown specs with developer execution.

- **Agent-Skills (`addyosmani/agent-skills`):** Importing deterministic, atomic Python/TypeScript tool definitions into the workspace to safely manage directory parsing and AST edits.


---

## 4. Active GitLab Epic

# Epic: Polestar Playbox - Template Starter Repository

## Context & Vision
The Polestar Playbox is our internal enterprise AI Sandbox, designed to democratize access to advanced generative capabilities in a secure, network-controlled environment. While the platform provides unlimited access to a powerful suite of Azure-deployed models (GPT-5 series, embeddings, and transcription), simply providing an API key or a blank chat interface is insufficient for driving enterprise adoption.

This Epic tracks the development of the "Try an LLM" starter template, the primary entry point for users accessing the Playbox via DevPod. The template is designed to accommodate a dual audience: non-technical Product Managers seeking immediate utility, and technical developers looking to understand agentic patterns.

## Core Concepts & Strategic Reasoning
To ensure users extract maximum value from the Playbox, this repository is architected to teach three core concepts by example:

### 1. Agent Configuration as Code (The .kilo Directory)
**The Concept:** Moving users away from isolated, copy-paste web chats and into context-aware, integrated workspaces.
**The Reasoning:** By exposing users to the `.kilo/` configuration directory, we demonstrate how agents can be given persistent instructions, specific skills, and strict boundaries. It teaches developers that AI behavior can be version-controlled, customized per repository, and standardized across a team, turning a generic LLM into a domain-specific teammate. Kilo Code is the scaffolded surface; Cline and Codex are supported alternatives, but each reads its own config format.

### 2. Task-Specific Model Routing
**The Concept:** Matching the right model to the right job based on complexity, speed, and context windows.
**The Reasoning:** Users naturally gravitate toward the most powerful model (e.g., `gpt-5.4`) for everything, which is inefficient. By pre-configuring specific agents for specific endpoints — using `gpt-5.4-nano` for rapid summarization, `gpt-5.4-mini` or `5.2` for everyday coding, and `gpt-5.4` exclusively for complex orchestration and planning — we educate users on cost-efficiency and latency optimization. Crucially, `gpt-5.4` is a **reasoning model**: its reasoning tokens are spent from the *same* per-request output budget as the visible answer, so each role's output cap and reasoning effort must be sized to the job (see [ADR-0001](docs/adr/ADR-0001.md)).

### 3. Show, Don't Tell Enterprise Demos
**The Concept:** Providing functional, immediately executable code paths rather than abstract documentation.
**The Reasoning:** The blank canvas problem is the biggest hurdle to AI adoption. PMs need to see immediate value (provided via a local UI and prompt library), while developers need to see how AI interacts with existing infrastructure. The included demos (GitLab API integration, RAG with embeddings, and Orchestrator patterns) provide concrete examples of how to securely bridge the gap between the isolated sandbox and actual business workflows.

## Proposed Repository Skeleton (Directory Tree)
The repository is scaffolded according to the following structure to support the concepts outlined above (this matches the on-disk scaffold at `workspace/playbox-try-an-llm/`):

polestar-playbox-template/
├── .kilo/                      # Agent Configuration (Kilo Code)
│   ├── agents/                 # Per-role definitions, each pinned to a model
│   │   ├── orchestrator.md     # -> gpt-5.4 (reasoning; planning/delegation)
│   │   ├── everyday-dev.md     # -> gpt-5.4-mini (workhorse)
│   │   ├── summarizer.md       # -> gpt-5.4-nano
│   │   └── react-frontend.md   # -> gpt-5.2 (fallback gpt-5.4-mini)
│   ├── rules/                  # Always-on global rules (general.md)
│   ├── skills/                 # Custom tool definitions
│   ├── commands/               # Reusable slash commands
│   ├── kilo.jsonc              # Provider/model config + per-role limits (ADR-0001)
│   └── system_prompt.md        # Global rules & network constraints
├── demos/                      # Executable Use Cases
│   ├── codebase-analyzer/      # 1. Repo→graph analyzer (flagship routing demo)
│   │   ├── analyze.py
│   │   └── dashboard/
│   ├── orchestrator/           # 2. Planning & Delegation
│   │   ├── spec.md
│   │   └── run_orchestrator.py
│   ├── gitlab-agent/           # 3. Enterprise API Integration
│   │   └── review_issues.py
│   ├── react-ui/               # 4. Frontend Generation (scaffold exercise)
│   ├── transcription/          # 5. Multimodal / Audio Processing
│   │   └── transcribe.py
│   ├── rag-embeddings/         # 6. Context Grounding (Embeddings)
│   │   ├── data/
│   │   └── rag_query.py
│   └── data-analysis/          # 7. Agent-written pandas over a mock CSV
│       ├── analyze_data.py
│       └── transaction_metrics.csv
├── specs/                      # Spec-Kit-style specs
├── docs/                       # MkDocs Documentation Source
│   ├── index.md
│   ├── getting-started/
│   ├── models.md
│   └── adr/                    # Architecture Decision Records (ADR-0001)
├── utils/
│   └── token_tracker.py        # Per-call token/cost logging
├── scripts/
│   └── init.sh                 # Bootstrap script (env scaffold + branch creation + uv sync)
├── .devpod/
│   └── install-kilo-code.sh    # Installs the Kilo Code extension on workspace start
├── .env.example                # Template for endpoint URLs and PATs
├── devfile.yaml                # DevPod environment specification (ports pre-forwarded)
├── mkdocs.yml                  # MkDocs configuration
├── pyproject.toml              # Python tooling (uv-managed; no requirements.txt)
├── PROMPTS.md                  # Copy-paste prompt library for PMs
├── AGENTS.md                   # Working contract for AI agents in this repo
└── README.md                   # Repository overview

## Implementation Plan (Sub-Issues)
The development of this epic will be tracked via the following sub-issues:

*   **Issue #1: DevPod Infrastructure & Bootstrap Script**
    *   Focus: devfile.yaml creation and init.sh for automated branch checkout to prevent direct commits to main.
*   **Issue #2: Agent Configuration & System Prompts**
    *   Focus: Scaffolding the `.kilo/` directory structure and writing the per-role agent files for model routing.
*   **Issue #3: PM Experience - Local UI & Prompt Library**
    *   Focus: Developing run_ui_playground.py and PROMPTS.md for low-friction user onboarding.
*   **Issue #4: Technical Demos (Orchestrator & GitLab API)**
    *   Focus: Building the advanced agentic workflow demos.
*   **Issue #5: Technical Demos (ReactJS & Transcription)**
    *   Focus: Providing UI scaffolding and demonstrating the gpt-4o-transcribe-diarize endpoint.
*   **Issue #6: RAG & Embeddings Demo**
    *   Focus: Implementing local vector search using the text-embedding-3-large endpoint.
*   **Issue #7: MkDocs Documentation Site**
    *   Focus: Compiling the educational guide mapping users to the features above.


---

## 5. Active Sub-Issues

### Issue #1: DevPod Infrastructure & Bootstrap Script

**Context:** Users will launch this template via DevPod. We need to ensure the container environment is properly configured to handle Python/Node workflows and that a bootstrap script automates the initial setup (branch creation, env variable scaffolding) so users aren't manually configuring their sandbox.

**Tasks:**

1. Create a `devfile.yaml` to define the DevPod workspace. It should include a standard Linux container with Python 3.11+ and Node.js 20+, with all demo service ports pre-forwarded.

2. Write a bash script `scripts/init.sh` that checks if the user is on the `main` branch, automatically creates/checks out a new branch (`sandbox/<gitlab-username>-<timestamp>`), copies `.env.example` to `.env`, and runs `uv sync`.

    **Acceptance Criteria:**


- [ ] `devfile.yaml` successfully launches a DevPod environment with Python and Node.js installed.

- [ ] `scripts/init.sh` is executable (`chmod +x`).

- [ ] `init.sh` successfully creates a uniquely named branch based on the user's local git config or system variables.

- [ ] `init.sh` does not overwrite an existing `.env` file if one is already present.


### Issue #2: Agent Configuration & System Prompts

**Context:** The repository needs to define how Kilo Code operates within the Playbox, requiring the `.kilo/` configuration directory and specific agent roles (Kilo's term for Roo's "custom modes") tailored to Azure model endpoints.

**Tasks:**

1. Create a `.kilo/` directory structure containing `agents/`, `rules/`, `skills/`, `commands/`, and the `kilo.jsonc` provider config.

2. Create specialized agent role files in `.kilo/agents/`: `orchestrator.md` (gpt-5.4), `everyday-dev.md` (gpt-5.4-mini/5.2), and `summarizer.md` (gpt-5.4-nano).

3. Draft a global `.kilo/system_prompt.md` enforcing Playbox network constraints.

    **Acceptance Criteria:**


- [ ] Directory structure `.kilo/agents/`, `.kilo/rules/`, and `.kilo/skills/` exists.

- [ ] At least three distinct agent role files exist, each explicitly pinning the target gpt-5 series model to be used.

- [ ] Global rules file strictly prohibits attempting to access external internet APIs (except internal GitLab/Azure endpoints).


### Issue #3: PM Experience - Local UI & Prompt Library

**Context:** To assist non-technical Product Managers, provide a lightweight local web UI and a library of tested prompts for immediate experimentation without IDE command palettes.

**Tasks:**

1. Create `demos/pm-ui/run_ui_playground.py` (Streamlit) connecting to the Azure model endpoints.

2. Create `PROMPTS.md` containing copy-pasteable prompt templates.

3. Add a command to spin up the UI easily.

    **Acceptance Criteria:**


- [ ] `run_ui_playground.py` runs locally on port 8501 (Streamlit) without syntax errors.

- [ ] Script uses environment variables from `.env` for Azure endpoint authentication.

- [ ] `PROMPTS.md` contains at least 3 formatted prompt templates with placeholders.


### Issue #4: Technical Demos (Orchestrator & GitLab API)

**Context:** Demonstrate advanced agentic capabilities: breaking down complex tasks and interacting with enterprise infrastructure.

**Tasks:**

1. **Orchestrator Demo**: Create `demos/orchestrator/` with a `spec.md` and `run_orchestrator.py` showing planner/sub-agent delegation (gpt-5.4 plans, delegates code-gen to gpt-5.4-mini).

2. **GitLab API Demo**: Create `demos/gitlab-agent/` with a `review_issues.py` script authenticating via GitLab PAT to read/summarize current project issues using `gpt-5.4-mini`.

    **Acceptance Criteria:**


- [ ] `demos/orchestrator/spec.md` is populated with a sample software requirement.

- [ ] GitLab demo script successfully handles pagination and authentication via `GITLAB_PAT`.

- [ ] Both demos include a `README.md` explaining execution.


### Issue #5: Technical Demos (ReactJS Frontend & Transcription)

**Context:** Provide boilerplate for a modern web frontend and demonstrate multimodal/audio capabilities using the Azure SDK.

**Tasks:**

1. **ReactJS Demo**: Scaffold Vite+React template in `demos/react-ui/`. Create `.kilo/agents/react-frontend.md` explicitly for this domain.

2. **Transcription Demo**: Create `demos/transcription/` with `transcribe.py` utilizing the Azure SDK and `gpt-4o-transcribe-diarize` on a dummy audio file.

    **Acceptance Criteria:**


- [ ] `demos/react-ui/` starts via `npm install && npm run dev` without errors.

- [ ] `react-frontend.md` agent role file exists with domain-specific instructions.

- [ ] `transcribe.py` imports correct Azure SDK libraries with proper error handling.


### Issue #6: RAG & Embeddings Demo

**Context:** Showcase how users can ground LLMs in specific company data using `text-embedding-3-large`.

**Tasks:**

1. Create `demos/rag-embeddings/` with a `rag_query.py` script using a local vector store (ChromaDB/FAISS).

2. Provide a sample document (e.g., `mock_company_policy.pdf`) in a `data/` folder.

    **Acceptance Criteria:**


- [ ] Script chunks the sample document and generates embeddings without crashing.

- [ ] Script retrieves relevant chunks based on queries.

- [ ] Vector database is strictly in-memory or saved locally (no external DB connections).


### Issue #7: MkDocs Documentation Site

**Context:** A centralized guide for users to navigate the Playbox, understand models, and run demos.

**Tasks:**

1. Initialize an MkDocs project (`mkdocs.yml`) with the `material` theme.

2. Create `docs/` structure: `index.md`, `getting-started/`, `models.md`, `adr/`, and `demos/` sub-pages.

    **Acceptance Criteria:**


- [ ] `mkdocs serve` runs cleanly locally.

- [ ] Navigation structure correctly links all markdown files.

- [ ] Content accurately reflects the available Azure Playbox models.


---

## 6. Skeleton Template Code

### Polestar Playbox - "Try an LLM" Starter Template

This template provides the initial directory structure and essential files for the "Polestar Playbox" starter repository, designed for deployment via DevPod on GitLab.

#### Directory Structure Overview

```text
├── .kilo/                  # Kilo Code Agent Configuration
│   ├── agents/             # Per-role definitions (each pins one model)
│   ├── rules/              # Always-on global rules
│   ├── skills/             # Reusable code snippets/tools for agents
│   ├── commands/           # Pre-defined prompts for users
│   ├── kilo.jsonc          # Provider/model config + per-role limits
│   └── system_prompt.md    # Global rules & network constraints
├── demos/                  # Demo Use Cases
│   ├── codebase-analyzer/
│   ├── orchestrator/
│   ├── gitlab-agent/
│   ├── react-ui/
│   ├── transcription/
│   ├── rag-embeddings/
│   └── data-analysis/
├── docs/                   # MkDocs source files (Guide & Concepts) + adr/
├── .devpod/                # DevPod helpers
│   └── install-kilo-code.sh # Installs the Kilo Code extension on workspace start
├── devfile.yaml            # DevPod specification (ports pre-forwarded)
├── scripts/
│   └── init.sh             # Bootstrap: env scaffold + branch creation + uv sync
├── utils/
│   └── token_tracker.py    # Per-call token/cost logging
├── mkdocs.yml              # MkDocs configuration
├── pyproject.toml          # Python tooling (uv-managed)
├── PROMPTS.md              # Copy-paste prompt library for PMs
├── README.md
└── AGENTS.md               # Working contract for AI agents in this repo
```

#### File Contents

##### 1. DevPod Configuration & Startup
We need to ensure the environment has the necessary runtimes (Node for React, Python for scripts) and automates the branching.

**`devfile.yaml`**
```yaml
schemaVersion: 2.2.0
metadata:
  name: playbox-try-an-llm
  description: Try an LLM in the Polestar Playbox
components:
  - name: tools
    container:
      image: mcr.microsoft.com/devcontainers/universal:2-linux
      memoryLimit: 4G
      command: ['sleep', 'infinity']
      env:
        - name: AZURE_OPENAI_API_KEY
          value: "" # Injected by the cluster/vault in production
        - name: AZURE_OPENAI_ENDPOINT
          value: "" # e.g. https://<your-playbox-apim-endpoint>/playbox-ai-deployment/openai
      endpoints:
        - name: codebase-analyzer
          targetPort: 5174
          exposure: public
        - name: docs
          targetPort: 8000
          exposure: public
        - name: react-ui
          targetPort: 5173
          exposure: public
commands:
  - id: install-kilo-code
    exec:
      component: tools
      commandLine: "bash ${PROJECT_SOURCE}/.devpod/install-kilo-code.sh"
      workingDir: ${PROJECT_SOURCE}
  - id: init
    exec:
      component: tools
      commandLine: "bash ${PROJECT_SOURCE}/scripts/init.sh"
      workingDir: ${PROJECT_SOURCE}
events:
  postStart:
    - install-kilo-code
    - init
```

**`scripts/init.sh`**
*(Moves the user off `main` onto a personal sandbox branch, scaffolds `.env`, and installs Python deps with `uv`. Idempotent — safe to re-run on every workspace start.)*
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Initializing your Polestar Playbox workspace..."

# 1. Environment variables
if [ ! -f .env ]; then
    cp .env.example .env
else
    echo ".env already exists; leaving it untouched."
fi

# 2. Move off main onto a personal sandbox branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    USER_ID=$(git config user.name | tr '[:upper:] ' '[:lower:]-' || echo "playbox-user")
    NEW_BRANCH="sandbox/${USER_ID}-$(date +%s)"
    git checkout -b "$NEW_BRANCH"
fi

# 3. Python dependencies (uv-managed — no requirements.txt)
if command -v uv >/dev/null 2>&1; then
    uv sync
fi

echo "Initialization complete. Open PROMPTS.md to begin."
```

##### 2. AI Agent Configuration (.kilo/)
We use the `.kilo/` structure. Roles live in `.kilo/agents/` (Kilo's term for Roo's "custom modes"), each optimized for one of the available GPT-5 models.

**`.kilo/agents/orchestrator.md`** (Optimized for gpt-5.4 — reasoning model)
```markdown
# Role: Orchestrator
You are the Lead Technical Project Manager. Your job is to break down complex tasks into smaller, executable steps.
You MUST prioritize using the `gpt-5.4` model for planning. It is a reasoning model — reserve it for genuine planning, not routine code generation.
When you need to generate code, delegate the task to a specific sub-agent (e.g., the React Frontend role) and instruct them to use `gpt-5.2` or `gpt-5.4-mini` to save tokens.
Always review the output of your sub-agents before declaring a task complete.
```

**`.kilo/agents/react-frontend.md`** (Optimized for gpt-5.2 or gpt-5.4-mini)
```markdown
# Role: React Frontend Developer
You are an expert ReactJS developer. You focus on building clean, responsive UI components.
Use the `gpt-5.2` model for rapid UI iterations (fallback `gpt-5.4-mini` for harder reasoning).
Always prefer functional components and React Hooks.
If you need complex logic or state management, you may request the user to switch to `gpt-5.4`.
```

**`.kilo/agents/summarizer.md`** (Optimized for gpt-5.4-nano)
```markdown
# Role: Content Summarizer
You are a fast, efficient summarization engine.
You MUST strictly use the `gpt-5.4-nano` model.
Provide concise, bulleted summaries of provided text, code, or transcripts. Focus only on the core facts and action items.
```

**`AGENTS.md`**
```markdown
# Polestar Playbox AI Agents Guide

Welcome to the Playbox! Your DevPod is equipped with the **Kilo Code** coding assistant. To get the best results, you need to tell the AI *who* it is and *what* model it should use. (Cline and Codex are supported alternatives, but `.kilo/` is the scaffolded surface.)

We have pre-configured roles in the `.kilo/agents/` directory.

### Available Models in the Playbox:
*   **GPT-5.4:** The heavyweight reasoning model. Best for complex logic, orchestration, and planning — route sparingly.
*   **GPT-5.4-mini:** The daily driver. Fast, capable, great for standard coding.
*   **GPT-5.4-nano:** The speedster. Quick summaries and simple text manipulation.
*   **GPT-5.2:** Reliable model for general tasks and UI/frontend work.
*   **GPT-4o-Transcribe-Diarize:** Specialized for audio processing.
*   **Text-Embedding-3-Large:** Used for semantic search and RAG applications.

### How to use these Roles:
In Kilo Code, switch agents or reference a role file in your prompt. For example:
> "@orchestrator Read the spec in `demos/orchestrator/spec.md` and create a plan."
```

##### 3. Demos

**`demos/orchestrator/README.md`**
```markdown
# Demo 1: The Orchestrator

**Goal:** Learn how to use a highly capable reasoning model (`gpt-5.4`) to plan a task, and delegate the execution to smaller models.

1. Open Kilo Code.
2. Select the `gpt-5.4` model (orchestrator role).
3. Paste this prompt:
   > "Act as the Orchestrator (@.kilo/agents/orchestrator.md). Read `demos/orchestrator/spec.md`. Create a step-by-step plan. For step 1, ask me to switch to the `gpt-5.4-mini` model before you generate the code."
```

**`demos/orchestrator/spec.md`**
```text
Project: Build a simple Python script that reads a CSV file of names and outputs a JSON file grouped by the first letter of the name.
```

**`demos/react-ui/README.md`**
```markdown
# Demo: UI Coding Agent

**Goal:** See how the AI handles existing project structures and specialized rules.

*Note: A basic React app (e.g., via Vite) should be scaffolded in this directory.*

1. Open Kilo Code and select `gpt-5.4-mini`.
2. Paste this prompt:
   > "Act as the Frontend Dev (@.kilo/agents/react-frontend.md). Start the local development server in the `demos/react-ui` directory. Then, modify `App.jsx` to include a button that toggles between dark mode and light mode."
```

**`demos/transcription/transcribe.py`**
```python
# demos/transcription/transcribe.py
import os
from openai import AzureOpenAI

# This demo assumes your environment variables are set by the Playbox cluster
# AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT

client = AzureOpenAI(
    api_version="2024-02-15-preview",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY")
)

# In a real scenario, this would be an actual audio file.
audio_file_path = "sample_audio.mp4"

print(f"Sending {audio_file_path} to the gpt-4o-transcribe-diarize endpoint...")

# Example API call
# response = client.audio.transcriptions.create(
#     model="gpt-4o-transcribe-diarize",
#     file=open(audio_file_path, "rb")
# )
# print(response.text)

print("Transcription complete! Now, ask the AI (using gpt-5.4-nano) to summarize the output.")
```

**`demos/rag-embeddings/README.md`**
```markdown
# Demo: Semantic Embeddings

**Goal:** Understand how `text-embedding-3-large` turns text into numbers for search.

1. Run the demo:
   > `uv run python demos/rag-embeddings/rag_query.py`

It generates embeddings for sample policy documents, stores them in an in-memory ChromaDB instance, retrieves the most relevant chunk for a query, and answers using `gpt-5.4-mini` grounded only on the retrieved context.
```

##### 4. Documentation Site (MkDocs)

**`mkdocs.yml`**
```yaml
site_name: Polestar Playbox — Try an LLM
docs_dir: docs
nav:
  - Home: index.md
  - Getting Started:
    - Environment Overview: getting-started/environment.md
    - AI Agents & Models: getting-started/agents.md
  - Models & Routing: models.md
  - Demos:
    - Codebase Analyzer: demos/codebase-analyzer.md
    - Orchestrator: demos/orchestrator.md
    - GitLab Agent: demos/gitlab-agent.md
    - RAG & Embeddings: demos/rag-embeddings.md
    - Data Analysis: demos/data-analysis.md
    - Transcription: demos/transcription.md
    - React UI: demos/react-ui.md
  - Decisions:
    - ADR-0001 (model limits): adr/ADR-0001.md
theme:
  name: material
  palette:
    scheme: slate # Dark mode default
markdown_extensions:
  - pymdownx.superfences
```

**`docs/index.md`**
```markdown
# Welcome to the Polestar Playbox

The **Polestar Playbox** is your secure, unlimited sandbox for experimenting with Enterprise AI.

This environment is highly controlled. You have access to the **Kilo Code** assistant and direct endpoints to the `gpt-5` series models, all within a safe boundary.

## The "Try an LLM" Path

You are currently on the simplest path. This repository is designed to introduce you to:
1. **Configuring AI Agents:** How to give models specific rules and context via `.kilo/`.
2. **Model Selection:** Knowing when to use `gpt-5.4` (reasoning) vs `gpt-5.4-nano`.
3. **Practical Execution:** Running code, building UIs, and calling Azure APIs.
```

### 6-A Skeleton Template Enhancements

#### File: PROMPTS.md
```
# File: PROMPTS.md
# Polestar Playbox Prompt Library

Use these pre-tested prompts to quickly execute tasks within the Playbox environment. Copy the text, fill in the bracketed variables, and paste it into the UI Playground or your Kilo Code agent chat. Each prompt notes the model to route to.

## Product Managers
**Draft a Product Requirements Document (PRD)** *(route to gpt-5.4)*
> Act as an expert Product Manager. Draft a comprehensive Product Requirements Document (PRD) for a new feature called [Feature Name]. The primary goal of this feature is to [Primary Goal]. The target users are [Target Audience]. Please include the following sections: Executive Summary, User Stories, Out of Scope, and Success Metrics.

**Summarize User Research Transcripts** *(route to gpt-5.4-nano)*
> You are analyzing user feedback. Read the following transcript/notes and provide a concise summary. Group your findings into three categories: 1) Key Pain Points, 2) Feature Requests, and 3) General Sentiment.
>
> [Insert Transcript/Notes Here]

## Developers
**Write a Unit Test Suite** *(route to gpt-5.4-mini)*
> Review the attached file `[filename.py/js]`. Write a comprehensive unit test suite for the primary functions using [pytest/Jest]. Ensure you include edge cases for [specific constraint, e.g., null values, network timeouts].

**Code Review against Security Best Practices** *(route to gpt-5.4)*
> Perform a security-focused code review on the provided code block. Specifically look for OWASP top 10 vulnerabilities, improper error handling, and hardcoded secrets. Provide your findings in a table with columns for: Issue, Severity, and Recommended Fix.
```

#### File: demos/pm-ui/run_ui_playground.py
```python
# File: demos/pm-ui/run_ui_playground.py
import os
import logging
import streamlit as st
from openai import AzureOpenAI

# Configure logging to output to console for sandbox monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Playbox LLM Playground", layout="centered")

st.title("Polestar Playbox — Chat Interface")
st.markdown("Test the GPT-5 series endpoints without leaving your browser.")

# Guard credentials — show a warning rather than crashing.
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not endpoint or not api_key:
    st.warning("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env to call the models.")

# Model selection — picking the right model is the point.
selected_model = st.selectbox("Choose a Model:", ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.2"])
user_input = st.text_area("Enter your prompt (or paste from PROMPTS.md):")

if st.button("Generate") and user_input:
    try:
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2024-02-15-preview")
        with st.spinner(f"Querying {selected_model}..."):
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": user_input}],
            )
            st.write(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Model call failed: {e}")
        st.error(f"Error communicating with the model: {e}")
```

#### File: utils/token_tracker.py
```python
# File: utils/token_tracker.py
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Approximated enterprise costs per 1k tokens for Playbox sandbox tracking
COST_RATES = {
    "gpt-5.4": {"prompt": 0.01, "completion": 0.03},
    "gpt-5.4-mini": {"prompt": 0.001, "completion": 0.002},
    "gpt-5.4-nano": {"prompt": 0.0005, "completion": 0.001},
    "text-embedding-3-large": {"prompt": 0.00013, "completion": 0.0}
}

def log_token_usage(model_name, usage_object):
    """Parses an OpenAI API usage object and logs the estimated cost."""
    if not usage_object:
        return

    prompt_tokens = usage_object.prompt_tokens
    completion_tokens = usage_object.completion_tokens
    total_tokens = usage_object.total_tokens

    rates = COST_RATES.get(model_name, {"prompt": 0.0, "completion": 0.0})
    estimated_cost = (
        (prompt_tokens / 1000.0) * rates["prompt"] +
        (completion_tokens / 1000.0) * rates["completion"]
    )

    logging.info(
        f"Model: {model_name} | Tokens: {total_tokens} "
        f"(Prompt: {prompt_tokens}, Completion: {completion_tokens}) | "
        f"Est. Sandbox Cost: ${estimated_cost:.6f}"
    )
```

#### File: demos/rag-embeddings/rag_query.py
```python
# File: demos/rag-embeddings/rag_query.py
import os
import logging
import chromadb
from openai import AzureOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] RAG-Demo: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
)

def get_embedding(text: str):
    """Embed text with text-embedding-3-large."""
    return client.embeddings.create(input=text, model="text-embedding-3-large").data[0].embedding

if __name__ == "__main__":
    print("--- Polestar Playbox RAG Demo ---")

    # In-memory vector store only — no external DB.
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="policy_docs")

    documents = [
        "Employees are permitted up to $500 per year for home office equipment.",
        "Travel requests exceeding $1000 require VP approval.",
        "The standard core working hours are 10:00 AM to 3:00 PM local time.",
    ]
    for i, doc in enumerate(documents):
        collection.add(embeddings=[get_embedding(doc)], documents=[doc], ids=[f"doc_{i}"])

    query = "What is the policy for buying a new desk chair for my house?"
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=1)
    retrieved = results["documents"][0][0]
    logger.info(f"Retrieved Context: {retrieved}")

    # Answer grounded ONLY on retrieved context, via gpt-5.4-mini.
    prompt = f"Answer the query based ONLY on the context.\nContext: {retrieved}\nQuery: {query}"
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"\nAgent Response: {response.choices[0].message.content}")
```

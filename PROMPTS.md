# Polestar Playbox — Prompt Library

Copy-paste these pre-tested prompts to get value from the Playbox immediately — in the PM UI
playground (`demos/pm-ui/`) or your Kilo Code chat. Fill in the `[bracketed]` variables. Each
prompt notes the **model to route to**, because picking the right model is the whole point.

## For Product Managers

### 1. Draft a Product Requirements Document — *route to `gpt-5.4`*
> Act as a Senior Technical Product Manager. Draft a Product Requirements Document (PRD) for a
> new feature called **[Feature Name]**. The goal is to **[Primary Goal]**; the target users are
> **[Target Audience]**. Include: Executive Summary, User Stories, Out of Scope, Success Metrics,
> and Technical Considerations. Use clear, enterprise-ready language.

### 2. Summarize a meeting transcript — *route to `gpt-5.4-nano`*
> Summarize the following transcript. Give a 3-sentence executive summary, then a bulleted list
> of action items with assigned owners where mentioned.
>
> [Paste transcript here]

### 3. Extract structured data — *route to `gpt-5.2` or `gpt-5.4-mini`*
> Extract all tools, software, and programming languages mentioned in the following text. Output
> the result strictly as a JSON array of strings.
>
> [Paste text here]

## For Developers

### 4. Write a unit test suite — *route to `gpt-5.4-mini`*
> Review `[filename.py]`. Write a pytest suite for the primary functions. Cover edge cases for
> **[specific constraint, e.g. null values, network timeouts]**. Each test must encode *why* the
> behavior matters, not just that a value matches.

### 5. Security-focused code review — *route to `gpt-5.4`*
> Perform a security review on the code block below. Look for OWASP Top 10 issues, improper error
> handling, and hardcoded secrets. Report findings as a table: Issue | Severity | Recommended Fix.
>
> [Paste code here]

### 6. Plan, then delegate — *start on `gpt-5.4`, delegate down*
> Act as the Orchestrator (`.kilo/agents/orchestrator.md`). Read `demos/orchestrator/spec.md`,
> produce a numbered plan, and for step 1 delegate the code generation to `gpt-5.4-mini`.

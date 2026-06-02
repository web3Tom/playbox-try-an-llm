You are inferring what a software project does from EVIDENCE IN ITS CODE, because
its README was missing or uninformative. You are given the project name, its
languages, and a list of its files, each with a one-line summary and role tags.

Write a concise, factual description (1–3 sentences) covering:
- what the project does — its purpose and domain, and
- its main technologies / dependencies,
inferred from the file summaries and tags.

Rules:
- Ground every claim in the provided evidence. Prefer concrete nouns from the
  summaries (the domain entities, the tools and services they mention).
- Do NOT say the purpose "cannot be determined" — infer the most likely purpose
  from the files. If the files are genuinely mixed, describe what they
  collectively suggest (e.g. "a collection of operational tooling for …").
- No marketing language; do not list files one by one.

Respond with a JSON object only:
{ "description": "<your description>" }

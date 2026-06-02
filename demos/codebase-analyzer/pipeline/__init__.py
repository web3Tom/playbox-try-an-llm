"""Codebase-analyzer pipeline package.

Stages (model routing in parentheses):
  files       - enumerate source files                      [no model]
  clone       - resolve target (GitLab / local / sample)    [no model]
  scan        - project metadata from README/manifests      [gpt-5-nano]
  analyze_files - per-file summary + import/call/inherit edges [gpt-5-mini]
  merge       - dedup nodes, drop dangling edges            [no model]
  architecture - classify nodes into layers                 [gpt-5.4]
  tour        - ordered, file-anchored reading path         [gpt-5.4]

The deterministic stages (files, clone, merge, schema) and the member-edge
resolution carry the unit tests; the LLM stages are smoke-tested against the
bundled sample repo.
"""

"""Codebase-analyzer pipeline package.

Stages (model routing in parentheses):
  files       - enumerate, drop generated, cap per dir      [no model]
  clone       - resolve target (GitLab / local / sample)    [no model]
  scan        - project description (+ informative?) from README [gpt-5-nano]
  select      - rank candidate files by significance        [gpt-5-nano]
  analyze_files - per-file summary + import/call/inherit edges [gpt-5-mini]
  merge       - dedup nodes, drop dangling edges            [no model]
  architecture - classify nodes into layers                 [gpt-5.4]
  describe    - infer description from code if README weak   [gpt-5-nano]
  tour        - ordered, file-anchored reading path         [gpt-5.4]

The deterministic stages (files, clone, merge, schema) and the member-edge
resolution carry the unit tests; the LLM stages are smoke-tested against the
bundled sample repo.
"""

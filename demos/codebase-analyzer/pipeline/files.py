"""Deterministic file enumeration — the [no model] front of the pipeline.

Walks a repo, filters out noise (vendored deps, build output, binaries, and
boilerplate/config files like ``__init__.py`` or ``*.config.js`` that would just
burn tokens), caps the count so a huge repo can't run up an unbounded LLM bill,
and reports what it dropped. Nothing here calls a model: enumerating files is
plain code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Directories we never descend into.
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".ruff_cache", "dist", "build", "site", ".idea", ".vscode", ".mypy_cache",
    "vendor", "target", ".next", "coverage",
}

# Extensions we treat as analysable source. Anything else (images, binaries,
# lockfiles) is skipped — the LLM would learn nothing from them.
SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".kt", ".swift", ".scala", ".sh",
    ".sql", ".vue", ".svelte",
}

# Exact filenames that are boilerplate or tooling config, never worth an LLM
# call: they carry little logic to map (empty package markers, thin shims, build
# and dependency scripts), so analysing them just burns tokens. Matched
# case-insensitively against the file name. Pattern-based configs (anything like
# `*.config.js` or `.eslintrc.*`) are caught by `_is_insignificant` instead, so
# we don't have to enumerate every tool here. Edit this to taste.
IGNORE_FILES = {
    "__init__.py",   # package marker — usually empty or pure re-exports
    "__main__.py",   # thin `python -m` shim
    "setup.py",      # packaging script, not product logic
    "conftest.py",   # pytest fixtures/config, not product logic
    "manage.py",     # Django CLI shim
    "gulpfile.js",
    "gruntfile.js",
    "env.py",        # environment/config loader, not product logic
    # Deployment / release / ops scripts — infrastructure, not app architecture.
    "docker-entrypoint.sh",
    "version.sh",
    "create_release.sh",
    "helper.sh",
    "vault_login_and_agent.sh",
}


def _is_insignificant(name: str) -> bool:
    """True for boilerplate/config files that aren't worth an LLM call."""
    low = name.lower()
    if low in IGNORE_FILES:
        return True
    # Tooling config written in a code language: vite/webpack/jest/babel/tailwind/
    # postcss/next/rollup/karma/... all match one of these shapes.
    if (".config." in low or ".conf." in low) and low.endswith((".js", ".ts", ".mjs", ".cjs")):
        return True
    if low.startswith((".eslintrc", ".prettierrc", ".babelrc", ".stylelintrc")):
        return True
    # Kubernetes tooling/config (kube_ps1.sh, kubeconfig, kubectl wrappers, …).
    if low.startswith("kube"):
        return True
    # Shell helper/ops scripts (azure_helper.sh, vault_helper.sh, …) — glue, not
    # application architecture.
    if low.endswith("_helper.sh"):
        return True
    return False


# Map extension -> language label for the project summary.
_LANG_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
    ".php": "PHP", ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++", ".cs": "C#",
    ".kt": "Kotlin", ".swift": "Swift", ".scala": "Scala", ".sh": "Shell",
    ".sql": "SQL", ".vue": "Vue", ".svelte": "Svelte",
}

DEFAULT_MAX_FILES = 30
MAX_FILE_BYTES = 100_000  # skip files larger than ~100KB (generated/minified)

# Filenames treated as entry points — sorted first so truncation keeps them.
_ENTRYPOINTS = {"main.py", "app.py", "index.js", "index.ts", "cli.py"}


@dataclass
class ScanResult:
    root: Path
    files: list[str]          # relative paths, kept after the cap
    total_found: int          # how many matched before the cap
    truncated: bool           # True when total_found exceeded the cap
    languages: list[str]


def enumerate_source_files(root: str | Path, max_files: int = DEFAULT_MAX_FILES) -> ScanResult:
    """Return source files under ``root`` (relative paths), capped at ``max_files``.

    Files are sorted by a cheap importance heuristic (entry points first, then
    shallower paths) so that when we truncate we keep the files most worth
    analysing. Truncation is recorded on the result, never silent.
    """
    root = Path(root)
    found: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if _is_insignificant(path.name):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        found.append(path)

    found.sort(key=lambda p: _importance_key(p, root))
    total = len(found)
    kept = found[:max_files]

    rel = [str(p.relative_to(root)) for p in kept]
    languages = sorted(
        {_LANG_BY_EXT[p.suffix.lower()] for p in kept if p.suffix.lower() in _LANG_BY_EXT}
    )
    return ScanResult(
        root=root,
        files=rel,
        total_found=total,
        truncated=total > len(kept),
        languages=languages,
    )


def _importance_key(path: Path, root: Path) -> tuple:
    """Lower sorts first. Prefer entry points, then shallower paths, then name."""
    entrypoint = 0 if path.name.lower() in _ENTRYPOINTS else 1
    depth = len(path.relative_to(root).parts)
    return (entrypoint, depth, str(path).lower())


def read_text(root: str | Path, rel_path: str, max_bytes: int = MAX_FILE_BYTES) -> str:
    """Read a file's text, tolerant of encoding issues and truncated to ``max_bytes``."""
    full = Path(root) / rel_path
    data = full.read_bytes()[:max_bytes]
    return data.decode("utf-8", errors="replace")

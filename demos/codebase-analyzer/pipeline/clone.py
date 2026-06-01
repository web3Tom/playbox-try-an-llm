"""Resolve an analysis target to a local directory — the [no model] entry stage.

Three modes:
  gitlab  - shallow-clone an internal GitLab repo into /tmp using GITLAB_PAT
  local   - analyse a directory already on disk (no copy, no clone)
  sample  - the tiny bundled sample repo (zero credentials, zero network)

Security: the PAT is injected into the clone URL only for the subprocess call
and is NEVER logged or printed. We log the host, never the credential.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

# The bundled sample lives next to this package.
SAMPLE_REPO = Path(__file__).resolve().parent.parent / "sample-repo"


@dataclass
class Target:
    path: Path           # local directory to analyse
    name: str            # display name
    cleanup: Path | None  # temp dir to delete when done (None for local/sample)


def resolve_sample() -> Target:
    """The bundled sample repo. Always available, needs nothing."""
    if not SAMPLE_REPO.is_dir():
        raise FileNotFoundError(f"bundled sample repo missing at {SAMPLE_REPO}")
    return Target(path=SAMPLE_REPO, name="sample-repo", cleanup=None)


def resolve_local(path: str) -> Target:
    """A directory already on disk. Validated, not copied."""
    p = Path(path).expanduser().resolve()
    if not p.is_dir():
        raise NotADirectoryError(f"not a directory: {p}")
    return Target(path=p, name=p.name, cleanup=None)


def resolve_gitlab(repo_url: str) -> Target:
    """Shallow-clone an internal GitLab repo into a fresh temp directory.

    Reads GITLAB_PAT from the environment and injects it into the URL for the
    clone only. Fails loud if the PAT is missing or the clone fails.
    """
    pat = os.getenv("GITLAB_PAT")
    if not pat:
        raise RuntimeError("GITLAB_PAT is not set — required to clone a private GitLab repo")

    parsed = urlparse(repo_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"expected an http(s) GitLab URL, got: {repo_url!r}")

    # Build an authenticated URL: https://oauth2:<pat>@host/path
    auth_netloc = f"oauth2:{pat}@{parsed.hostname}"
    if parsed.port:
        auth_netloc += f":{parsed.port}"
    auth_url = urlunparse(parsed._replace(netloc=auth_netloc))

    name = Path(parsed.path).stem or "repo"
    dest = Path(tempfile.mkdtemp(prefix="playbox-analyzer-")) / name

    logger.info("Cloning %s (host: %s) ...", name, parsed.hostname)  # host only, never the PAT
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", auth_url, str(dest)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        # Scrub the PAT from any error text before surfacing it.
        stderr = (exc.stderr or "").replace(pat, "***")
        shutil.rmtree(dest.parent, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {stderr.strip()}") from None

    return Target(path=dest, name=name, cleanup=dest.parent)


def cleanup(target: Target) -> None:
    """Remove the temp clone, if any. Safe to call for local/sample targets."""
    if target.cleanup is not None:
        shutil.rmtree(target.cleanup, ignore_errors=True)
        logger.info("Cleaned up temporary clone for %s", target.name)

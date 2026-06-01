"""Target resolution must validate inputs and fail loud when the PAT is missing
— we never want a half-configured clone to proceed silently.
"""

import pytest

from pipeline import clone


def test_resolve_local_rejects_non_directory(tmp_path):
    missing = tmp_path / "nope"
    with pytest.raises(NotADirectoryError):
        clone.resolve_local(str(missing))


def test_resolve_local_accepts_real_directory(tmp_path):
    target = clone.resolve_local(str(tmp_path))
    assert target.path == tmp_path.resolve()
    assert target.cleanup is None  # local dirs are never deleted


def test_resolve_gitlab_requires_pat(monkeypatch):
    monkeypatch.delenv("GITLAB_PAT", raising=False)
    with pytest.raises(RuntimeError, match="GITLAB_PAT"):
        clone.resolve_gitlab("https://gitlab.example/group/repo.git")


def test_resolve_gitlab_rejects_non_http_url(monkeypatch):
    monkeypatch.setenv("GITLAB_PAT", "dummy")
    with pytest.raises(ValueError):
        clone.resolve_gitlab("git@gitlab.example:group/repo.git")

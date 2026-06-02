"""The select stage triages files but must NEVER break the run or invent paths.

These tests pin the guardrails: it passes through when there's nothing to
triage, validates the model's choice against the real candidate list (no
hallucinated paths), backfills to use the whole budget, and falls back to the
deterministic pick on an empty response or an API error.
"""

from openai import OpenAIError

from pipeline.select import select_files


class _Resp:
    def __init__(self, text):
        self.output_text = text


class _Responses:
    def __init__(self, text, raise_exc=False):
        self._text = text
        self._raise = raise_exc

    def create(self, **_kwargs):
        if self._raise:
            raise OpenAIError("boom")
        return _Resp(self._text)


class _Client:
    def __init__(self, text="", raise_exc=False):
        self.responses = _Responses(text, raise_exc)


_CANDIDATES = ["app.py", "api/routes.py", "svc.py", "db.py", "util.py"]
_FALLBACK = ["app.py", "api/routes.py", "svc.py"]


def test_passthrough_when_nothing_to_triage():
    # candidates within budget -> return them as-is, no model call needed.
    out = select_files(_Client(), "desc", ["a.py", "b.py"], ["a.py", "b.py"], max_files=3)
    assert out == ["a.py", "b.py"]


def test_returns_validated_model_choice():
    client = _Client('{"files": ["svc.py", "app.py", "db.py"]}')
    out = select_files(client, "desc", _CANDIDATES, _FALLBACK, max_files=3)
    assert out == ["svc.py", "app.py", "db.py"]


def test_drops_hallucinated_paths_and_backfills():
    # Model returns one real + one invented path; result is filled from fallback.
    client = _Client('{"files": ["svc.py", "ghost.py"]}')
    out = select_files(client, "desc", _CANDIDATES, _FALLBACK, max_files=3)
    assert "ghost.py" not in out
    assert out[0] == "svc.py"          # model's valid pick kept first
    assert len(out) == 3               # backfilled to the budget
    assert set(out) <= set(_CANDIDATES)


def test_falls_back_on_empty_response():
    client = _Client('{"files": []}')
    out = select_files(client, "desc", _CANDIDATES, _FALLBACK, max_files=3)
    assert out == _FALLBACK


def test_falls_back_on_api_error():
    client = _Client(raise_exc=True)
    out = select_files(client, "desc", _CANDIDATES, _FALLBACK, max_files=3)
    assert out == _FALLBACK

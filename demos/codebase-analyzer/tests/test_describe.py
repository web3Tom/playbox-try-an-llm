"""When the README is uninformative, describe must infer a description from the
analyzed file summaries — and must degrade quietly (empty string) when there's
nothing to infer from or the call fails, so the run never breaks.
"""

from openai import OpenAIError

from pipeline.describe import synthesize_description
from pipeline.schema import Node


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


def _file(path, summary, tags=None):
    return Node(id=f"file:{path}", type="file", name=path, filePath=path, summary=summary, tags=tags or [])


def test_synthesizes_from_file_summaries():
    nodes = [
        _file("vault.py", "Authenticates to HashiCorp Vault", ["auth"]),
        _file("kube.py", "Manages Kubernetes contexts", ["ops"]),
    ]
    client = _Client('{"description":"Operational tooling for Vault auth and Kubernetes management."}')
    out = synthesize_description(client, "ripcord", ["Python"], nodes)
    assert "Vault" in out


def test_returns_empty_when_no_file_summaries():
    # No file nodes with summaries -> no model call, empty string.
    out = synthesize_description(_Client('{"description":"x"}'), "proj", [], [])
    assert out == ""


def test_ignores_member_nodes_without_summaries():
    nodes = [_file("a.py", ""), Node(id="function:a.py::f", type="function", name="f", filePath="a.py")]
    out = synthesize_description(_Client('{"description":"x"}'), "proj", ["Python"], nodes)
    assert out == ""          # nothing with a usable summary -> no call


def test_returns_empty_on_api_error():
    nodes = [_file("a.py", "does a thing")]
    out = synthesize_description(_Client(raise_exc=True), "proj", ["Python"], nodes)
    assert out == ""

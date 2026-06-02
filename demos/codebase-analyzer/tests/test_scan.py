"""scan_project must report WHETHER the README actually described the project,
so the pipeline knows when to fall back to inferring from code. An empty or
generic README must read as uninformative even if the model forgets the flag.
"""

from pipeline.scan import scan_project


class _Resp:
    def __init__(self, text):
        self.output_text = text


class _Responses:
    def __init__(self, text):
        self._text = text

    def create(self, **_kwargs):
        return _Resp(self._text)


class _Client:
    def __init__(self, text):
        self.responses = _Responses(text)


def test_no_context_is_uninformative_without_a_model_call(tmp_path):
    # No README/manifest at all -> ("", False), and the client is never consulted.
    desc, informative = scan_project(_Client('{"description":"x","informative":true}'), tmp_path, "proj")
    assert desc == ""
    assert informative is False


def test_informative_readme(tmp_path):
    (tmp_path / "README.md").write_text("A billing service written in Python.\n")
    desc, informative = scan_project(
        _Client('{"description":"A billing service.","informative":true}'), tmp_path, "proj"
    )
    assert desc == "A billing service."
    assert informative is True


def test_generic_template_readme_is_uninformative(tmp_path):
    (tmp_path / "README.md").write_text("Generic GitLab project template.\n")
    _desc, informative = scan_project(
        _Client('{"description":"A generic template.","informative":false}'), tmp_path, "proj"
    )
    assert informative is False


def test_empty_description_is_uninformative_even_if_flag_true(tmp_path):
    (tmp_path / "README.md").write_text("x\n")
    _desc, informative = scan_project(
        _Client('{"description":"","informative":true}'), tmp_path, "proj"
    )
    assert informative is False

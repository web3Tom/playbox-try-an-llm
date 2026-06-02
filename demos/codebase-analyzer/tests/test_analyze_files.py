"""The member graph is only useful if call/inherit edges resolve CORRECTLY.

These tests pin the resolution rules that turn model-supplied *names* into real
member->member edges: same-file matches win, unambiguous cross-file names
resolve, ambiguous ones are dropped (never guessed), inheritance is class-only,
and self-references are discarded. If these change silently, the graph quietly
grows wrong edges — so each test encodes the rule, not just the mechanics.
"""

from pipeline.analyze_files import _as_names, _member_edges, _member_nodes
from pipeline.schema import Node


def test_member_nodes_returns_node_raw_pairs_and_drops_malformed():
    raw = [
        {"name": "foo", "type": "function", "summary": "s", "complexity": "low"},
        {"name": "", "type": "function"},      # no name -> dropped
        {"name": "Bar", "type": "interface"},  # bad type -> dropped
        "not-a-dict",                          # dropped
    ]
    pairs = _member_nodes("app.py", raw)
    assert [n.name for n, _ in pairs] == ["foo"]
    node, original = pairs[0]
    assert node.id == "function:app.py::foo"
    assert node.complexity == "simple"          # "low" normalized
    assert original["type"] == "function"       # raw dict carried for edge pass


def _pair(path, name, mtype, calls=None, extends=None):
    raw = {"name": name, "type": mtype}
    if calls is not None:
        raw["calls"] = calls
    if extends is not None:
        raw["extends"] = extends
    node = Node(id=f"{mtype}:{path}::{name}", type=mtype, name=name, filePath=path)
    return node, raw


def test_member_edges_resolves_same_file_call():
    pairs = [
        _pair("a.py", "main", "function", calls=["helper"]),
        _pair("a.py", "helper", "function"),
    ]
    edges = _member_edges(pairs)
    assert any(
        e.source == "function:a.py::main"
        and e.target == "function:a.py::helper"
        and e.type == "calls"
        for e in edges
    )


def test_member_edges_resolves_unambiguous_cross_file_call():
    pairs = [
        _pair("a.py", "run", "function", calls=["Widget"]),
        _pair("b.py", "Widget", "class"),
    ]
    edges = _member_edges(pairs)
    assert any(e.target == "class:b.py::Widget" and e.type == "calls" for e in edges)


def test_member_edges_drops_ambiguous_cross_file_name():
    # 'save' lives in two files; a caller with no local 'save' can't disambiguate.
    pairs = [
        _pair("c.py", "do", "function", calls=["save"]),
        _pair("a.py", "save", "function"),
        _pair("b.py", "save", "function"),
    ]
    edges = _member_edges(pairs)
    assert all(e.target not in ("function:a.py::save", "function:b.py::save") for e in edges)


def test_member_edges_same_file_wins_over_ambiguous_global():
    pairs = [
        _pair("a.py", "caller", "function", calls=["save"]),
        _pair("a.py", "save", "function"),
        _pair("b.py", "save", "function"),
    ]
    edges = _member_edges(pairs)
    targets = [e.target for e in edges if e.source == "function:a.py::caller"]
    assert targets == ["function:a.py::save"]   # local match, not dropped as ambiguous


def test_member_edges_inherits_is_class_only():
    pairs = [
        _pair("a.py", "Base", "class"),
        _pair("a.py", "Child", "class", extends=["Base"]),
        _pair("a.py", "fn", "function", extends=["Base"]),  # functions never inherit
    ]
    inh = [e for e in _member_edges(pairs) if e.type == "inherits"]
    assert len(inh) == 1
    assert inh[0].source == "class:a.py::Child"
    assert inh[0].target == "class:a.py::Base"


def test_member_edges_drops_self_reference():
    pairs = [_pair("a.py", "rec", "function", calls=["rec"])]
    assert _member_edges(pairs) == []


def test_as_names_coerces_string_and_filters_junk():
    assert _as_names("foo") == ["foo"]
    assert _as_names(["a", "", "  b ", 3]) == ["a", "b", "3"]
    assert _as_names(None) == []
    assert _as_names({"x": 1}) == []

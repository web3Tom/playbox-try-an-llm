"""Schema validation must catch the failure modes an LLM actually produces:
invalid enums, duplicate ids, and edges that point at non-existent nodes.
"""

from pipeline.schema import Edge, KnowledgeGraph, Node, Project, normalize_complexity, validate


def test_normalize_complexity_maps_loose_labels():
    # Models say "high"/"medium"/"low"; the dashboard expects our canonical set.
    assert normalize_complexity("high") == "complex"
    assert normalize_complexity("MEDIUM") == "moderate"
    assert normalize_complexity("low") == "simple"


def test_normalize_complexity_defaults_moderate_not_crash():
    # A garbage label must degrade gracefully — it should never abort a run.
    assert normalize_complexity(None) == "moderate"
    assert normalize_complexity("wildly-unknown") == "moderate"


def _graph(nodes, edges):
    return KnowledgeGraph(project=Project(name="t"), nodes=nodes, edges=edges)


def test_validate_passes_for_consistent_graph():
    nodes = [Node(id="file:a", type="file", name="a", filePath="a")]
    assert validate(_graph(nodes, [])) == []


def test_validate_flags_dangling_edge():
    # The whole reason merge exists: an edge to a node we never produced is
    # invalid and would render a broken dashboard.
    nodes = [Node(id="file:a", type="file", name="a", filePath="a")]
    edges = [Edge(source="file:a", target="file:ghost", type="imports")]
    problems = validate(_graph(nodes, edges))
    assert any("ghost" in p for p in problems)


def test_validate_flags_bad_enums_and_duplicates():
    nodes = [
        Node(id="x", type="widget", name="x", filePath="x"),   # bad type
        Node(id="x", type="file", name="x", filePath="x"),     # duplicate id
    ]
    problems = validate(_graph(nodes, []))
    assert any("invalid type" in p for p in problems)
    assert any("duplicate node ids" in p for p in problems)

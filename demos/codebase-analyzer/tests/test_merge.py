"""Merge is the deterministic heart of the pipeline. It must dedup nodes,
dedup edges, and prune dangling/self edges — and report the prune count.
"""

from pipeline.merge import assemble, merge_edges, merge_nodes
from pipeline.schema import Edge, Node


def _node(nid, complexity="moderate"):
    return Node(id=nid, type="file", name=nid, filePath=nid, complexity=complexity)


def test_merge_nodes_dedups_by_id_and_normalizes_complexity():
    groups = [[_node("a", complexity="high")], [_node("a"), _node("b")]]
    nodes = merge_nodes(groups)
    ids = {n.id for n in nodes}
    assert ids == {"a", "b"}
    # First occurrence wins, and its loose "high" is normalized to "complex".
    a = next(n for n in nodes if n.id == "a")
    assert a.complexity == "complex"


def test_merge_edges_drops_dangling_and_counts_them():
    node_ids = {"a", "b"}
    groups = [[
        Edge(source="a", target="b", type="imports"),
        Edge(source="a", target="ghost", type="imports"),  # dangling
    ]]
    edges, dropped = merge_edges(groups, node_ids)
    assert len(edges) == 1
    assert dropped == 1


def test_merge_edges_drops_self_loops():
    edges, dropped = merge_edges([[Edge("a", "a", "calls")]], {"a"})
    assert edges == []
    assert dropped == 1


def test_merge_edges_dedups_identical_edges():
    groups = [[Edge("a", "b", "imports")], [Edge("a", "b", "imports")]]
    edges, _ = merge_edges(groups, {"a", "b"})
    assert len(edges) == 1


def test_assemble_end_to_end():
    node_groups = [[_node("a")], [_node("b"), _node("a")]]
    edge_groups = [[Edge("a", "b", "imports"), Edge("a", "x", "calls")]]
    nodes, edges = assemble(node_groups, edge_groups)
    assert {n.id for n in nodes} == {"a", "b"}
    assert len(edges) == 1  # the a->x edge was dangling and pruned

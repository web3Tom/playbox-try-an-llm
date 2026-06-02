"""The tour must never point a user at a file that isn't in the graph.

Two layers guard that: schema.validate() flags a tour step whose filePath is
unknown, and build_tour() drops such steps (with a log) before they ever reach
the graph. Both are tested because the dashboard turns each step into a clickable
link to a node — a dangling step is a dead link.
"""

from pipeline.schema import KnowledgeGraph, Node, Project, TourStep, validate
from pipeline.tour import build_tour


def _graph_with_tour(tour):
    return KnowledgeGraph(
        project=Project(name="t"),
        nodes=[Node(id="file:a", type="file", name="a", filePath="a")],
        tour=tour,
    )


def test_validate_flags_tour_step_with_unknown_file():
    problems = validate(_graph_with_tour([TourStep(order=1, title="x", filePath="ghost.py", explanation="")]))
    assert any("tour step 1" in p and "ghost.py" in p for p in problems)


def test_validate_accepts_tour_step_with_known_file():
    assert validate(_graph_with_tour([TourStep(order=1, title="x", filePath="a", explanation="")])) == []


class _FakeResp:
    def __init__(self, text):
        self.output_text = text


class _FakeResponses:
    def __init__(self, text):
        self._text = text

    def create(self, **_kwargs):
        return _FakeResp(self._text)


class _FakeClient:
    """Stands in for AzureOpenAI — returns a canned Responses payload."""
    def __init__(self, text):
        self.responses = _FakeResponses(text)


def test_build_tour_drops_steps_referencing_unknown_files_and_reorders():
    nodes = [Node(id="file:a.py", type="file", name="a.py", filePath="a.py")]
    payload = (
        '{"steps": ['
        '{"title": "Start", "filePath": "a.py", "explanation": "e"},'
        '{"title": "Ghost", "filePath": "zzz.py", "explanation": "e"}'
        ']}'
    )
    steps = build_tour(_FakeClient(payload), "desc", nodes)
    assert len(steps) == 1
    assert steps[0].filePath == "a.py"
    assert steps[0].order == 1          # order is re-derived after the drop

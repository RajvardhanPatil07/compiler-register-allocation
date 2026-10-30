import networkx as nx
from allocator import parse_program, analyze_liveness, build_interference_graph

def graph_for(text):
    instructions = parse_program(text)
    return build_interference_graph(instructions, *analyze_liveness(instructions))

def test_reuse_example_has_only_required_conflicts():
    graph = graph_for("a=1\nb=a\nc=a+b\nd=a+c")
    assert set(graph) == {"a", "b", "c", "d"}
    assert {frozenset(edge) for edge in graph.edges()} == {frozenset(("a", "b")), frozenset(("a", "c"))}
    assert graph.degree("d") == 0
    assert list(nx.selfloop_edges(graph)) == []

def test_external_inputs_conflict_when_read_together():
    graph = graph_for("result=left+right")
    assert graph.has_edge("left", "right")
    assert graph.degree("result") == 0

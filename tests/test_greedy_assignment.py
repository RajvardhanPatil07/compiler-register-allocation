import networkx as nx
from allocator import color_graph
from graph_tools import check_coloring, compare_strategies

def test_complete_graph_requires_one_register_per_vertex():
    graph = nx.complete_graph(["d", "b", "a", "c"])
    steps = []
    coloring = color_graph(graph, steps)
    assert coloring == {"a": 0, "b": 1, "c": 2, "d": 3}
    assert check_coloring(graph, coloring)["valid"]
    assert steps[-1]["coloring"] == coloring
    coloring["a"] = 99
    assert steps[0]["coloring"] == {"a": 0}

def test_bipartite_star_reuses_leaf_registers():
    graph = nx.Graph([("a", "b"), ("a", "c"), ("a", "d")])
    assert color_graph(graph) == {"a": 0, "b": 1, "c": 1, "d": 1}
    assert all(row["Registers"] == 2 for row in compare_strategies(graph))

def test_invalid_assignments_report_missing_invalid_and_conflicting_values():
    graph = nx.Graph([("a", "b")])
    assert check_coloring(graph, {"a": 0})["missing"] == ["b"]
    assert check_coloring(graph, {"a": True, "b": -1})["invalid"] == ["a", "b"]
    assert check_coloring(graph, {"a": 0, "b": 0})["conflicts"] == [("a", "b")]

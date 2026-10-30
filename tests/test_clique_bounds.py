import networkx as nx
from graph_tools import largest_clique

def test_largest_clique_is_a_lower_bound_not_a_coloring_proof():
    graph = nx.cycle_graph(["a", "b", "c", "d", "e"])
    clique = largest_clique(graph)
    assert len(clique) == 2
    assert graph.has_edge(*clique)
    assert len(set(nx.coloring.greedy_color(graph, strategy="DSATUR").values())) == 3

def test_complete_and_empty_graph_cliques():
    assert largest_clique(nx.complete_graph(["c", "a", "b"])) == ["a", "b", "c"]
    assert largest_clique(nx.Graph()) == []

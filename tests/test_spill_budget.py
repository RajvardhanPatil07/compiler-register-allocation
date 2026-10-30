import networkx as nx
import pytest
from graph_tools import allocate_with_spilling, check_coloring

def test_triangle_spills_alphabetical_tie_without_mutating_input():
    graph = nx.complete_graph(["c", "b", "a"])
    result = allocate_with_spilling(graph, 2)
    assert result["spilled"] == ["a"]
    assert set(graph) == {"a", "b", "c"} and graph.number_of_edges() == 3
    assert set(result["graph"]) == {"b", "c"}
    assert len(set(result["coloring"].values())) <= 2
    assert check_coloring(result["graph"], result["coloring"])["valid"]

def test_sufficient_budget_does_not_spill():
    assert allocate_with_spilling(nx.path_graph(["a", "b", "c"]), 2)["spilled"] == []

@pytest.mark.parametrize("budget", [0, -1, True, 1.5, "2"])
def test_invalid_budget_is_rejected(budget):
    with pytest.raises(ValueError):
        allocate_with_spilling(nx.Graph(), budget)

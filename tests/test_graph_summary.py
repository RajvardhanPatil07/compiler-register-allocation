import networkx as nx
from graph_tools import graph_details, adjacency_rows

def test_disconnected_graph_preserves_isolates_and_handshake_identity():
    graph = nx.Graph([("a", "b"), ("b", "c")])
    graph.add_node("z")
    details = graph_details(graph)
    assert details["degree_sequence"] == [2, 1, 1, 0]
    assert details["degree_sum"] == details["twice_edges"] == 4
    assert {frozenset(c) for c in details["components"]} == {frozenset("abc"), frozenset("z")}
    rows = adjacency_rows(graph)
    assert [r["Variable"] for r in rows] == ["a", "b", "c", "z"]
    assert rows[0]["To b"] == rows[1]["To a"] == 1
    assert all(row[f"To {row['Variable']}"] == 0 for row in rows)
    assert all(rows[3][f"To {name}"] == 0 for name in graph)

"""Graph statistics used by the Discrete Mathematics laboratory."""

import networkx as nx
import pandas as pd


def degree_table(graph: nx.Graph) -> pd.DataFrame:
    # DM concept: degree counts the edges incident to each vertex.
    rows = [{"Variable": node, "Degree": degree} for node, degree in graph.degree()]
    rows.sort(key=lambda row: (-row["Degree"], row["Variable"]))
    return pd.DataFrame(rows, columns=["Variable", "Degree"])


def degree_sequence(graph: nx.Graph) -> list[int]:
    # DM concept: the degree sequence lists vertex degrees in descending order.
    return sorted((degree for _, degree in graph.degree()), reverse=True)


def check_handshake_lemma(graph: nx.Graph) -> dict:
    # DM concept: the handshake lemma says the degree sum equals twice the edge count.
    degree_sum = sum(degree for _, degree in graph.degree())
    twice_edges = 2 * graph.number_of_edges()
    return {"degree_sum": degree_sum, "twice_edges": twice_edges, "holds": degree_sum == twice_edges}


def adjacency_matrix(graph: nx.Graph) -> pd.DataFrame:
    # DM concept: an adjacency matrix records 1 for an edge and 0 for no edge.
    vertices = sorted(graph.nodes())
    values = nx.to_numpy_array(graph, nodelist=vertices, dtype=int)
    return pd.DataFrame(values, index=vertices, columns=vertices)


def connected_components(graph: nx.Graph) -> list[list[str]]:
    # DM concept: a connected component is a maximal group joined by paths.
    components = [sorted(component) for component in nx.connected_components(graph)]
    return sorted(components, key=lambda component: component[0] if component else "")

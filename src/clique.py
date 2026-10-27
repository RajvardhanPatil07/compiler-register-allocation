"""Clique utilities for register-allocation lower bounds."""

import networkx as nx


def maximum_clique(graph: nx.Graph) -> tuple[list[str], int]:
    # DM concept: every vertex in a clique is adjacent to every other vertex.
    if graph.number_of_nodes() == 0:
        return [], 0
    cliques = (sorted(clique) for clique in nx.find_cliques(graph))
    largest = max(cliques, key=lambda clique: (len(clique), clique))
    return largest, len(largest)

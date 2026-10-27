"""Validation helpers for graph colorings."""

import networkx as nx


def check_coloring_validity(graph: nx.Graph, coloring: dict) -> dict:
    # DM concept: a proper coloring assigns different colors to every edge's endpoints.
    bad_edges = []
    for left, right in graph.edges():
        if left not in coloring or right not in coloring:
            bad_edges.append((left, right))
        elif coloring[left] == coloring[right]:
            bad_edges.append((left, right))
    return {"valid": len(bad_edges) == 0, "bad_edges": sorted(bad_edges)}

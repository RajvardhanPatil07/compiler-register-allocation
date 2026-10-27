"""Validation helpers for graph colorings."""

import networkx as nx


def check_coloring_validity(graph: nx.Graph, coloring: dict) -> dict:
    # DM concept: a proper coloring assigns every vertex a color and separates edge endpoints.
    missing_vertices = sorted(set(graph.nodes()) - set(coloring))
    bad_edges = []
    for left, right in graph.edges():
        if left not in coloring or right not in coloring:
            bad_edges.append((left, right))
        elif coloring[left] == coloring[right]:
            bad_edges.append((left, right))
    valid = not bad_edges and not missing_vertices
    return {
        "valid": valid,
        "bad_edges": sorted(bad_edges),
        "missing_vertices": missing_vertices,
    }

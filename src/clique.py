"""Clique utilities for register-allocation lower bounds."""

import networkx as nx


def maximum_clique(graph: nx.Graph) -> tuple[list[str], int]:
    # DM concept: every vertex in a clique is adjacent to every other vertex.
    if graph.number_of_nodes() == 0:
        return [], 0
    cliques = (sorted(clique) for clique in nx.find_cliques(graph))
    largest = max(cliques, key=lambda clique: (len(clique), clique))
    return largest, len(largest)


def explain_pigeonhole(graph: nx.Graph, register_count: int) -> dict:
    # DM concept: a clique larger than the register set forces two variables to share a color.
    vertices, size = maximum_clique(graph)
    impossible = size > register_count
    if impossible:
        message = (
            f"These {size} variables all interfere with each other, but only "
            f"{register_count} registers exist. By the pigeonhole principle, "
            "two of them must share a register, which is not allowed. "
            "So allocation without spilling is impossible."
        )
    else:
        message = (
            f"The available register budget ({register_count}) meets the clique "
            f"lower bound ({size}). This lower bound alone does not prove that "
            "the complete graph fits the budget."
        )
    return {
        "clique": vertices,
        "clique_size": size,
        "register_count": register_count,
        "impossible": impossible,
        "message": message,
    }

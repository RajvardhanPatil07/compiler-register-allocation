"""Readable CNF clauses for the graph k-coloring problem."""

from itertools import combinations
import networkx as nx


def _proposition(vertex: str, color: int) -> str:
    # DM concept: x(v, c) is a proposition that vertex v receives color c.
    return f"x({vertex},{color})"


def generate_coloring_cnf(graph: nx.Graph, color_count: int,
                          display_limit: int = 50) -> dict:
    # DM concept: CNF expresses coloring constraints as an AND of OR-clauses.
    if color_count < 1:
        raise ValueError("CNF coloring needs at least one available color.")
    clauses = []
    vertices = sorted(graph.nodes())
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    counts = {
        "At-least-one": len(vertices),
        "At-most-one": len(vertices) * color_count * (color_count - 1) // 2,
        "Adjacent-different": len(edges) * color_count,
    }
    for vertex in vertices:
        literals = [_proposition(vertex, color) for color in range(1, color_count + 1)]
        clauses.append({"Group": "At-least-one", "Clause": " OR ".join(literals)})
        if len(clauses) >= display_limit:
            break
    if len(clauses) < display_limit:
        for vertex in vertices:
            for first, second in combinations(range(1, color_count + 1), 2):
                clause = f"NOT {_proposition(vertex, first)} OR NOT {_proposition(vertex, second)}"
                clauses.append({"Group": "At-most-one", "Clause": clause})
                if len(clauses) >= display_limit:
                    break
            if len(clauses) >= display_limit:
                break
    if len(clauses) < display_limit:
        for left, right in edges:
            for color in range(1, color_count + 1):
                clause = f"NOT {_proposition(left, color)} OR NOT {_proposition(right, color)}"
                clauses.append({"Group": "Adjacent-different", "Clause": clause})
                if len(clauses) >= display_limit:
                    break
            if len(clauses) >= display_limit:
                break
    total = sum(counts.values())
    return {
        "clauses": clauses,
        "counts": [
            {"Clause group": name, "Total clauses": amount}
            for name, amount in counts.items()
        ],
        "total_clauses": total,
        "truncated": total > display_limit,
        "display_limit": display_limit,
    }

"""Coloring comparisons and bounded exact coloring for small graphs."""

from typing import Dict, List, Optional, Tuple
import networkx as nx


def coloring_count(coloring: Dict[str, int]) -> int:
    # DM concept: the number of distinct colors is the number of color classes.
    return len(set(coloring.values()))


def compare_coloring_strategies(graph: nx.Graph) -> List[dict]:
    # DM concept: greedy strategies choose colors by different vertex orderings.
    strategies = [
        ("largest_first", "Greedy largest_first"),
        ("smallest_last", "Greedy smallest_last"),
        ("DSATUR", "Greedy DSATUR"),
    ]
    results = []
    for strategy, label in strategies:
        colors = nx.coloring.greedy_color(graph, strategy=strategy)
        assignment = ", ".join(
            f"{node}: R{colors[node] + 1}" for node in sorted(colors)
        ) or "No variables"
        results.append({
            "Strategy": label,
            "Colors Used": coloring_count(colors),
            "Assignment": assignment,
            "Coloring": colors,
        })
    return results


def _assign_vertex(graph: nx.Graph, vertices: List[str], color_limit: int,
                   position: int, assignment: Dict[str, int]) -> bool:
    # DM concept: backtracking tries a color, then undoes it if a conflict appears.
    if position == len(vertices):
        return True
    vertex = vertices[position]
    neighbor_colors = {assignment[neighbor] for neighbor in graph.neighbors(vertex)
                       if neighbor in assignment}
    for color in range(color_limit):
        if color in neighbor_colors:
            continue
        assignment[vertex] = color
        if _assign_vertex(graph, vertices, color_limit, position + 1, assignment):
            return True
        del assignment[vertex]
    return False


def exact_coloring(graph: nx.Graph, size_limit: int = 12) -> Tuple[Optional[int], Dict[str, int]]:
    # DM concept: the chromatic number is the smallest color count for a proper coloring.
    vertex_count = graph.number_of_nodes()
    if vertex_count > size_limit:
        return None, {}
    if vertex_count == 0:
        return 0, {}
    vertices = sorted(graph.nodes(), key=lambda node: (-graph.degree(node), node))
    for color_limit in range(1, vertex_count + 1):
        assignment = {}
        if _assign_vertex(graph, vertices, color_limit, 0, assignment):
            return color_limit, assignment.copy()
    return vertex_count, {vertex: index for index, vertex in enumerate(vertices)}


def coloring_steps(graph: nx.Graph) -> List[dict]:
    # DM concept: a proper coloring gives each vertex a color unused by its neighbors.
    vertices = sorted(graph.nodes(), key=lambda node: (-graph.degree(node), node))
    assignment = {}
    steps = []
    for vertex in vertices:
        neighbor_colors = sorted({assignment[neighbor] for neighbor in graph.neighbors(vertex)
                                  if neighbor in assignment})
        color = 0
        while color in neighbor_colors:
            color += 1
        assignment[vertex] = color
        steps.append({
            "vertex": vertex,
            "neighbor_colors": neighbor_colors,
            "color": color,
            "partial_coloring": assignment.copy(),
        })
    return steps

"""Simple greedy graph coloring for register assignment."""

from typing import Dict
import networkx as nx


def color_graph(graph: nx.Graph) -> Dict[str, int]:
    # DM concept: greedy coloring assigns different colors to adjacent vertices.
    return nx.coloring.greedy_color(graph, strategy="largest_first")


def coloring_count(coloring: Dict[str, int]) -> int:
    # DM concept: each distinct color represents one register class.
    return max(coloring.values()) + 1 if coloring else 0

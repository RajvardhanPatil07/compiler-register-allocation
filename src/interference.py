"""Construction and basic analysis of the interference graph."""

from itertools import combinations
from typing import List, Set
import networkx as nx
from .parser import Instruction


def build_interference_graph(instructions: List[Instruction], live_in: List[Set[str]], live_out: List[Set[str]]) -> nx.Graph:
    # DM concept: an undirected edge joins variables that cannot share a register.
    graph = nx.Graph()
    variables = set()
    for instruction in instructions:
        variables.update(instruction.use)
        variables.update(instruction.define)
    graph.add_nodes_from(sorted(variables))

    for i, instruction in enumerate(instructions):
        defined = next(iter(instruction.define))
        for variable in live_out[i]:
            if variable != defined:
                graph.add_edge(defined, variable)
        for left, right in combinations(sorted(live_in[i]), 2):
            graph.add_edge(left, right)
    return graph


def graph_statistics(graph: nx.Graph) -> dict:
    # DM concept: vertex, edge and degree counts summarize a graph's structure.
    degrees = dict(graph.degree())
    return {
        "vertices": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "max_degree": max(degrees.values()) if degrees else 0,
        "connected_components": nx.number_connected_components(graph) if graph.number_of_nodes() else 0,
        "degrees": degrees,
    }

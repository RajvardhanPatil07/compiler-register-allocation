"""Simple degree-based register spilling and program rewriting."""

import re
import networkx as nx

from src.coloring import color_graph, coloring_count
from src.parser import Instruction


def select_spill_candidate(graph: nx.Graph) -> str | None:
    # DM concept: vertex degree counts conflicts, so the largest-degree vertex is chosen first.
    if graph.number_of_nodes() == 0:
        return None
    degrees = dict(graph.degree())
    highest_degree = max(degrees.values())
    candidates = [vertex for vertex, degree in degrees.items() if degree == highest_degree]
    return sorted(candidates)[0]


def allocate_with_spilling(graph: nx.Graph, register_count: int) -> dict:
    # DM concept: remove a conflicting vertex until the remaining graph fits the color budget.
    if register_count < 1:
        raise ValueError("The register count must be at least one.")
    remaining = graph.copy()
    spilled = []
    while True:
        coloring = color_graph(remaining)
        used_colors = coloring_count(coloring)
        if used_colors <= register_count:
            return {
                "spilled": spilled,
                "coloring": coloring,
                "registers_used": used_colors,
                "graph": remaining.copy(),
            }
        candidate = select_spill_candidate(remaining)
        if candidate is None:
            return {"spilled": spilled, "coloring": {}, "registers_used": 0, "graph": remaining}
        spilled.append(candidate)
        remaining.remove_node(candidate)


def rewrite_program_with_registers(instructions: list[Instruction],
                                   coloring: dict, spilled: list[str]) -> list[str]:
    # DM concept: variable names are replaced by their color/register or a memory marker.
    rewritten = []
    spilled_set = set(spilled)
    variable_pattern = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for instruction in instructions:
        pieces = []
        position = 0
        for match in variable_pattern.finditer(instruction.text):
            pieces.append(instruction.text[position:match.start()])
            variable = match.group()
            if variable in spilled_set:
                pieces.append(f"MEM[{variable}]")
            elif variable in coloring:
                pieces.append(f"R{coloring[variable] + 1}")
            else:
                pieces.append(variable)
            position = match.end()
        pieces.append(instruction.text[position:])
        rewritten.append("".join(pieces))
    return rewritten

"""The four steps of register allocation: parse, liveness, graph, coloring."""

import re
from dataclasses import dataclass
from itertools import combinations

import networkx as nx


MAX_TEXT_LENGTH = 10000
MAX_INSTRUCTIONS = 100
MAX_VARIABLES = 40
MAX_NAME_LENGTH = 32


@dataclass
class Instruction:
    """A record of one source line and the variables it reads and writes."""

    number: int
    text: str
    use: set[str]
    define: set[str]


def is_variable(value):
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) is not None


def is_value(value):
    is_number = re.fullmatch(r"\d+(\.\d+)?", value) is not None
    return is_variable(value) or is_number


def parse_program(program):
    """Accept copies, constants, or one binary operation per assignment."""
    if len(program) > MAX_TEXT_LENGTH:
        raise ValueError(f"Use at most {MAX_TEXT_LENGTH} characters in the program.")
    instructions = []
    program_variables = set()
    for number, line in enumerate(program.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        if text.count("=") != 1:
            raise ValueError(f"Line {number}: use one '=' in each assignment.")

        destination, expression = text.split("=")
        destination = destination.strip()
        if not is_variable(destination):
            raise ValueError(f"Line {number}: invalid variable name '{destination}'.")

        # Keep the operator so a copy and a two-value expression stay distinct.
        parts = re.split(r"([+\-*/%])", expression)
        parts = [part.strip() for part in parts]
        values = parts[::2]
        if len(parts) not in (1, 3) or not all(is_value(value) for value in values):
            raise ValueError(f"Line {number}: use x = a or x = a + b. Operators: + - * / %.")

        used = set()
        for value in values:
            if is_variable(value):
                used.add(value)
        for variable in used.union({destination}):
            if len(variable) > MAX_NAME_LENGTH:
                raise ValueError(f"Line {number}: keep variable names within {MAX_NAME_LENGTH} characters.")
        program_variables.update(used.union({destination}))
        if len(program_variables) > MAX_VARIABLES:
            raise ValueError(f"Use at most {MAX_VARIABLES} variables in this small teaching project.")
        instructions.append(Instruction(number, text, used, {destination}))
        if len(instructions) > MAX_INSTRUCTIONS:
            raise ValueError(f"Use at most {MAX_INSTRUCTIONS} instructions in this small teaching project.")

    if not instructions:
        raise ValueError("Enter at least one assignment.")

    first_definition = {}
    for instruction in instructions:
        for variable in instruction.define:
            if variable not in first_definition:
                first_definition[variable] = instruction.number
    for instruction in instructions:
        for variable in sorted(instruction.use):
            # Names never assigned in the program represent external inputs.
            first_line = first_definition.get(variable)
            if first_line is not None and first_line >= instruction.number:
                raise ValueError(f"Line {instruction.number}: '{variable}' is used before its definition.")
    return instructions


def analyze_liveness(instructions):
    """Work backward to find the values needed before and after each line."""
    live_in = [set() for instruction in instructions]
    live_out = [set() for instruction in instructions]

    for index in reversed(range(len(instructions))):
        instruction = instructions[index]
        if index < len(instructions) - 1:
            live_out[index] = live_in[index + 1].copy()

        # The new value replaces the old one. Values read on this line are still needed.
        still_needed = live_out[index].difference(instruction.define)
        live_in[index] = instruction.use.union(still_needed)

    return live_in, live_out


def build_interference_graph(instructions, live_in, live_out):
    """An edge joins variables that need different registers in this model."""
    graph = nx.Graph()
    for instruction in instructions:
        graph.add_nodes_from(sorted(instruction.use.union(instruction.define)))

    for index, instruction in enumerate(instructions):
        for first, second in combinations(sorted(live_in[index]), 2):
            graph.add_edge(first, second)

        # A new value must coexist with the other values needed after this line.
        for destination in instruction.define:
            for variable in live_out[index]:
                if destination != variable:
                    graph.add_edge(destination, variable)
    return graph


def color_graph(graph, steps=None):
    """Greedily assign the first free color, visiting names alphabetically."""
    coloring = {}
    for variable in sorted(graph.nodes()):
        neighbor_colors = set()
        for neighbor in graph.neighbors(variable):
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])

        color = 0
        while color in neighbor_colors:
            color += 1
        coloring[variable] = color
        if steps is not None:
            steps.append({
                "variable": variable,
                "neighbor_colors": sorted(neighbor_colors),
                "color": color,
                "coloring": coloring.copy(),
            })
    return coloring

"""Small demonstrations built on the four main functions in allocator.py."""

import re

import networkx as nx

from allocator import color_graph


def graph_details(graph):
    degrees = []
    for variable in sorted(graph.nodes()):
        degrees.append({"Variable": variable, "Degree": graph.degree(variable)})
    components = []
    for component in nx.connected_components(graph):
        components.append(sorted(component))
    degree_values = [row["Degree"] for row in degrees]
    return {
        "degrees": degrees,
        "degree_sequence": sorted(degree_values, reverse=True),
        "degree_sum": sum(degree_values),
        "twice_edges": 2 * graph.number_of_edges(),
        "components": components,
    }


def adjacency_rows(graph):
    rows = []
    for first in sorted(graph.nodes()):
        row = {"Variable": first}
        for second in sorted(graph.nodes()):
            row[f"To {second}"] = int(graph.has_edge(first, second))
        rows.append(row)
    return rows


def live_ranges(instructions, live_in, live_out):
    """Summarize each variable's span; gaps and separate definitions are merged."""
    points = {}
    for index, instruction in enumerate(instructions):
        variables = instruction.use.union(instruction.define, live_in[index], live_out[index])
        for variable in variables:
            if variable not in points:
                points[variable] = []
            points[variable].append(instruction.number)
    rows = []
    for variable in sorted(points):
        rows.append({"Variable": variable, "Start": min(points[variable]), "End": max(points[variable])})
    return rows


def compare_strategies(graph):
    results = []
    alphabetical = color_graph(graph)
    results.append({"Strategy": "Alphabetical (our code)", "Registers": len(set(alphabetical.values()))})
    for strategy in ["largest_first", "smallest_last", "DSATUR"]:
        coloring = nx.coloring.greedy_color(graph, strategy=strategy)
        results.append({"Strategy": strategy, "Registers": len(set(coloring.values()))})
    return results


def check_coloring(graph, coloring):
    missing = []
    invalid = []
    conflicts = []
    for variable in graph.nodes():
        if variable not in coloring:
            missing.append(variable)
        elif type(coloring[variable]) is not int or coloring[variable] < 0:
            invalid.append(variable)
    for first, second in graph.edges():
        if first in coloring and second in coloring and coloring[first] == coloring[second]:
            conflicts.append((first, second))
    return {
        "valid": not missing and not invalid and not conflicts,
        "missing": missing, "invalid": invalid, "conflicts": conflicts,
    }


def largest_clique(graph):
    """Enumerate maximal cliques and keep a largest one. Intended for small graphs."""
    largest = []
    for clique in nx.find_cliques(graph):
        if len(clique) > len(largest):
            largest = sorted(clique)
    return largest


def allocate_with_spilling(graph, budget):
    """Remove a highest-degree variable until our greedy assignment fits."""
    if type(budget) is not int or budget < 1:
        raise ValueError("Use a whole number of registers, starting at 1.")
    remaining = graph.copy()
    spilled = []
    coloring = color_graph(remaining)
    while len(set(coloring.values())) > budget:
        variables = sorted(remaining.nodes())
        candidate = variables[0]
        for variable in variables:
            if remaining.degree(variable) > remaining.degree(candidate):
                candidate = variable
        spilled.append(candidate)
        remaining.remove_node(candidate)
        coloring = color_graph(remaining)
    return {"graph": remaining, "coloring": coloring, "spilled": spilled}


def rewrite_program(instructions, coloring, spilled):
    """Replace whole names, so replacing a never changes a name such as total."""
    locations = {}
    for variable, color in coloring.items():
        locations[variable] = f"R{color + 1}"
    for variable in spilled:
        locations[variable] = f"MEM[{variable}]"

    def storage_name(match):
        variable = match.group()
        if variable not in locations:
            raise ValueError(f"No register or memory slot was given to '{variable}'.")
        return locations[variable]

    lines = []
    for instruction in instructions:
        lines.append(re.sub(r"[A-Za-z_][A-Za-z0-9_]*", storage_name, instruction.text))
    return lines

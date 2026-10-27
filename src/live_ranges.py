"""Live-range data for a straight-line instruction sequence."""

from typing import List, Set
from .parser import Instruction


def build_live_ranges(instructions: List[Instruction], live_in: List[Set[str]],
                      live_out: List[Set[str]]) -> List[dict]:
    # DM concept: a live range is an interval from a variable's start to its last live point.
    variables = set()
    for instruction in instructions:
        variables.update(instruction.use)
        variables.update(instruction.define)
    rows = []
    for variable in sorted(variables):
        definitions = [item.number for item in instructions if variable in item.define]
        occurrences = [
            item.number for item in instructions
            if variable in item.use or variable in item.define
        ]
        start = definitions[0] if definitions else occurrences[0]
        live_points = []
        for index, item in enumerate(instructions):
            if variable in live_in[index] or variable in live_out[index]:
                live_points.append(item.number)
        end = max(live_points) if live_points else start
        rows.append({
            "Variable": variable,
            "Start": start,
            "End": max(start, end),
            "Start reason": "Definition" if definitions else "Input use",
        })
    return rows

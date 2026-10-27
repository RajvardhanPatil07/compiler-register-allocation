"""Backward liveness analysis for a linear instruction sequence."""

from typing import List, Set, Tuple
from .parser import Instruction


def analyze_liveness(instructions: List[Instruction]) -> Tuple[List[Set[str]], List[Set[str]]]:
    # DM concept: LIVE-IN = USE union (LIVE-OUT minus DEF), computed backwards.
    count = len(instructions)
    live_in = [set() for _ in range(count)]
    live_out = [set() for _ in range(count)]
    for index in range(count - 1, -1, -1):
        if index < count - 1:
            live_out[index] = live_in[index + 1].copy()
        live_in[index] = instructions[index].use | (live_out[index] - instructions[index].define)
    return live_in, live_out


def _format_set(values: Set[str]) -> str:
    # DM concept: set notation shows the members used by each liveness equation.
    return "{" + ", ".join(sorted(values)) + "}"


def liveness_equation(use: Set[str], live_out: Set[str], define: Set[str], live_in: Set[str]) -> str:
    # DM concept: union combines USE with LIVE-OUT values not removed by DEF.
    use_text = _format_set(use)
    out_text = _format_set(live_out)
    define_text = _format_set(define)
    in_text = _format_set(live_in)
    return f"LIVE-IN = USE ∪ (LIVE-OUT − DEF) = {use_text} ∪ ({out_text} − {define_text}) = {in_text}"

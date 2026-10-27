"""Parser and input-order checks for simplified three-address code."""

import re
from dataclasses import dataclass
from typing import List, Set


@dataclass
class Instruction:
    number: int
    text: str
    use: Set[str]
    define: Set[str]


VARIABLE = r"[A-Za-z_][A-Za-z0-9_]*"
NUMBER = r"\d+(?:\.\d+)?"
VALUE = rf"(?:{VARIABLE}|{NUMBER})"
RIGHT_HAND_SIDE = re.compile(
    rf"^\s*{VALUE}(?:\s*[+\-*/%]\s*{VALUE})?\s*$"
)


def parse_line(line: str, number: int) -> Instruction:
    # DM concept: USE and DEF are sets of variables read and written by one instruction.
    text = line.strip()
    if not text:
        raise ValueError(f"Line {number}: empty line is not an instruction.")
    if text.count("=") != 1:
        raise ValueError(f"Line {number}: expected one assignment operator '='.")
    left, right = text.split("=", 1)
    left, right = left.strip(), right.strip()
    if not re.fullmatch(VARIABLE, left):
        raise ValueError(f"Line {number}: invalid destination variable '{left}'.")
    if not RIGHT_HAND_SIDE.fullmatch(right):
        raise ValueError(
            f"Line {number}: unsupported symbol or expression. Use x = a or x = a + b "
            "with one operator from +, -, *, /, %."
        )
    use = set(re.findall(VARIABLE, right))
    return Instruction(number, text, use, {left})


def _check_use_before_definition(instructions: List[Instruction]) -> None:
    # DM concept: a variable must be defined before a later-defined value is first used.
    first_definition = {}
    for instruction in instructions:
        for variable in instruction.define:
            if variable not in first_definition:
                first_definition[variable] = instruction.number
    for instruction in instructions:
        for variable in sorted(instruction.use):
            definition_line = first_definition.get(variable)
            if definition_line is not None and definition_line > instruction.number:
                raise ValueError(
                    f"Line {instruction.number}: variable '{variable}' is used before it is "
                    f"defined on line {definition_line}."
                )


def parse_program(program: str) -> List[Instruction]:
    # DM concept: a program is a finite, ordered set of numbered instructions.
    instructions = []
    for line_number, line in enumerate(program.splitlines(), start=1):
        if line.strip():
            instructions.append(parse_line(line, line_number))
    if not instructions:
        raise ValueError("Line 1: input is empty. Enter at least one assignment.")
    _check_use_before_definition(instructions)
    return instructions

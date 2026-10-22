"""Parser for simplified three-address-code input."""

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
    text = line.strip()
    if not text:
        raise ValueError("Empty instruction.")
    if text.count("=") != 1:
        raise ValueError(f"Line {number}: expected one assignment operator '='.")

    left, right = text.split("=", 1)
    left = left.strip()
    right = right.strip()

    if not re.fullmatch(VARIABLE, left):
        raise ValueError(f"Line {number}: invalid destination variable '{left}'.")
    if not RIGHT_HAND_SIDE.fullmatch(right):
        raise ValueError(
            f"Line {number}: use a variable or number, optionally followed "
            "by one operator (+, -, *, /, %) and another variable or number."
        )

    tokens = re.findall(VARIABLE, right)
    use = set(tokens)

    # Keep the destination in USE when it appears on the right side,
    # as in "value = value + 1".
    return Instruction(number, text, use, {left})


def parse_program(program: str) -> List[Instruction]:
    instructions = []
    for line in program.splitlines():
        if line.strip():
            instructions.append(parse_line(line, len(instructions) + 1))
    if not instructions:
        raise ValueError("Please enter at least one instruction.")
    return instructions

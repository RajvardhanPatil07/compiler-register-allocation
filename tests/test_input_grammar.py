import pytest
from allocator import parse_program

@pytest.mark.parametrize("operator", ["+", "-", "*", "/", "%"])
def test_binary_operators_accept_external_inputs(operator):
    instruction = parse_program(f"result=left{operator}right")[0]
    assert instruction.use == {"left", "right"}
    assert instruction.define == {"result"}

@pytest.mark.parametrize("text", ["", "a = -1", "a = b + c + d", "1a = 2", "a == 1", "a = b\nb = 1", "a = a + 1"])
def test_invalid_or_uninitialized_programs_fail(text):
    with pytest.raises(ValueError):
        parse_program(text)

def test_blank_lines_keep_source_numbers_and_constants_are_not_variables():
    instructions = parse_program("\na = 1.5\n\nb = a")
    assert [i.number for i in instructions] == [2, 4]
    assert instructions[0].use == set()
    assert instructions[1].use == {"a"}

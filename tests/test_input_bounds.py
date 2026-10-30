import pytest
from allocator import parse_program, MAX_TEXT_LENGTH, MAX_INSTRUCTIONS, MAX_VARIABLES, MAX_NAME_LENGTH

def test_instruction_boundary():
    assert len(parse_program("a=1\n" * MAX_INSTRUCTIONS)) == MAX_INSTRUCTIONS
    with pytest.raises(ValueError, match="instructions"):
        parse_program("a=1\n" * (MAX_INSTRUCTIONS + 1))

def test_variable_boundary():
    assert len(parse_program("\n".join(f"v{i}=1" for i in range(MAX_VARIABLES)))) == MAX_VARIABLES
    with pytest.raises(ValueError, match="variables"):
        parse_program("\n".join(f"v{i}=1" for i in range(MAX_VARIABLES + 1)))

def test_name_boundary():
    parse_program("a" * MAX_NAME_LENGTH + "=1")
    with pytest.raises(ValueError, match="names"):
        parse_program("a" * (MAX_NAME_LENGTH + 1) + "=1")

def test_text_boundary():
    parse_program("a=1" + " " * (MAX_TEXT_LENGTH - 3))
    with pytest.raises(ValueError, match="characters"):
        parse_program("a=1" + " " * (MAX_TEXT_LENGTH - 2))

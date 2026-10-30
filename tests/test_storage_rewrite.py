import pytest
from allocator import parse_program
from graph_tools import rewrite_program

def test_whole_names_and_constants_survive_storage_rewrite():
    instructions = parse_program("a=1.5\ndata=a+total")
    assert rewrite_program(instructions, {"a": 0, "data": 1}, ["total"]) == ["R1=1.5", "R2=R1+MEM[total]"]

def test_missing_storage_mapping_fails():
    with pytest.raises(ValueError, match="No register or memory slot"):
        rewrite_program(parse_program("result=input"), {"result": 0}, [])

from allocator import parse_program, analyze_liveness
from graph_tools import live_ranges

def test_worked_example_live_sets():
    instructions = parse_program("a=1\nb=a\nc=a+b\nd=a+c")
    live_in, live_out = analyze_liveness(instructions)
    assert live_in == [set(), {"a"}, {"a", "b"}, {"a", "c"}]
    assert live_out == [{"a"}, {"a", "b"}, {"a", "c"}, set()]
    live_out[0].add("changed")
    assert "changed" not in live_in[1]

def test_redefinition_kills_old_value():
    instructions = parse_program("a=1\na=2\nb=a")
    assert analyze_liveness(instructions) == ([set(), set(), {"a"}], [set(), {"a"}, set()])

def test_timeline_uses_source_line_numbers():
    instructions = parse_program("\na=1\n\nb=a")
    live_in, live_out = analyze_liveness(instructions)
    assert live_ranges(instructions, live_in, live_out) == [
        {"Variable": "a", "Start": 2, "End": 4},
        {"Variable": "b", "Start": 4, "End": 4},
    ]

import unittest

import networkx as nx

from src.coloring_tools import coloring_steps
from src.liveness import liveness_equation, analyze_liveness
from src.live_ranges import build_live_ranges
from src.parser import parse_program


class LivenessDisplayTests(unittest.TestCase):
    # DM concept: the equation displays set union and set difference with actual members.
    def test_liveness_equation_uses_real_sets(self):
        equation = liveness_equation({"a"}, {"b", "c"}, {"d"}, {"a", "b", "c"})
        self.assertEqual(
            equation,
            "LIVE-IN = USE ∪ (LIVE-OUT − DEF) = {a} ∪ ({b, c} − {d}) = {a, b, c}",
        )

    # DM concept: source instruction numbers remain correct when blank lines are skipped.
    def test_live_ranges_keep_source_line_numbers(self):
        instructions = parse_program("a = 1\n\nresult = a + 1")
        self.assertEqual([item.number for item in instructions], [1, 3])
        live_in, live_out = analyze_liveness(instructions)
        ranges = {row["Variable"]: row for row in build_live_ranges(instructions, live_in, live_out)}
        self.assertEqual(ranges["result"]["Start"], 3)

    # DM concept: a live range records a variable's start and last live instruction.
    def test_live_ranges_cover_input_and_defined_variables(self):
        instructions = parse_program("a = b + c\nd = a + b\nresult = d")
        live_in, live_out = analyze_liveness(instructions)
        ranges = {row["Variable"]: row for row in build_live_ranges(instructions, live_in, live_out)}
        self.assertEqual(ranges["a"]["Start"], 1)
        self.assertEqual(ranges["d"]["Start"], 2)
        self.assertGreaterEqual(ranges["b"]["End"], ranges["b"]["Start"])


class StepColoringTests(unittest.TestCase):
    # DM concept: each step chooses the smallest color not used by earlier colored neighbors.
    def test_steps_produce_a_valid_final_coloring(self):
        graph = nx.path_graph(["a", "b", "c"])
        steps = coloring_steps(graph)
        self.assertEqual(len(steps), 3)
        final_coloring = steps[-1]["partial_coloring"]
        for left, right in graph.edges():
            self.assertNotEqual(final_coloring[left], final_coloring[right])
        self.assertEqual(steps[0]["neighbor_colors"], [])


if __name__ == "__main__":
    unittest.main()

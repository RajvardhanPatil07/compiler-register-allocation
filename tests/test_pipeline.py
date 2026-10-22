import unittest

from src.coloring import color_graph, coloring_count
from src.interference import build_interference_graph, graph_statistics
from src.liveness import analyze_liveness
from src.parser import parse_program, parse_line


class ParserTests(unittest.TestCase):
    def test_extracts_use_and_define(self):
        instruction = parse_line("total = price * count", 1)
        self.assertEqual(instruction.use, {"price", "count"})
        self.assertEqual(instruction.define, {"total"})

    def test_self_reference_is_used(self):
        instruction = parse_line("value = value + 1", 1)
        self.assertEqual(instruction.use, {"value"})
        self.assertEqual(instruction.define, {"value"})

    def test_rejects_missing_assignment(self):
        with self.assertRaises(ValueError):
            parse_line("a + b", 1)

    def test_rejects_invalid_destination(self):
        with self.assertRaises(ValueError):
            parse_line("2value = a + b", 1)

    def test_rejects_empty_program(self):
        with self.assertRaises(ValueError):
            parse_program("  \n\n")


class LivenessTests(unittest.TestCase):
    def test_liveness_for_straight_line_program(self):
        instructions = parse_program(
            "a = b + c\n"
            "d = a + e\n"
            "result = d + c"
        )
        live_in, live_out = analyze_liveness(instructions)

        self.assertEqual(live_in[0], {"b", "c", "e"})
        self.assertEqual(live_out[0], {"a", "c", "e"})
        self.assertEqual(live_in[1], {"a", "c", "e"})
        self.assertEqual(live_out[1], {"d", "c"})
        self.assertEqual(live_in[2], {"d", "c"})
        self.assertEqual(live_out[2], set())


class InterferenceAndColoringTests(unittest.TestCase):
    def test_simultaneously_live_variables_interfere(self):
        instructions = parse_program(
            "a = b + c\n"
            "d = a + e\n"
            "result = d + c"
        )
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)

        for live_set in live_in:
            for left in live_set:
                for right in live_set:
                    if left != right:
                        self.assertTrue(graph.has_edge(left, right))

    def test_coloring_gives_different_colors_to_adjacent_vertices(self):
        instructions = parse_program(
            "a = b + c\n"
            "d = a + e\n"
            "result = d + c"
        )
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        coloring = color_graph(graph)

        for left, right in graph.edges():
            self.assertNotEqual(coloring[left], coloring[right])

    def test_triangle_uses_three_colors(self):
        instructions = parse_program("x = a + b\ny = x + c\nresult = y + a")
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        coloring = color_graph(graph)

        self.assertEqual(coloring_count(coloring), 3)

    def test_graph_statistics(self):
        instructions = parse_program("x = a + b\nresult = x")
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        stats = graph_statistics(graph)

        self.assertEqual(stats["vertices"], graph.number_of_nodes())
        self.assertEqual(stats["edges"], graph.number_of_edges())
        self.assertEqual(stats["connected_components"], 1)


if __name__ == "__main__":
    unittest.main()

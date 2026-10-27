import unittest
from pathlib import Path

from src.coloring import color_graph, coloring_count
from src.interference import build_interference_graph, graph_statistics
from src.liveness import analyze_liveness
from src.parser import parse_program, parse_line


class ParserTests(unittest.TestCase):
    # DM concept: USE and DEF are sets of read and written variables.
    def test_extracts_use_and_define(self):
        instruction = parse_line("total = price * count", 1)
        self.assertEqual(instruction.use, {"price", "count"})
        self.assertEqual(instruction.define, {"total"})

    # DM concept: constants do not add variables to the USE set.
    def test_accepts_copy_and_number_assignments(self):
        self.assertEqual(parse_line("copy = value", 1).use, {"value"})
        self.assertEqual(parse_line("answer = 42", 1).use, set())

    # DM concept: a variable appearing on both sides is read and written.
    def test_self_reference_is_used(self):
        instruction = parse_line("value = value + 1", 1)
        self.assertEqual(instruction.use, {"value"})
        self.assertEqual(instruction.define, {"value"})

    # DM concept: each instruction must follow the assignment grammar.
    def test_rejects_missing_assignment(self):
        with self.assertRaises(ValueError):
            parse_line("a + b", 1)

    # DM concept: a variable must start with a letter or underscore.
    def test_rejects_invalid_destination(self):
        with self.assertRaises(ValueError):
            parse_line("2value = a + b", 1)

    # DM concept: a program is a non-empty finite sequence.
    def test_rejects_empty_program(self):
        with self.assertRaises(ValueError):
            parse_program("  \n\n")

    # DM concept: an assignment must have a value on its right-hand side.
    def test_rejects_empty_right_hand_side(self):
        with self.assertRaises(ValueError):
            parse_line("value =", 1)

    # DM concept: supported expressions contain at most one binary operator.
    def test_rejects_malformed_expression(self):
        with self.assertRaises(ValueError):
            parse_line("value = a + * b", 1)

    # DM concept: one assignment contains exactly one equality symbol.
    def test_rejects_multiple_equals(self):
        with self.assertRaises(ValueError):
            parse_line("value == a", 1)


class LivenessTests(unittest.TestCase):
    # DM concept: LIVE-IN is USE union (LIVE-OUT minus DEF).
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
    # DM concept: variables live at the same point must be pairwise adjacent.
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

    # DM concept: a proper coloring gives different colors to edge endpoints.
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

    # DM concept: three pairwise adjacent vertices need three colors.
    def test_triangle_uses_three_colors(self):
        instructions = parse_program("x = a + b\ny = x + c\nresult = y + a")
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        coloring = color_graph(graph)

        self.assertTrue(graph.has_edge("a", "b"))
        self.assertTrue(graph.has_edge("a", "c"))
        self.assertTrue(graph.has_edge("b", "c"))
        self.assertEqual(coloring_count(coloring), 3)

    # DM concept: isolated vertices form one-vertex connected components.
    def test_graph_statistics_include_isolated_vertices(self):
        instructions = parse_program("x = a + b\nresult = x")
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        stats = graph_statistics(graph)

        self.assertEqual(stats["vertices"], 4)
        self.assertEqual(stats["edges"], 1)
        self.assertEqual(stats["connected_components"], 3)

    # DM concept: an unused definition is an isolated vertex in this model.
    def test_unused_final_definition_is_isolated_until_used(self):
        program = "a = b + c\nd = a * e\nunused = d + c"
        instructions = parse_program(program)
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)

        self.assertEqual(graph.degree("unused"), 0)

        program_with_use = program + "\nresult = unused + a"
        instructions = parse_program(program_with_use)
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)

        self.assertGreater(graph.degree("unused"), 0)

    # DM concept: every graph edge must remain properly colored after the pipeline.
    def test_repository_sample_runs_through_full_pipeline(self):
        repository_root = Path(__file__).resolve().parents[1]
        sample_path = repository_root / "examples" / "sample_program.txt"
        program = sample_path.read_text(encoding="utf-8")

        instructions = parse_program(program)
        live_in, live_out = analyze_liveness(instructions)
        graph = build_interference_graph(instructions, live_in, live_out)
        coloring = color_graph(graph)

        self.assertEqual(set(coloring), set(graph.nodes()))
        for left, right in graph.edges():
            self.assertNotEqual(coloring[left], coloring[right])


if __name__ == "__main__":
    unittest.main()

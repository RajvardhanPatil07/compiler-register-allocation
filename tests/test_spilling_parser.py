import unittest

import networkx as nx

from src.parser import parse_program
from src.spilling import allocate_with_spilling, rewrite_program_with_registers
from src.validity import check_coloring_validity


class SpillingTests(unittest.TestCase):
    # DM concept: removing high-degree vertices can reduce a graph's coloring requirement.
    def test_spilling_ends_with_valid_coloring(self):
        graph = nx.complete_graph(["a", "b", "c", "d"])
        result = allocate_with_spilling(graph, 2)
        self.assertTrue(result["spilled"])
        self.assertLessEqual(result["registers_used"], 2)
        self.assertEqual(set(result["coloring"]), set(result["graph"].nodes()))
        self.assertTrue(check_coloring_validity(result["graph"], result["coloring"])["valid"])

    # DM concept: rewritten variables use the register assigned by their color.
    def test_rewrites_registers_and_spilled_variables(self):
        instructions = parse_program("a = 1\nb = 2\nc = a + b")
        rewritten = rewrite_program_with_registers(
            instructions, {"a": 0, "c": 1}, ["b"]
        )
        self.assertEqual(rewritten, ["R1 = 1", "MEM[b] = 2", "R2 = R1 + MEM[b]"])

    # DM concept: degree-based spill choice is deterministic when degrees tie.
    def test_spill_candidate_uses_highest_degree_then_name(self):
        graph = nx.complete_graph(["c", "b", "a"])
        result = allocate_with_spilling(graph, 2)
        self.assertEqual(result["spilled"], ["a"])
        self.assertEqual(result["registers_used"], 2)


class ParserOrderTests(unittest.TestCase):
    # DM concept: instruction order matters when a variable is assigned later.
    def test_reports_use_before_later_definition_with_source_line(self):
        with self.assertRaisesRegex(ValueError, "Line 3: variable 'z'.*line 4"):
            parse_program("\nx = 1\ny = z + 1\nz = 2")

    # DM concept: a name that is never assigned can represent an external input.
    def test_accepts_external_input_variables(self):
        instructions = parse_program("answer = external_value + 1")
        self.assertEqual(instructions[0].use, {"external_value"})

    # DM concept: unsupported expression symbols receive a numbered diagnostic.
    def test_reports_unsupported_symbols_with_line_number(self):
        with self.assertRaisesRegex(ValueError, "Line 2: unsupported symbol"):
            parse_program("a = 1\nb = a ^ 2")

    # DM concept: an empty instruction sequence is not a valid program.
    def test_empty_input_has_friendly_error(self):
        with self.assertRaisesRegex(ValueError, "Line 1: input is empty"):
            parse_program("\n \n")


if __name__ == "__main__":
    unittest.main()

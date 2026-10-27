import unittest
from pathlib import Path

import networkx as nx

from src.coloring import color_graph, coloring_count
from src.coloring_tools import exact_coloring
from src.interference import build_interference_graph
from src.liveness import analyze_liveness
from src.parser import parse_program
from src.spilling import allocate_with_spilling


ROOT = Path(__file__).resolve().parents[1]


def load_example_graph(filename: str) -> nx.Graph:
    # DM concept: the source program determines an interference graph through liveness.
    program_path = ROOT / "examples" / filename
    instructions = parse_program(program_path.read_text(encoding="utf-8"))
    live_in, live_out = analyze_liveness(instructions)
    return build_interference_graph(instructions, live_in, live_out)


class ExampleProgramTests(unittest.TestCase):
    # DM concept: the chromatic number of this example is exactly two.
    def test_easy_example_needs_two_colors(self):
        count, _ = exact_coloring(load_example_graph("easy_2_registers.txt"))
        self.assertEqual(count, 2)

    # DM concept: this example demonstrates a graph requiring three colors.
    def test_medium_example_needs_three_colors(self):
        count, _ = exact_coloring(load_example_graph("medium_3_registers.txt"))
        self.assertEqual(count, 3)

    # DM concept: this example demonstrates a graph requiring at least four colors.
    def test_hard_example_needs_four_colors(self):
        count, _ = exact_coloring(load_example_graph("hard_4_registers.txt"))
        self.assertEqual(count, 4)

    # DM concept: insufficient colors cause degree-based spilling until a valid coloring fits.
    def test_spilling_example_needs_spill_at_two_registers(self):
        graph = load_example_graph("spilling_demo.txt")
        result = allocate_with_spilling(graph, 2)
        self.assertTrue(result["spilled"])
        self.assertLessEqual(result["registers_used"], 2)

    # DM concept: greedy coloring can use more colors than the chromatic number.
    def test_greedy_counterexample_is_verified_by_exact_search(self):
        graph = load_example_graph("greedy_not_optimal.txt")
        exact_count, _ = exact_coloring(graph)
        greedy_count = coloring_count(color_graph(graph))
        self.assertEqual(exact_count, 5)
        self.assertEqual(greedy_count, 6)
        self.assertGreater(greedy_count, exact_count)

    # DM concept: disconnected components are separate groups without paths between them.
    def test_disconnected_example_has_multiple_components(self):
        graph = load_example_graph("disconnected_components.txt")
        self.assertGreater(nx.number_connected_components(graph), 1)

    # DM concept: a single isolated vertex needs exactly one color.
    def test_single_vertex_needs_one_color(self):
        count, coloring = exact_coloring(nx.empty_graph(["only"]))
        self.assertEqual(count, 1)
        self.assertEqual(coloring, {"only": 0})


if __name__ == "__main__":
    unittest.main()

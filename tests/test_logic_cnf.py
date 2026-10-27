import unittest

import networkx as nx

from src.clique import explain_pigeonhole
from src.cnf_view import generate_coloring_cnf


class PigeonholeTests(unittest.TestCase):
    # DM concept: a clique larger than the color budget cannot be properly colored.
    def test_pigeonhole_message_triggers_for_triangle(self):
        result = explain_pigeonhole(nx.complete_graph(["a", "b", "c"]), 2)
        self.assertTrue(result["impossible"])
        self.assertEqual(result["clique_size"], 3)
        self.assertIn("pigeonhole principle", result["message"])
        self.assertIn("allocation without spilling is impossible", result["message"])

    # DM concept: a color budget meeting the clique lower bound passes this lower-bound check.
    def test_pigeonhole_message_passes_when_budget_is_enough(self):
        result = explain_pigeonhole(nx.complete_graph(3), 3)
        self.assertFalse(result["impossible"])
        self.assertIn("does not prove that the graph", result["message"])


class CnfTests(unittest.TestCase):
    # DM concept: CNF clause groups encode exactly-one-color and adjacent-different constraints.
    def test_clause_counts_for_one_edge_and_two_colors(self):
        graph = nx.Graph([("a", "b")])
        result = generate_coloring_cnf(graph, 2)
        counts = {row["Clause group"]: row["Total clauses"] for row in result["counts"]}
        self.assertEqual(counts["At-least-one"], 2)
        self.assertEqual(counts["At-most-one"], 2)
        self.assertEqual(counts["Adjacent-different"], 2)
        self.assertEqual(result["total_clauses"], 6)
        self.assertFalse(result["truncated"])

    # DM concept: the display cap limits long clause lists while preserving total counts.
    def test_clause_display_is_limited(self):
        result = generate_coloring_cnf(nx.complete_graph(8), 4, display_limit=5)
        self.assertEqual(len(result["clauses"]), 5)
        self.assertTrue(result["truncated"])
        self.assertGreater(result["total_clauses"], 5)


if __name__ == "__main__":
    unittest.main()

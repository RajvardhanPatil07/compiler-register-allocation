import unittest

import networkx as nx

from src.relation_check import build_complement_graph, check_relation_properties
from src.validity import check_coloring_validity


class RelationTests(unittest.TestCase):
    # DM concept: a path gives a non-transitive interference relation.
    def test_path_has_non_transitive_counterexample(self):
        details = check_relation_properties(nx.path_graph(["a", "b", "c"]))
        self.assertFalse(details["reflexive"])
        self.assertTrue(details["irreflexive"])
        self.assertTrue(details["symmetric"])
        self.assertFalse(details["transitive"])
        self.assertEqual(details["counterexample"], ("a", "b", "c"))

    # DM concept: complement edges represent pairs that do not interfere.
    def test_complement_graph(self):
        graph = nx.path_graph(["a", "b", "c"])
        complement = build_complement_graph(graph)
        self.assertTrue(complement.has_edge("a", "c"))
        self.assertFalse(complement.has_edge("a", "b"))


class ColoringValidityTests(unittest.TestCase):
    # DM concept: an edge endpoint pair must never share a color.
    def test_valid_coloring_passes(self):
        graph = nx.path_graph(["a", "b", "c"])
        result = check_coloring_validity(graph, {"a": 0, "b": 1, "c": 0})
        self.assertTrue(result["valid"])
        self.assertEqual(result["bad_edges"], [])

    # DM concept: equal colors on adjacent vertices violate proper coloring.
    def test_wrong_coloring_fails(self):
        graph = nx.path_graph(["a", "b", "c"])
        result = check_coloring_validity(graph, {"a": 0, "b": 0, "c": 1})
        self.assertFalse(result["valid"])
        self.assertEqual(result["bad_edges"], [("a", "b")])


if __name__ == "__main__":
    unittest.main()

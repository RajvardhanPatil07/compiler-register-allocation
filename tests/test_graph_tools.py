import unittest

import networkx as nx

from src.clique import maximum_clique
from src.coloring_tools import compare_coloring_strategies, exact_coloring
from src.graph_stats import adjacency_matrix, check_handshake_lemma, connected_components, degree_sequence, degree_table


class GraphStatisticsTests(unittest.TestCase):
    # DM concept: vertex degrees count incident edges.
    def test_degree_table_and_sequence(self):
        graph = nx.path_graph(["a", "b", "c"])
        table = degree_table(graph)
        self.assertEqual(table.iloc[0]["Degree"], 2)
        self.assertEqual(degree_sequence(graph), [2, 1, 1])

    # DM concept: the sum of degrees equals twice the number of edges.
    def test_handshake_lemma(self):
        graph = nx.cycle_graph(4)
        result = check_handshake_lemma(graph)
        self.assertEqual(result["degree_sum"], 8)
        self.assertEqual(result["twice_edges"], 8)
        self.assertTrue(result["holds"])

    # DM concept: an adjacency matrix records whether each pair has an edge.
    def test_adjacency_matrix(self):
        graph = nx.path_graph(["a", "b"])
        matrix = adjacency_matrix(graph)
        self.assertEqual(matrix.loc["a", "b"], 1)
        self.assertEqual(matrix.loc["a", "a"], 0)

    # DM concept: connected components group vertices linked by paths.
    def test_connected_components(self):
        graph = nx.Graph([("a", "b"), ("c", "d")])
        self.assertEqual(connected_components(graph), [["a", "b"], ["c", "d"]])


class CliqueAndColoringTests(unittest.TestCase):
    # DM concept: a triangle is a clique of size three.
    def test_triangle_clique_size(self):
        vertices, size = maximum_clique(nx.complete_graph(3))
        self.assertEqual(size, 3)
        self.assertEqual(len(vertices), 3)

    # DM concept: a path of three vertices can be properly colored with two colors.
    def test_exact_chromatic_number_for_path(self):
        graph = nx.path_graph(3)
        count, coloring = exact_coloring(graph)
        self.assertEqual(count, 2)
        for left, right in graph.edges():
            self.assertNotEqual(coloring[left], coloring[right])

    # DM concept: each vertex of a triangle must have a distinct color.
    def test_exact_chromatic_number_for_triangle(self):
        count, _ = exact_coloring(nx.complete_graph(3))
        self.assertEqual(count, 3)

    # DM concept: exact search is bounded so large inputs do not cause a long search.
    def test_exact_coloring_size_limit(self):
        count, coloring = exact_coloring(nx.path_graph(13))
        self.assertIsNone(count)
        self.assertEqual(coloring, {})

    # DM concept: greedy algorithms may choose a coloring with a strategy-specific order.
    def test_three_greedy_strategies_are_reported(self):
        results = compare_coloring_strategies(nx.path_graph(3))
        self.assertEqual(len(results), 3)
        self.assertTrue(all(result["Colors Used"] == 2 for result in results))


if __name__ == "__main__":
    unittest.main()

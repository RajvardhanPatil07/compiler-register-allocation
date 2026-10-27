"""Relation-property checks and complement graphs for interference."""

import networkx as nx


def interference_relation(graph: nx.Graph) -> set[tuple[str, str]]:
    # DM concept: each undirected interference edge contributes two ordered pairs.
    relation = set()
    for left, right in graph.edges():
        relation.add((left, right))
        relation.add((right, left))
    return relation


def _find_transitivity_counterexample(vertices: list[str], relation: set) -> tuple | None:
    # DM concept: transitivity fails when (a, b) and (b, c) exist but (a, c) does not.
    fallback = None
    for first in vertices:
        for middle in vertices:
            if (first, middle) not in relation:
                continue
            for last in vertices:
                if (middle, last) not in relation or (first, last) in relation:
                    continue
                example = (first, middle, last)
                if len(set(example)) == 3:
                    return example
                if fallback is None:
                    fallback = example
    return fallback


def check_relation_properties(graph: nx.Graph) -> dict:
    # DM concept: relation properties are checked using ordered pairs and missing pairs.
    vertices = list(graph.nodes())
    relation = interference_relation(graph)
    counterexample = _find_transitivity_counterexample(vertices, relation)
    return {
        "relation": relation,
        "reflexive": all((vertex, vertex) in relation for vertex in vertices),
        "irreflexive": all((vertex, vertex) not in relation for vertex in vertices),
        "symmetric": all((right, left) in relation for left, right in relation),
        "transitive": counterexample is None,
        "counterexample": counterexample,
    }


def build_complement_graph(graph: nx.Graph) -> nx.Graph:
    # DM concept: the complement joins distinct vertices that are not adjacent originally.
    return nx.complement(graph)

#!/usr/bin/env python3
"""Reproduce the paper's 39-vertex reduction of H_3."""

import itertools
import sys
from pathlib import Path

H3_DIR = Path(__file__).resolve().parents[1] / "h3"
sys.path.insert(0, str(H3_DIR))
from build_h3 import build, triangles_and_system  # noqa: E402


REMOVED_CLIQUES = (0, 1, 4)


def maximal_cliques(G):
    return [
        frozenset(i for i, points in enumerate(G["son"]) if point in points)
        for point in G["unital"]
    ]


def write_cnf(path, edges, triangles):
    edge_index = {edge: i + 1 for i, edge in enumerate(edges)}
    clauses = []
    for triangle in triangles:
        variables = tuple(edge_index[edge] for edge in itertools.combinations(triangle, 2))
        clauses.extend((variables, tuple(-v for v in variables)))
    with path.open("w") as stream:
        stream.write(f"p cnf {len(edges)} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")
    return clauses


def main():
    root = Path(__file__).resolve().parent
    graph = build()
    all_triangles, nondegenerate = triangles_and_system(graph)
    cliques = maximal_cliques(graph)
    removed = set().union(*(cliques[i] for i in REMOVED_CLIQUES))
    assert len(removed) == 24
    assert not set.intersection(*(set(cliques[i]) for i in REMOVED_CLIQUES))
    vertices = set(range(graph["n"])) - removed
    induced_triangles = [t for t in all_triangles if set(t) <= vertices]
    selected = [t for t in nondegenerate if set(t) <= vertices]
    assert len(vertices) == 39
    assert len(induced_triangles) == 1488
    assert len(selected) == 898
    selected_set = set(selected)
    for quad in itertools.combinations(sorted(vertices), 4):
        assert sum(face in selected_set for face in itertools.combinations(quad, 3)) < 4
    edges = sorted({edge for triangle in selected for edge in itertools.combinations(triangle, 2)})
    assert all(edge[0] in vertices and edge[1] in vertices for edge in edges)
    clauses = write_cnf(root / "h3_39.cnf", edges, selected)
    with (root / "h3_39.edges").open("w") as stream:
        for u, v in edges:
            stream.write(f"{u} {v}\n")
    with (root / "h3_39.vertices").open("w") as stream:
        for v in sorted(vertices):
            stream.write(f"{v}\n")
    print(
        f"removed_cliques={REMOVED_CLIQUES} removed_vertices={len(removed)} "
        f"vertices={len(vertices)} edges={len(edges)} "
        f"triangles={len(induced_triangles)} nondegenerate={len(selected)} "
        f"clauses={len(clauses)}"
    )
    print("property_a=no 4-subset contains all 4 selected triples [OK]")


if __name__ == "__main__":
    main()

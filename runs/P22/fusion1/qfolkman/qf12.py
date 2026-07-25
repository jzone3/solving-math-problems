#!/usr/bin/env python3
"""Reproduce the 12-vertex example printed in the authors' notebook."""

import itertools
from pathlib import Path


TRIPLES = (
    (0, 1, 2), (0, 1, 3), (0, 1, 5), (0, 1, 6), (0, 1, 7), (0, 1, 11),
    (0, 2, 4), (0, 2, 5), (0, 2, 7), (0, 2, 9), (0, 2, 10), (0, 2, 11),
    (0, 3, 4), (0, 3, 8), (0, 3, 9), (0, 4, 5), (0, 4, 6), (0, 4, 8),
    (0, 5, 7), (0, 5, 9), (0, 5, 10), (0, 6, 7), (0, 6, 9), (0, 6, 10),
    (0, 6, 11), (0, 7, 8), (0, 8, 9), (0, 8, 10), (0, 8, 11), (0, 10, 11),
    (1, 2, 3), (1, 2, 4), (1, 2, 8), (1, 2, 9), (1, 2, 10), (1, 3, 5),
    (1, 3, 6), (1, 3, 7), (1, 3, 8), (1, 3, 9), (1, 4, 5), (1, 4, 6),
    (1, 4, 7), (1, 4, 8), (1, 5, 9), (1, 5, 10), (1, 5, 11), (1, 6, 9),
    (1, 6, 10), (1, 7, 10), (1, 7, 11), (1, 8, 10), (1, 8, 11), (1, 9, 10),
    (1, 9, 11), (2, 3, 4), (2, 3, 6), (2, 3, 7), (2, 3, 10), (2, 3, 11),
    (2, 4, 6), (2, 4, 9), (2, 4, 11), (2, 5, 6), (2, 5, 8), (2, 5, 11),
    (2, 6, 9), (2, 7, 8), (2, 7, 9), (2, 7, 10), (2, 8, 9), (2, 8, 11),
    (3, 4, 5), (3, 4, 9), (3, 4, 10), (3, 5, 6), (3, 5, 7), (3, 5, 8),
    (3, 5, 11), (3, 6, 10), (3, 6, 11), (3, 7, 8), (3, 7, 9), (3, 8, 10),
    (3, 8, 11), (3, 9, 10), (3, 9, 11), (3, 10, 11), (4, 5, 6), (4, 5, 9),
    (4, 5, 10), (4, 5, 11), (4, 6, 8), (4, 6, 10), (4, 6, 11), (4, 7, 8),
    (4, 7, 9), (4, 7, 10), (4, 7, 11), (4, 8, 9), (4, 9, 11), (5, 6, 7),
    (5, 6, 8), (5, 7, 9), (5, 7, 10), (5, 7, 11), (5, 8, 9), (5, 8, 10),
    (5, 10, 11), (6, 7, 8), (6, 7, 9), (6, 7, 11), (6, 8, 9), (6, 8, 10),
    (6, 9, 11), (7, 8, 10), (7, 8, 11), (7, 9, 10), (8, 9, 10), (8, 9, 11),
)


def write_cnf(path):
    assert len(TRIPLES) == 120
    assert all(len(set(t)) == 3 and all(0 <= v < 12 for v in t) for t in TRIPLES)
    for quad in itertools.combinations(range(12), 4):
        assert sum(set(face) <= set(quad) for face in TRIPLES) < 4
    edges = sorted({edge for triple in TRIPLES for edge in itertools.combinations(triple, 2)})
    edge_index = {edge: i + 1 for i, edge in enumerate(edges)}
    clauses = []
    for triple in TRIPLES:
        variables = tuple(edge_index[edge] for edge in itertools.combinations(triple, 2))
        clauses.extend((variables, tuple(-v for v in variables)))
    with path.open("w") as stream:
        stream.write(f"p cnf {len(edges)} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")
    return edges, clauses


def main():
    root = Path(__file__).resolve().parent
    edges, clauses = write_cnf(root / "qf12.cnf")
    with (root / "qf12.edges").open("w") as stream:
        for u, v in edges:
            stream.write(f"{u} {v}\n")
    print(f"vertices=12 edges={len(edges)} triangles={len(TRIPLES)} clauses={len(clauses)}")
    print("property_a=no 4-subset contains all 4 triples [OK]")


if __name__ == "__main__":
    main()

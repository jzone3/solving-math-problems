#!/usr/bin/env python3
"""Construct and certify the paper's 11-vertex quasi-Folkman system."""

from itertools import combinations
from pathlib import Path


N = 11
BASE = (
    (1, 2, 3),
    (1, 2, 4),
    (1, 2, 6),
    (1, 2, 7),
    (1, 3, 5),
    (1, 3, 8),
    (1, 4, 7),
    (1, 4, 8),
)


def rotate(triple, shift):
    return tuple(sorted(((v - 1 + shift) % N) + 1 for v in triple))


def build_triangles():
    triangles = {rotate(triple, shift) for triple in BASE for shift in range(N)}
    assert len(triangles) == 8 * N == 88
    return sorted(triangles)


def build_graph(triangles):
    edges = sorted({edge for triple in triangles for edge in combinations(triple, 2)})
    assert all(1 <= u < v <= N for u, v in edges)
    return edges


def check_k4_free(triangles):
    triangle_set = set(triangles)
    bad = []
    for quad in combinations(range(1, N + 1), 4):
        faces = list(combinations(quad, 3))
        count = sum(face in triangle_set for face in faces)
        if count == 4:
            bad.append((quad, faces))
    assert not bad, bad
    return bad


def write_cnf(edges, triangles, path):
    edge_index = {edge: i + 1 for i, edge in enumerate(edges)}
    clauses = []
    for a, b, c in triangles:
        vars_ = [
            edge_index[tuple(sorted(edge))]
            for edge in combinations((a, b, c), 2)
        ]
        clauses.append(tuple(vars_))
        clauses.append(tuple(-v for v in vars_))
    assert len(clauses) == 2 * len(triangles) == 176
    with path.open("w") as stream:
        stream.write(f"p cnf {len(edges)} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")
    return clauses


def main():
    root = Path(__file__).resolve().parent
    triangles = build_triangles()
    edges = build_graph(triangles)
    check_k4_free(triangles)
    clauses = write_cnf(edges, triangles, root / "qf11.cnf")
    with (root / "qf11.edges").open("w") as stream:
        for edge in edges:
            stream.write(f"{edge[0]} {edge[1]}\n")
    print(f"vertices={N} edges={len(edges)} triangles={len(triangles)}")
    print("property_a=no 4-subset contains all 4 triples [OK]")
    print(f"qf11.cnf variables={len(edges)} clauses={len(clauses)}")


if __name__ == "__main__":
    main()

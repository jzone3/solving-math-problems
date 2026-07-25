#!/usr/bin/env python3
"""Independent verifier for qf11.py's triangle set and CNF."""

from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
N = 11
SEEDS = (
    frozenset((1, 2, 3)),
    frozenset((1, 2, 4)),
    frozenset((1, 2, 6)),
    frozenset((1, 2, 7)),
    frozenset((1, 3, 5)),
    frozenset((1, 3, 8)),
    frozenset((1, 4, 7)),
    frozenset((1, 4, 8)),
)


def reconstruct():
    triangles = set()
    for seed in SEEDS:
        for shift in range(N):
            triangles.add(
                frozenset(1 + ((vertex - 1 + shift) % N) for vertex in seed)
            )
    assert len(triangles) == 88
    return sorted(tuple(sorted(t)) for t in triangles)


def expected_clauses(triangles):
    edges = sorted(
        {
            tuple(sorted(edge))
            for triple in triangles
            for edge in combinations(triple, 2)
        }
    )
    index = {edge: number for number, edge in enumerate(edges, 1)}
    result = []
    for triple in triangles:
        variables = tuple(index[edge] for edge in combinations(triple, 2))
        result += [variables, tuple(-x for x in variables)]
    return edges, Counter(result)


def read_cnf(path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    assert header[:2] == ["p", "cnf"]
    nvars, nclauses = map(int, header[2:4])
    clauses = []
    for line in lines[1:]:
        values = tuple(map(int, line.split()))
        assert values[-1] == 0
        clauses.append(values[:-1])
    assert len(clauses) == nclauses
    return nvars, nclauses, Counter(clauses)


def main():
    triangles = reconstruct()
    triangle_set = set(triangles)
    for quad in combinations(range(1, N + 1), 4):
        assert sum(face in triangle_set for face in combinations(quad, 3)) < 4
    edges, expected = expected_clauses(triangles)
    nvars, nclauses, actual = read_cnf(ROOT / "qf11.cnf")
    assert (nvars, nclauses) == (len(edges), 176)
    assert actual == expected
    print(
        f"independent verifier: vertices={N} edges={len(edges)} "
        f"triangles={len(triangles)} clauses={nclauses} [PASS]"
    )


if __name__ == "__main__":
    main()

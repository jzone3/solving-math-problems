#!/usr/bin/env python3
"""Independently parse Kissat models and verify Exoo witnesses."""

import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = (
    ("L17_2", 17, 2),
    ("L61_8", 61, 8),
    ("L79_12", 79, 12),
    ("L421_7", 421, 7),
    ("L631_24", 631, 24),
)


def independent_connection(n, generator):
    values = []
    x = 1 % n
    while x not in values:
        values.append(x)
        x = (x * generator) % n
    assert (-1) % n in values
    return set(values)


def independent_graph(n, generator):
    connection = independent_connection(n, generator)
    adjacency = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if (v - u) % n in connection:
                adjacency[u].add(v)
                adjacency[v].add(u)
    return adjacency


def independent_triangles(adjacency):
    result = []
    for a in range(len(adjacency)):
        for b in sorted(v for v in adjacency[a] if v > a):
            for c in sorted(v for v in adjacency[a] if v > b):
                if c in adjacency[b]:
                    result.append((a, b, c))
    return result


def parse_model(path, variable_count):
    assignment = {}
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields or fields[0] != "v":
            continue
        for literal in map(int, fields[1:]):
            if literal == 0:
                continue
            assignment[abs(literal)] = literal > 0
    assert len(assignment) == variable_count, (path, len(assignment), variable_count)
    return assignment


def verify_one(name, n, generator):
    adjacency = independent_graph(n, generator)
    edge_list = [
        (u, v)
        for u in range(n)
        for v in sorted(adjacency[u])
        if u < v
    ]
    edge_index = {edge: i + 1 for i, edge in enumerate(edge_list)}
    triangle_list = independent_triangles(adjacency)
    model = parse_model(ROOT / f"{name}.model", len(edge_list))
    for triangle in triangle_list:
        vars_ = [edge_index[edge] for edge in itertools.combinations(triangle, 2)]
        colors = {model[var] for var in vars_}
        assert len(colors) == 2, (name, triangle, vars_, colors)
    print(
        f"{name}: independently verified SAT witness "
        f"vertices={n} edges={len(edge_list)} triangles={len(triangle_list)} [PASS]"
    )


if __name__ == "__main__":
    for target in TARGETS:
        verify_one(*target)

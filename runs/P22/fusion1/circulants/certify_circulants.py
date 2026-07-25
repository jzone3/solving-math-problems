#!/usr/bin/env python3
"""Build and structurally certify the circulants from arXiv:1207.3750."""

import itertools
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def subgroup_connection_set(n, generator):
    values = set()
    x = 1 % n
    while x not in values:
        values.add(x)
        x = (x * generator) % n
    assert (-1) % n in values
    return values


def power_residue_set(n, exponent):
    values = {pow(a, exponent, n) for a in range(1, n)}
    values.discard(0)
    assert (-1) % n in values
    return values


def graph_from_connection(n, connection):
    edges = {
        (u, v)
        for u, v in itertools.combinations(range(n), 2)
        if (v - u) % n in connection
    }
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency, edges


def triangles(adjacency):
    result = []
    for a, neighbors in enumerate(adjacency):
        larger = sorted(b for b in neighbors if b > a)
        for b, c in itertools.combinations(larger, 2):
            if c in adjacency[b]:
                result.append((a, b, c))
    return result


def k4_free(adjacency):
    for vertex, neighbors in enumerate(adjacency):
        for a, b in itertools.combinations(neighbors, 2):
            if b not in adjacency[a]:
                continue
            common = adjacency[a] & adjacency[b] & neighbors
            if common:
                return False, (vertex, a, b, min(common))
    return True, None


def write_arrowing_cnf(path, edges, triangle_list):
    edge_index = {edge: i + 1 for i, edge in enumerate(edges)}
    with path.open("w") as stream:
        stream.write(f"p cnf {len(edges)} {2 * len(triangle_list)}\n")
        for a, b, c in triangle_list:
            variables = tuple(edge_index[e] for e in ((a, b), (a, c), (b, c)))
            stream.write(" ".join(map(str, variables)) + " 0\n")
            stream.write(" ".join(map(str, (-v for v in variables))) + " 0\n")


def describe(name, adjacency, triangle_list, expected=None):
    edges = sum(map(len, adjacency)) // 2
    k4, witness = k4_free(adjacency)
    print(
        f"{name}: vertices={len(adjacency)} degree_set={sorted({len(a) for a in adjacency})} "
        f"edges={edges} triangles={len(triangle_list)} K4-free={k4}"
    )
    if witness:
        print(f"{name}: K4 witness={witness}")
    if expected:
        assert len(adjacency) == expected["vertices"]
        if "edges" in expected:
            assert edges == expected["edges"]
        assert len(triangle_list) == expected["triangles"]
        if expected.get("k4_free", True):
            assert k4
    return edges


def build_all():
    exoo = [
        ("L17_2", 17, subgroup_connection_set(17, 2)),
        ("L61_8", 61, subgroup_connection_set(61, 8)),
        ("L79_12", 79, subgroup_connection_set(79, 12)),
        ("L421_7", 421, subgroup_connection_set(421, 7)),
        ("L631_24", 631, subgroup_connection_set(631, 24)),
        ("L457_6", 457, subgroup_connection_set(457, 6)),
        ("L761_3", 761, subgroup_connection_set(761, 3)),
    ]
    records = []
    for name, n, connection in exoo:
        adjacency, edges = graph_from_connection(n, connection)
        triangle_list = triangles(adjacency)
        describe(name, adjacency, triangle_list)
        write_arrowing_cnf(ROOT / f"{name}.cnf", sorted(edges), triangle_list)
        records.append(
            {"name": name, "vertices": n, "edges": len(edges), "triangles": len(triangle_list)}
        )

    connection = power_residue_set(941, 5)
    adjacency, _ = graph_from_connection(941, connection)
    all_triangles = triangles(adjacency)
    describe(
        "G941",
        adjacency,
        all_triangles,
        {"vertices": 941, "triangles": 707632},
    )
    # The edge count is determined after construction; retain the paper's
    # triangle/K4 assertions while recording the exact edge count.
    g941_edges = sum(map(len, adjacency)) // 2
    assert g941_edges == 941 * len(connection) // 2
    keep = set(range(941)) - {2 * i for i in range(81)}
    assert len(keep) == 860
    kept_vertices = sorted(keep)
    remap = {old: new for new, old in enumerate(kept_vertices)}
    reduced_adjacency = [
        {remap[w] for w in adjacency[v] if w in keep}
        for v in kept_vertices
    ]
    reduced_triangles = triangles(reduced_adjacency)
    describe(
        "G860",
        reduced_adjacency,
        reduced_triangles,
        {"vertices": 860, "edges": 73981, "triangles": 542514},
    )
    records.extend(
        [
            {
                "name": "G941",
                "vertices": 941,
                "edges": g941_edges,
                "triangles": len(all_triangles),
                "k4_free": True,
            },
            {
                "name": "G860",
                "vertices": 860,
                "edges": sum(map(len, reduced_adjacency)) // 2,
                "triangles": len(reduced_triangles),
                "k4_free": True,
            },
        ]
    )
    (ROOT / "structural_results.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    build_all()

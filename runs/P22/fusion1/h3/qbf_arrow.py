#!/usr/bin/env python3
"""Encode the H3 arrowing question as a single 2-QBF."""
from __future__ import annotations

import argparse
from pathlib import Path

from build_h3 import build, triangles_and_system
from k4free_max import edge_key, enumerate_k4s


ROOT = Path(__file__).resolve().parent


def triangle_edges(triangles):
    return [
        tuple(edge_key(*e) for e in ((a, b), (a, c), (b, c)))
        for a, b, c in triangles
    ]


def write_qdimacs(path, edges, triangles, k4s):
    edge_var = {e: i + 1 for i, e in enumerate(edges)}
    s_first = 1
    x_first = len(edges) + 1
    t_first = 2 * len(edges) + 1
    x_var = {e: x_first + i for i, e in enumerate(edges)}
    t_var = {i: t_first + i for i in range(len(triangles))}

    clauses = []
    for k4 in k4s:
        clauses.append(tuple(-edge_var[e] for e in k4))
    for i, tri in enumerate(triangles):
        t = t_var[i]
        a, b, c = (edge_var[e] for e in tri)
        xa, xb, xc = (x_var[e] for e in tri)
        clauses.extend(
            (
                (-t, a),
                (-t, b),
                (-t, c),
                (-t, -xa, xb),
                (-t, xa, -xb),
                (-t, -xb, xc),
                (-t, xb, -xc),
            )
        )
    clauses.append(tuple(t_var.values()))

    variables = 2 * len(edges) + len(triangles)
    with path.open("w") as out:
        out.write(f"p cnf {variables} {len(clauses)}\n")
        out.write(
            "e "
            + " ".join(str(s_first + i) for i in range(len(edges)))
            + " 0\n"
        )
        out.write(
            "a "
            + " ".join(str(x_first + i) for i in range(len(edges)))
            + " 0\n"
        )
        out.write(
            "e "
            + " ".join(str(t_first + i) for i in range(len(triangles)))
            + " 0\n"
        )
        for clause in clauses:
            out.write(" ".join(map(str, clause)) + " 0\n")
    return variables, len(clauses)


def self_check_empty_subgraph(edges, triangles):
    # With every s_e false, every present-clause forces t_T false.
    # Consequently the final all-t clause is false, independently of x.
    assert edges and triangles
    empty_s = {e: False for e in edges}
    all_zero_x = {e: False for e in edges}
    possible_t = []
    for tri in triangles:
        present = all(empty_s[e] for e in tri)
        monochromatic = len({all_zero_x[e] for e in tri}) == 1
        possible_t.append(present and monochromatic)
    assert not any(possible_t), "empty S/all-x must fail the matrix"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=ROOT / "h3_arrow.qdimacs"
    )
    args = parser.parse_args()

    graph = build()
    edges = graph["edges"]
    all_triangles, _ = triangles_and_system(graph)
    triangles = triangle_edges(all_triangles)
    k4s = enumerate_k4s(graph)
    assert len(edges) == 1008
    assert len(triangles) == 5376
    assert len(k4s) == 9576
    assert len(set(edges)) == len(edges)
    assert all(len(set(tri)) == 3 for tri in triangles)
    self_check_empty_subgraph(edges, triangles)
    variables, clauses = write_qdimacs(args.output, edges, triangles, k4s)
    assert variables == 7392
    assert clauses == 47209
    print(f"edges={len(edges)} triangles={len(triangles)} k4s={len(k4s)}")
    print(f"variables={variables} clauses={clauses}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

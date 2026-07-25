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


def verified_vertex_automorphisms(graph):
    try:
        from pynauty import Graph, autgrp
    except ImportError as exc:
        raise RuntimeError(
            "--symbreak requires pynauty; install it or omit --symbreak"
        ) from exc

    n = graph["n"]
    adjacency = {i: set(graph["adj"][i]) for i in range(n)}
    nauty_graph = Graph(number_of_vertices=n, adjacency_dict=adjacency)
    generators = autgrp(nauty_graph)[0]
    verified = []
    for permutation in generators:
        permutation = tuple(permutation)
        if len(permutation) != n or set(permutation) != set(range(n)):
            raise AssertionError("pynauty returned a non-permutation")
        for u in range(n):
            for v in range(n):
                assert (
                    (v in adjacency[u])
                    == (permutation[v] in adjacency[permutation[u]])
                ), "unverified graph automorphism"
        verified.append(permutation)
    return verified


def edge_actions(edges, vertex_automorphisms):
    edge_index = {edge: i for i, edge in enumerate(edges)}
    actions = []
    for permutation in vertex_automorphisms:
        action = []
        for u, v in edges:
            image = edge_key(permutation[u], permutation[v])
            assert image in edge_index
            action.append(edge_index[image])
        assert sorted(action) == list(range(len(edges)))
        actions.append(tuple(action))
    return actions


def add_lex_leader(clauses, s_vars, edge_action, next_var):
    """Add an outer-existential CNF for s <=_lex edge_action(s)."""
    prefix = list(range(next_var, next_var + len(s_vars) + 1))
    clauses.append((prefix[0],))
    for i, s in enumerate(s_vars):
        p = s_vars[edge_action[i]]
        q = prefix[i]
        q_next = prefix[i + 1]
        # If the previous coordinates agree, forbid s_i=1 and p_i=0.
        clauses.append((-q, -s, p))
        # q_next <-> (q and (s <-> p)).
        clauses.append((-q_next, q))
        clauses.append((-q_next, -s, p))
        clauses.append((-q_next, s, -p))
        clauses.append((-q, s, p, q_next))
        clauses.append((-q, -s, -p, q_next))
    return prefix, next_var + len(prefix)


def write_qdimacs(
    path, edges, triangles, k4s, vertex_automorphisms=None
):
    edge_var = {e: i + 1 for i, e in enumerate(edges)}
    s_first = 1
    x_first = len(edges) + 1
    t_first = 2 * len(edges) + 1
    x_var = {e: x_first + i for i, e in enumerate(edges)}
    t_var = {i: t_first + i for i in range(len(triangles))}

    clauses = []
    for k4 in k4s:
        clauses.append(tuple(-edge_var[e] for e in k4))
    s_vars = list(range(s_first, x_first))
    outer_vars = list(s_vars)
    next_var = 2 * len(edges) + len(triangles) + 1
    used_actions = []
    if vertex_automorphisms:
        used_actions = edge_actions(edges, vertex_automorphisms)
        for action in used_actions:
            prefix, next_var = add_lex_leader(
                clauses, s_vars, action, next_var
            )
            outer_vars.extend(prefix)
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

    variables = next_var - 1
    with path.open("w") as out:
        out.write(f"p cnf {variables} {len(clauses)}\n")
        out.write("e " + " ".join(map(str, outer_vars)) + " 0\n")
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
    return variables, len(clauses), len(used_actions), len(outer_vars)


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
    parser.add_argument(
        "--symbreak",
        action="store_true",
        help="add verified generator lex-leader constraints",
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
    automorphisms = (
        verified_vertex_automorphisms(graph) if args.symbreak else []
    )
    variables, clauses, used, outer_count = write_qdimacs(
        args.output,
        edges,
        triangles,
        k4s,
        automorphisms,
    )
    if not args.symbreak:
        assert variables == 7392
        assert clauses == 47209
    print(
        f"edges={len(edges)} triangles={len(triangles)} "
        f"k4s={len(k4s)} automorphisms={used}"
    )
    print(f"variables={variables} clauses={clauses}")
    print(f"outer_existential_variables={outer_count}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Extract and independently verify SAT witnesses for the three H3 subgraphs."""
from __future__ import annotations

import itertools
import json
import os
import subprocess
from pathlib import Path

from build_h3 import build, triangles_and_system


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "k4free_results.json"
TARGETS = {
    "max-triangle-ilp": ROOT / "k4free_max.cnf",
    "max-edge-ilp": ROOT / "k4free_max_cnfs" / "max-edge-ilp.cnf",
    "greedy-max-triangle": ROOT / "k4free_max_cnfs" / "greedy-max-triangle.cnf",
}


def parse_model(output, nv):
    literals = []
    for line in output.splitlines():
        if line.startswith("v "):
            literals.extend(int(x) for x in line.split()[1:] if x != "0")
    assert literals, "Kissat did not emit a model"
    assignment = {}
    for literal in literals:
        assert literal != 0
        variable = abs(literal)
        assert 1 <= variable <= nv
        assignment[variable] = literal > 0
    assert set(assignment) == set(range(1, nv + 1))
    return assignment


def parse_cnf(path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    assert header[:2] == ["p", "cnf"]
    nv, nc = int(header[2]), int(header[3])
    clauses = []
    for line in lines[1:]:
        if line:
            values = [int(x) for x in line.split()]
            assert values[-1] == 0
            clauses.append(tuple(values[:-1]))
    assert len(clauses) == nc
    return nv, nc, clauses


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def verify_formula(clauses, assignment):
    for clause in clauses:
        assert any(assignment[abs(lit)] == (lit > 0) for lit in clause)


def graph_triangles(adj):
    return [
        (a, b, c)
        for a, b, c in itertools.combinations(range(63), 3)
        if b in adj[a] and c in adj[a] and c in adj[b]
    ]


def count_k4s(adj, kept):
    count = 0
    for a, b, c, d in itertools.combinations(range(63), 4):
        if (
            b in adj[a]
            and c in adj[a]
            and d in adj[a]
            and c in adj[b]
            and d in adj[b]
            and d in adj[c]
        ):
            edges = (
                (a, b),
                (a, c),
                (a, d),
                (b, c),
                (b, d),
                (c, d),
            )
            if all(edge_key(*edge) in kept for edge in edges):
                count += 1
    return count


def main():
    data = json.loads(RESULTS.read_text())
    records = {record["subgraph"]: record for record in data["results"]}
    G = build()
    all_triangles, _ = triangles_and_system(G)
    base_adj = G["adj"]
    witnesses = {}
    path_env = os.environ.copy()
    path_env["PATH"] = f"{Path.home() / '.local/bin'}:{path_env.get('PATH', '')}"

    for name, cnf in TARGETS.items():
        record = records[name]
        expected_kept = {
            edge_key(*edge) for edge in record["kept_edges"]
        }
        assert expected_kept == set(map(tuple, record["kept_edges"]))
        assert expected_kept == set(sorted(expected_kept))

        kept = sorted(expected_kept)
        kept_adj = [set() for _ in range(63)]
        for u, v in kept:
            assert v in base_adj[u]
            kept_adj[u].add(v)
            kept_adj[v].add(u)

        actual_triangles = [
            tri
            for tri in all_triangles
            if all(edge_key(*edge) in expected_kept for edge in
                   ((tri[0], tri[1]), (tri[0], tri[2]), (tri[1], tri[2])))
        ]
        k4_count = count_k4s(base_adj, expected_kept)
        assert k4_count == 0

        nv, nc, clauses = parse_cnf(cnf)
        assert nv == len(kept)
        assert nc == 2 * len(actual_triangles)
        edge_to_var = {edge: i + 1 for i, edge in enumerate(kept)}
        expected_clauses = []
        for a, b, c in actual_triangles:
            variables = (
                edge_to_var[(a, b)],
                edge_to_var[(a, c)],
                edge_to_var[(b, c)],
            )
            expected_clauses.extend((variables, tuple(-x for x in variables)))
        assert sorted(clauses) == sorted(expected_clauses)

        proc = subprocess.run(
            ["kissat", "--quiet", str(cnf)],
            env=path_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert proc.returncode == 10, (name, proc.returncode, proc.stdout)
        assignment = parse_model(proc.stdout, nv)
        verify_formula(clauses, assignment)

        colors = {
            f"{u},{v}": int(assignment[var])
            for (u, v), var in edge_to_var.items()
        }
        mono_triangles = []
        for tri in actual_triangles:
            values = [
                assignment[edge_to_var[edge_key(*edge)]]
                for edge in ((tri[0], tri[1]), (tri[0], tri[2]), (tri[1], tri[2]))
            ]
            if values[0] == values[1] == values[2]:
                mono_triangles.append(tri)
        assert not mono_triangles
        used_vertices = sorted({v for edge in kept for v in edge})
        witnesses[name] = {
            "cnf": str(cnf),
            "vertices_used": used_vertices,
            "vertex_count": len(used_vertices),
            "edges": len(kept),
            "triangles": len(actual_triangles),
            "k4_count": k4_count,
            "colors": colors,
        }
        print(
            f"{name}: |V used|={len(used_vertices)} |E|={len(kept)} "
            f"#triangles={len(actual_triangles)} mono triangles = 0 "
            f"K4-free: yes PASS"
        )

    (ROOT / "witnesses.json").write_text(json.dumps(witnesses, indent=2))
    print("PASS: all three SAT witnesses independently verified")
    print(f"wrote {ROOT / 'witnesses.json'}")


if __name__ == "__main__":
    main()

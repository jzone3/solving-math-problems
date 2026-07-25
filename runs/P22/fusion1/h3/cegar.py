#!/usr/bin/env python3
"""CEGAR search for a K4-free subgraph of H3 arrowing all triangles."""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import time
from pathlib import Path

import pulp

from build_h3 import build, triangles_and_system
from k4free_max import enumerate_k4s, edge_key


ROOT = Path(__file__).resolve().parent


def triangle_edges(triangles):
    return [
        tuple(edge_key(*e) for e in ((a, b), (a, c), (b, c)))
        for a, b, c in triangles
    ]


def parse_model(output, nv):
    literals = []
    for line in output.splitlines():
        if line.startswith("v "):
            literals.extend(int(x) for x in line.split()[1:] if x != "0")
    assignment = {}
    for lit in literals:
        assert lit
        assignment[abs(lit)] = lit > 0
    assert set(assignment) == set(range(1, nv + 1))
    return assignment


def all_mono_indices(coloring, edge_index, triangles):
    mono = []
    for i, tri in enumerate(triangles):
        values = [coloring[edge_index[e]] for e in tri]
        if values[0] == values[1] == values[2]:
            mono.append(i)
    return mono


def direct_stats(kept, all_triangles, k4s):
    kept = set(kept)
    k4_count = sum(all(e in kept for e in k4) for k4 in k4s)
    actual = [tri for tri in all_triangles if all(e in kept for e in tri)]
    return k4_count, actual


def solve_cegar_ilp(edges, k4s, triangles, colorings, edge_index, seconds):
    model = pulp.LpProblem("H3_CEGAR", pulp.LpMaximize)
    x = {e: pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary)
         for i, e in enumerate(edges)}
    y = {i: pulp.LpVariable(f"y_{i}", cat=pulp.LpBinary)
         for i in range(len(triangles))}
    for i, k4 in enumerate(k4s):
        model += pulp.lpSum(x[e] for e in k4) <= 5, f"k4_{i}"
    for i, tri in enumerate(triangles):
        for e in tri:
            model += y[i] <= x[e], f"tri_{i}_{e[0]}_{e[1]}"
        model += pulp.lpSum(x[e] for e in tri) - 2 <= y[i], f"tri_lb_{i}"
    for ci, coloring in enumerate(colorings):
        mono = all_mono_indices(coloring, edge_index, triangles)
        assert mono
        model += pulp.lpSum(y[i] for i in mono) >= 1, f"color_{ci}"
    model += pulp.lpSum(y.values())
    solver = pulp.HiGHS(
        msg=False,
        timeLimit=seconds,
        mip_rel_gap=0.0,
    )
    started = time.monotonic()
    status_code = model.solve(solver)
    elapsed = time.monotonic() - started
    status = pulp.LpStatus[status_code]
    kept = [e for e in edges if (pulp.value(x[e]) or 0.0) >= 0.5]
    if status in {"Not Solved", "Undefined"} or not kept:
        return status, None, elapsed
    kept_set = set(kept)
    valid = all(
        any(all(e in kept_set for e in triangles[i])
            for i in all_mono_indices(c, edge_index, triangles))
        for c in colorings
    )
    if not valid:
        return "invalid-extraction", None, elapsed
    return status, sorted(kept), elapsed


def write_cnf(path, edges, triangles):
    edge_var = {e: i + 1 for i, e in enumerate(edges)}
    with path.open("w") as f:
        f.write(f"p cnf {len(edges)} {2 * len(triangles)}\n")
        for tri in triangles:
            a, b, c = (edge_var[e] for e in tri)
            f.write(f"{a} {b} {c} 0\n")
            f.write(f"{-a} {-b} {-c} 0\n")


def kissat(cnf, proof, seconds, env):
    if proof.exists():
        proof.unlink()
    started = time.monotonic()
    proc = subprocess.run(
        ["kissat", "--quiet", f"--time={seconds}", str(cnf), str(proof)],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.monotonic() - started
    if proc.returncode == 10:
        return "SAT", elapsed, proc.stdout
    if proc.returncode == 20:
        return "UNSAT", elapsed, proc.stdout
    if proc.returncode == 0:
        return "TIMEOUT", elapsed, proc.stdout
    return f"RC{proc.returncode}", elapsed, proc.stdout


def seed_colorings(root, edge_index):
    data = json.loads((root / "witnesses.json").read_text())
    colorings = []
    for record in data.values():
        coloring = [0] * len(edge_index)
        for key, value in record["colors"].items():
            u, v = map(int, key.split(","))
            coloring[edge_index[edge_key(u, v)]] = int(value)
        colorings.append(tuple(coloring))
    return list(dict.fromkeys(colorings))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ilp-time", type=int, default=90)
    parser.add_argument("--kissat-time", type=int, default=120)
    parser.add_argument("--wall-time", type=int, default=2400)
    parser.add_argument("--max-iterations", type=int, default=300)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()

    G = build()
    edges = G["edges"]
    edge_index = {e: i for i, e in enumerate(edges)}
    all_triangles, _ = triangles_and_system(G)
    all_edge_triangles = triangle_edges(all_triangles)
    triangles = all_edge_triangles
    k4s = enumerate_k4s(G)
    assert len(edges) == 1008 and len(triangles) == 5376

    state_path = ROOT / "colorings.json"
    if args.resume and state_path.exists():
        saved = json.loads(state_path.read_text())
        colorings = [tuple(map(int, c)) for c in saved]
        assert all(len(c) == len(edges) for c in colorings)
    else:
        colorings = seed_colorings(ROOT, edge_index)
    records = []
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    final_status = "undecided-progress"
    latest = None

    for iteration in range(args.max_iterations):
        if time.monotonic() - started >= args.wall_time:
            break
        ilp_status, kept, ilp_seconds = solve_cegar_ilp(
            edges, k4s, triangles, colorings, edge_index, args.ilp_time
        )
        if ilp_status == "Infeasible":
            final_status = "FALSE"
            rec = {
                "iteration": iteration,
                "colorings": len(colorings),
                "ilp_backend": "highs",
                "ilp_status": ilp_status,
                "ilp_seconds": ilp_seconds,
            }
            records.append(rec)
            print(f"{iteration} C={len(colorings)} ILP=INFEASIBLE decisive FALSE",
                  flush=True)
            break
        if kept is None:
            rec = {
                "iteration": iteration,
                "colorings": len(colorings),
                "ilp_status": ilp_status,
                "ilp_seconds": ilp_seconds,
                "error": "no feasible incumbent extracted",
            }
            records.append(rec)
            print(f"{iteration} C={len(colorings)} ILP={ilp_status} no incumbent",
                  flush=True)
            break

        k4_count, actual = direct_stats(kept, all_edge_triangles, k4s)
        assert k4_count == 0
        cnf = ROOT / f"cegar_{iteration:03d}.cnf"
        proof = ROOT / f"cegar_{iteration:03d}.drat"
        write_cnf(cnf, kept, actual)
        sat_status, sat_seconds, output = kissat(
            cnf, proof, args.kissat_time, env
        )
        rec = {
            "iteration": iteration,
            "colorings": len(colorings),
            "ilp_backend": "highs",
            "ilp_status": ilp_status,
            "ilp_seconds": ilp_seconds,
            "edges": len(kept),
            "triangles": len(actual),
            "k4_count": k4_count,
            "kept_edges": [list(e) for e in kept],
            "kissat": sat_status,
            "kissat_seconds": sat_seconds,
            "cnf": str(cnf),
            "proof": str(proof),
        }
        records.append(rec)
        latest = {"edges": kept, "triangles": actual, "cnf": str(cnf)}
        print(
            f"{iteration} C={len(colorings)} ILP={ilp_status} "
            f"|E|={len(kept)} T={len(actual)} K4={k4_count} "
            f"Kissat={sat_status} ilp={ilp_seconds:.1f}s sat={sat_seconds:.1f}s",
            flush=True,
        )
        if sat_status == "UNSAT":
            trim = subprocess.run(
                ["drat-trim", str(cnf), str(proof)],
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            rec["drat"] = trim.stdout
            if trim.returncode == 0 and "VERIFIED" in trim.stdout:
                final_status = "f<=63"
            else:
                final_status = "undecided-progress"
            break
        if sat_status != "SAT":
            break
        assignment = parse_model(output, len(kept))
        kept_index = {e: i for i, e in enumerate(kept)}
        coloring = [0] * len(edges)
        for e, i in kept_index.items():
            coloring[edge_index[e]] = int(assignment[i + 1])
        assert not all_mono_indices(coloring, edge_index, actual)
        colorings.append(tuple(coloring))
        colorings = list(dict.fromkeys(colorings))
        (ROOT / "colorings.json").write_text(json.dumps(colorings, indent=2))

    summary = {
        "status": final_status,
        "iterations": len(records),
        "colorings": len(colorings),
        "wall_seconds": time.monotonic() - started,
        "edge_order": [list(e) for e in edges],
        "ilp_backend": "highs",
        "ilp_time_limit": args.ilp_time,
        "kissat_time_limit": args.kissat_time,
        "wall_time_limit": args.wall_time,
        "records": records,
        "last": latest,
    }
    if latest is not None:
        summary["last"]["k4_free"] = True
    summary["all_candidates_k4_free"] = all(
        r.get("k4_count") == 0 for r in records if "k4_count" in r
    )
    summary["kissat_results"] = [r.get("kissat") for r in records]
    (ROOT / "cegar_results.json").write_text(json.dumps(summary, indent=2))
    (ROOT / "colorings.json").write_text(json.dumps(colorings, indent=2))
    print(
        f"final status={final_status} iterations={len(records)} "
        f"C={len(colorings)} wall={summary['wall_seconds']:.1f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()

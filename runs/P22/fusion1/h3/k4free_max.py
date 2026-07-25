#!/usr/bin/env python3
"""Search for triangle-rich K4-free subgraphs of H_3."""
from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import subprocess
import time
from pathlib import Path

import pulp

from build_h3 import build, triangles_and_system


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def enumerate_k4s(G):
    adj = G["adj"]
    k4s = []
    for a, b, c, d in itertools.combinations(range(63), 4):
        if (
            b in adj[a]
            and c in adj[a]
            and d in adj[a]
            and c in adj[b]
            and d in adj[b]
            and d in adj[c]
        ):
            k4s.append(
                tuple(
                    edge_key(*e)
                    for e in ((a, b), (a, c), (a, d), (b, c), (b, d), (c, d))
                )
            )
    assert len(k4s) == 9576
    return k4s


def triangle_edges(triangles):
    return [
        tuple(edge_key(*e) for e in ((a, b), (a, c), (b, c)))
        for a, b, c in triangles
    ]


def solve_ilp(
    edges,
    k4s,
    triangles,
    mode,
    seconds,
    log_path,
    initial_kept=None,
    backend="cbc",
    objective_floor=None,
):
    model = pulp.LpProblem(
        f"H3_K4free_{mode}",
        pulp.LpMaximize,
    )
    x = {
        e: pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary)
        for i, e in enumerate(edges)
    }
    for i, k4 in enumerate(k4s):
        model += pulp.lpSum(x[e] for e in k4) <= 5, f"k4_{i}"

    z = {}
    if mode == "triangles":
        for i, tri in enumerate(triangles):
            z[i] = pulp.LpVariable(f"z_{i}", cat=pulp.LpBinary)
            for e in tri:
                model += z[i] <= x[e], f"tri_{i}_{e[0]}_{e[1]}"
            model += (
                z[i] >= pulp.lpSum(x[e] for e in tri) - 2
            ), f"tri_lower_{i}"
        model += pulp.lpSum(z.values())
        if objective_floor is not None:
            model += pulp.lpSum(z.values()) >= objective_floor, "objective_floor"
    elif mode == "edges":
        model += pulp.lpSum(x.values())
    else:
        raise ValueError(mode)

    if initial_kept is not None:
        initial = set(initial_kept)
        for e in edges:
            x[e].setInitialValue(1 if e in initial else 0)
        if mode == "triangles":
            for i, tri in enumerate(triangles):
                z[i].setInitialValue(1 if all(e in initial for e in tri) else 0)

    if backend == "highs":
        solver = pulp.HiGHS(
            msg=True,
            timeLimit=seconds,
            logPath=str(log_path),
            mip_rel_gap=0.0,
            warmStart=initial_kept is not None,
        )
    elif backend == "cbc":
        solver = pulp.PULP_CBC_CMD(
            msg=True,
            timeLimit=seconds,
            logPath=str(log_path),
            warmStart=initial_kept is not None,
        )
    else:
        raise ValueError(backend)
    started = time.monotonic()
    status_code = model.solve(solver)
    elapsed = time.monotonic() - started
    status = pulp.LpStatus[status_code]
    if elapsed >= seconds - 1 and status == "Optimal":
        status = "Feasible (time limit)"
    kept = [e for e in edges if (pulp.value(x[e]) or 0.0) >= 0.5]
    # CBC can leave the PuLP variable values at a non-incumbent terminal
    # relaxation after a time-limit exit.  Never pass an infeasible extraction
    # downstream; retain the known feasible warm start in that case.
    if initial_kept is not None:
        kept_set = set(kept)
        feasible = all(not all(e in kept_set for e in k4) for k4 in k4s)
        if not feasible:
            kept = sorted(initial_kept)
    kept_set = set(kept)
    if mode == "triangles":
        objective = sum(all(e in kept_set for e in tri) for tri in triangles)
    else:
        objective = len(kept)
    if (
        initial_kept is not None
        and objective_floor is not None
        and objective < objective_floor
    ):
        kept = sorted(initial_kept)
        kept_set = set(kept)
        objective = (
            sum(all(e in kept_set for e in tri) for tri in triangles)
            if mode == "triangles"
            else len(kept)
        )
    return {
        "mode": mode,
        "status": status,
        "objective": None if objective is None else float(objective),
        "kept": kept,
        "seconds": elapsed,
    }


def graph_stats(kept, all_triangles, k4s):
    kept_set = set(kept)
    adj = [set() for _ in range(63)]
    for u, v in kept:
        adj[u].add(v)
        adj[v].add(u)
    k4_count = 0
    for k4 in k4s:
        if all(e in kept_set for e in k4):
            k4_count += 1
    assert k4_count == 0
    actual_triangles = [
        tri for tri in all_triangles if all(e in kept_set for e in tri)
    ]
    return k4_count, actual_triangles


def write_cnf(path, kept, triangles):
    edge_var = {e: i + 1 for i, e in enumerate(sorted(kept))}
    clauses = []
    for tri in triangles:
        a, b, c = (edge_var[e] for e in tri)
        clauses.extend(((a, b, c), (-a, -b, -c)))
    with path.open("w") as f:
        f.write(f"p cnf {len(edge_var)} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


def kissat(cnf, proof, seconds):
    if proof.exists():
        proof.unlink()
    started = time.monotonic()
    try:
        proc = subprocess.run(
            [
                "kissat",
                "--quiet",
                f"--time={seconds}",
                str(cnf),
                str(proof),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=seconds + 15,
        )
        elapsed = time.monotonic() - started
        if proc.returncode == 10:
            result = "SAT"
        elif proc.returncode == 20:
            result = "UNSAT"
        elif proc.returncode == 0 and elapsed >= seconds - 1:
            result = "TIMEOUT"
        else:
            result = f"RC{proc.returncode}"
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        result = "TIMEOUT"
    return result, elapsed


def greedy_max_triangles(edges, k4s, triangles):
    """Delete edges greedily, preferring deletions that lose few triangles."""
    kept = set(edges)
    while True:
        active_k4 = [k for k in k4s if all(e in kept for e in k)]
        if not active_k4:
            break
        incidence = {}
        for k4 in active_k4:
            for e in k4:
                incidence[e] = incidence.get(e, 0) + 1
        tri_loss = {
            e: sum(all(other in kept for other in tri) for tri in triangles if e in tri)
            for e in incidence
        }
        chosen = max(
            incidence,
            key=lambda e: (incidence[e] / (1 + tri_loss[e]), incidence[e], -tri_loss[e]),
        )
        kept.remove(chosen)
    return sorted(kept)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=int, default=900)
    parser.add_argument("--kissat-time", type=int, default=300)
    parser.add_argument("--seed", type=int, default=32263)
    parser.add_argument("--out", type=Path, default=Path("k4free_results.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    cnf_dir = root / "k4free_max_cnfs"
    cnf_dir.mkdir(exist_ok=True)

    G = build()
    all_edges = G["edges"]
    all_tris, nondeg = triangles_and_system(G)
    all_edge_tris = triangle_edges(all_tris)
    nondeg_edge_tris = triangle_edges(nondeg)
    k4s = enumerate_k4s(G)
    assert len(all_edges) == 1008
    assert len(nondeg_edge_tris) == 3024

    print(
        f"constructed H3: edges={len(all_edges)} all_triangles={len(all_tris)} "
        f"nondeg_triangles={len(nondeg)} K4s={len(k4s)}",
        flush=True,
    )
    results = []
    feasible_seed = greedy_max_triangles(all_edges, k4s, nondeg_edge_tris)
    seed_k4, seed_triangles = graph_stats(feasible_seed, all_edge_tris, k4s)
    assert seed_k4 == 0
    print(
        f"feasible warm start: edges={len(feasible_seed)} "
        f"triangles={len(seed_triangles)}",
        flush=True,
    )

    candidates = [
        (
            "max-triangle-ilp",
            solve_ilp(
                all_edges,
                k4s,
                nondeg_edge_tris,
                "triangles",
                args.time_limit,
                root / "k4free_max_triangles.cbc.log",
                feasible_seed,
            ),
        ),
        (
            "max-edge-ilp",
            solve_ilp(
                all_edges,
                k4s,
                nondeg_edge_tris,
                "edges",
                args.time_limit,
                root / "k4free_max_edges.cbc.log",
                feasible_seed,
            ),
        ),
    ]
    candidates.append(
        (
            "greedy-max-triangle",
            {
                "mode": "greedy",
                "status": "heuristic",
                "objective": None,
                "kept": greedy_max_triangles(
                    all_edges, k4s, nondeg_edge_tris
                ),
                "seconds": 0.0,
            },
        )
    )

    for name, solution in candidates:
        kept = sorted(solution["kept"])
        k4_count, actual_triangles = graph_stats(kept, all_edge_tris, k4s)
        actual_nondeg = [t for t in actual_triangles if t in set(nondeg_edge_tris)]
        degenerate_count = len(actual_triangles) - len(actual_nondeg)
        if name == "max-triangle-ilp":
            cnf = root / "k4free_max.cnf"
            proof = root / "k4free_max.drat"
        else:
            cnf = cnf_dir / f"{name}.cnf"
            proof = cnf_dir / f"{name}.drat"
        write_cnf(cnf, kept, actual_triangles)
        sat_status, sat_seconds = kissat(cnf, proof, args.kissat_time)
        record = {
            "subgraph": name,
            "ilp_status": solution["status"],
            "ilp_optimum_certified": solution["status"] == "Optimal",
            "ilp_objective": solution["objective"],
            "ilp_seconds": solution["seconds"],
            "edges": len(kept),
            "triangles": len(actual_triangles),
            "nondeg_triangles": len(actual_nondeg),
            "degenerate_triangles": degenerate_count,
            "k4_count": k4_count,
            "k4_free_assert": k4_count == 0,
            "kissat": sat_status,
            "kissat_seconds": sat_seconds,
            "cnf": str(cnf),
            "proof": str(proof),
            "kept_edges": kept,
        }
        results.append(record)
        args.out.write_text(json.dumps(results, indent=2))
        print(
            f"{name}: |E|={len(kept)} triangles={len(actual_triangles)} "
            f"nondeg={len(actual_nondeg)} degenerate={degenerate_count} "
            f"{sat_status} {sat_seconds:.3f}s K4-free={k4_count == 0}",
            flush=True,
        )
        if sat_status == "UNSAT":
            print(
                f"UNSAT FOUND: subgraph={name} cnf={cnf} proof={proof}",
                flush=True,
            )
            return

    summary = {
        "instance": {
            "vertices": 63,
            "edges": len(all_edges),
            "k4s": len(k4s),
            "nondeg_triangles": len(nondeg),
        },
        "results": results,
    }
    args.out.write_text(json.dumps(summary, indent=2))
    print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()

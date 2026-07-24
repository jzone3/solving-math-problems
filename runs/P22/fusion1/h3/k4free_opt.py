#!/usr/bin/env python3
"""Bounded backend comparison for the H3 max-nondegenerate-triangle ILP."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from build_h3 import build, triangles_and_system
from k4free_max import (
    enumerate_k4s,
    graph_stats,
    greedy_max_triangles,
    solve_ilp,
    triangle_edges,
    write_cnf,
)


ROOT = Path(__file__).resolve().parent


def main():
    G = build()
    edges = G["edges"]
    all_triangles, nondeg = triangles_and_system(G)
    all_edge_triangles = triangle_edges(all_triangles)
    nondeg_edge_triangles = triangle_edges(nondeg)
    k4s = enumerate_k4s(G)
    seed = greedy_max_triangles(edges, k4s, nondeg_edge_triangles)

    # A short CBC restart provides a current baseline; HiGHS receives the
    # known feasible 682-triangle incumbent as a MIP start.
    runs = [
        ("cbc-900", "cbc", 900),
        ("highs-1200", "highs", 1200),
    ]
    records = []
    for label, backend, limit in runs:
        log = ROOT / f"k4free_opt_{label}.log"
        started = time.monotonic()
        sol = solve_ilp(
            edges,
            k4s,
            nondeg_edge_triangles,
            "triangles",
            limit,
            log,
            seed,
            backend=backend,
        )
        elapsed = time.monotonic() - started
        kept = sorted(sol["kept"])
        k4_count, actual = graph_stats(kept, all_edge_triangles, k4s)
        cnf = ROOT / f"k4free_opt_{label}.cnf"
        write_cnf(cnf, kept, actual)
        kissat_started = time.monotonic()
        proc = subprocess.run(
            ["kissat", "--quiet", "--time=300", str(cnf)],
            env={"PATH": f"{Path.home() / '.local/bin'}:{__import__('os').environ.get('PATH', '')}"},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        kissat_seconds = time.monotonic() - kissat_started
        kissat_status = (
            "SAT" if proc.returncode == 10
            else "UNSAT" if proc.returncode == 20
            else "TIMEOUT" if proc.returncode == 0
            else f"RC{proc.returncode}"
        )
        record = {
            "backend": backend,
            "label": label,
            "time_limit": limit,
            "solver_status": sol["status"],
            "best_lower_bound": sol["objective"],
            "elapsed": elapsed,
            "edges": len(kept),
            "triangles": len(actual),
            "nondeg_triangles": sum(
                all(e in set(kept) for e in tri) for tri in nondeg_edge_triangles
            ),
            "k4_count": k4_count,
            "k4_free": k4_count == 0,
            "cnf": str(cnf),
            "kissat": kissat_status,
            "kissat_seconds": kissat_seconds,
            "kissat_output": proc.stdout,
            "log": str(log),
        }
        records.append(record)
        print(
            f"{label}: solver={sol['status']} LB={sol['objective']} "
            f"|E|={len(kept)} triangles={len(actual)} "
            f"K4-free={k4_count == 0} kissat={kissat_status} "
            f"{kissat_seconds:.3f}s",
            flush=True,
        )
        if kissat_status == "UNSAT":
            print(f"UNSAT FOUND: {cnf}", flush=True)
            break

    out = {
        "certified_optimal": any(r["solver_status"] == "Optimal" for r in records),
        "records": records,
        "best_incumbent": max(r["best_lower_bound"] for r in records),
    }
    (ROOT / "k4free_opt.json").write_text(json.dumps(out, indent=2))
    print(f"wrote {ROOT / 'k4free_opt.json'}")


if __name__ == "__main__":
    main()

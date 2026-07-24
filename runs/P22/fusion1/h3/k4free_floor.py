#!/usr/bin/env python3
"""Short HiGHS restart with the known 682-triangle incumbent enforced."""
import json
import time
from pathlib import Path

from build_h3 import build, triangles_and_system
from k4free_max import (
    enumerate_k4s,
    graph_stats,
    greedy_max_triangles,
    solve_ilp,
    triangle_edges,
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
    started = time.monotonic()
    solution = solve_ilp(
        edges,
        k4s,
        nondeg_edge_triangles,
        "triangles",
        600,
        ROOT / "k4free_opt_highs_floor-600.log",
        seed,
        backend="highs",
        objective_floor=682,
    )
    kept = sorted(solution["kept"])
    k4_count, actual = graph_stats(kept, all_edge_triangles, k4s)
    result = {
        "solver": "highs",
        "time_limit": 600,
        "solver_status": solution["status"],
        "best_lower_bound": solution["objective"],
        "elapsed": time.monotonic() - started,
        "edges": len(kept),
        "triangles": len(actual),
        "nondeg_triangles": sum(
            all(e in set(kept) for e in tri) for tri in nondeg_edge_triangles
        ),
        "k4_count": k4_count,
        "k4_free": k4_count == 0,
        "objective_floor": 682,
        "kept_edges": kept,
        "log": str(ROOT / "k4free_opt_highs_floor-600.log"),
    }
    (ROOT / "k4free_floor.json").write_text(json.dumps(result, indent=2))
    print(result)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Structure-aware cube generation and measurement for the G127 CNF.

The local constraints are the NAE form of the triangle clauses restricted to
the edges induced by a greedily grown vertex set W.  Counts are obtained by a
small DPLL/#SAT routine with unit propagation; samples are local satisfying
assignments, not arbitrary cubes that can immediately contradict a triangle.
"""
from __future__ import annotations

import argparse
import json
import random
from functools import lru_cache
from pathlib import Path

P = 127
CUBIC = {pow(x, 3, P) for x in range(1, P)}
ADJ = [set((u + c) % P for c in CUBIC) for u in range(P)]
EDGES_STAR = sorted((0, c) for c in CUBIC)
EDGES_REST = sorted(
    (u, v) for u in range(1, P) for v in ADJ[u] if u < v
)
GLOBAL_EDGE_VAR = {e: i + 1 for i, e in enumerate(EDGES_STAR + EDGES_REST)}
assert len(GLOBAL_EDGE_VAR) == 2667


def all_triangles():
    out = []
    for u in range(P):
        for v in ADJ[u]:
            if u < v:
                for w in ADJ[u] & ADJ[v]:
                    if w > v:
                        out.append((u, v, w))
    return out


TRIANGLES = all_triangles()


def grow_sets():
    """Return a deterministic dense greedy growth sequence."""
    W = set(TRIANGLES[0])
    result = [frozenset(W)]
    while len(W) < 20:
        best = max(
            (
                (
                    sum(x in t and set(t) - {x} <= W for t in TRIANGLES),
                    sum(x in ADJ[y] for y in W),
                    -x,
                ),
                x,
            )
            for x in range(P)
            if x not in W
        )
        W.add(best[1])
        result.append(frozenset(W))
    return result


def region_data(W):
    edges = sorted((u, v) for u in W for v in W if u < v and v in ADJ[u])
    edge_index = {e: i for i, e in enumerate(edges)}
    triangles = []
    for t in TRIANGLES:
        if set(t) <= W:
            triangles.append(
                tuple(
                    edge_index[(min(a, b), max(a, b))]
                    for a, b in ((t[0], t[1]), (t[0], t[2]), (t[1], t[2]))
                )
            )
    return edges, triangles


def local_counter(nvars, triangles, fixed, do_count=True):
    """Count NAE-satisfying assignments and retain one randomized model."""
    occurrences = [[] for _ in range(nvars)]
    for tri in triangles:
        for v in tri:
            occurrences[v].append(tri)

    def propagate(a):
        changed = True
        while changed:
            changed = False
            for x, y, z in triangles:
                vals = (a[x], a[y], a[z])
                assigned = [v for v in vals if v >= 0]
                if len(assigned) == 3:
                    if assigned[0] == assigned[1] == assigned[2]:
                        return False
                elif len(assigned) == 2 and assigned[0] == assigned[1]:
                    v = next(i for i in (x, y, z) if a[i] < 0)
                    forced = 1 - assigned[0]
                    if a[v] >= 0 and a[v] != forced:
                        return False
                    if a[v] < 0:
                        a[v] = forced
                        changed = True
        return True

    def choose(a):
        unassigned = [i for i, v in enumerate(a) if v < 0]
        return max(unassigned, key=lambda i: len(occurrences[i])) if unassigned else None

    @lru_cache(maxsize=None)
    def count(state):
        a = list(state)
        if not propagate(a):
            return 0
        v = choose(a)
        if v is None:
            return 1
        total = 0
        for value in (0, 1):
            b = a[:]
            b[v] = value
            total += count(tuple(b))
        return total

    initial = [-1] * nvars
    for v, value in fixed.items():
        initial[v] = value
    total = count(tuple(initial)) if do_count else None

    # Randomized model generation uses the same propagator, with random
    # branching.  It is intentionally independent of the count cache.
    def random_model(rng):
        def search(a):
            if not propagate(a):
                return None
            v = choose(a)
            if v is None:
                return tuple(a)
            values = [0, 1]
            rng.shuffle(values)
            for value in values:
                b = a[:]
                b[v] = value
                result = search(b)
                if result is not None:
                    return result
            return None

        return search(initial[:])

    return total, random_model, count.cache_info()


def build_table(targets):
    chosen = []
    for target in targets:
        candidates = []
        for W in grow_sets():
            edges, triangles = region_data(W)
            candidates.append((abs(len(edges) - target), len(edges), W, edges, triangles))
        item = min(candidates, key=lambda x: (x[0], x[1]))
        chosen.append(item)
    return chosen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", default="15,22,30,40")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--skip-count", action="store_true")
    parser.add_argument("--seed", type=int, default=22127)
    parser.add_argument("--out", type=Path, default=Path("dense_cube_table.json"))
    args = parser.parse_args()
    targets = [int(x) for x in args.targets.split(",") if x]
    rng = random.Random(args.seed)
    rows = []
    for target, item in zip(targets, build_table(targets)):
        _, m, W, edges, triangles = item
        fixed = {}
        for i, e in enumerate(edges):
            if e == (0, 1):
                fixed[i] = 1
        if args.skip_count:
            total, model, cache_info = None, None, "skipped"
            # Build the randomized local model generator without spending time
            # on the #SAT count.
            total, model, cache_info = local_counter(len(edges), triangles, fixed, False)
        else:
            total, model, cache_info = local_counter(len(edges), triangles, fixed)
        samples = []
        while len(samples) < args.samples:
            assignment = model(rng)
            if assignment is None:
                raise RuntimeError("failed to generate a local satisfying assignment")
            global_vars = [GLOBAL_EDGE_VAR[tuple(e)] for e in edges]
            if len(edges) == 30:
                assert set(global_vars) != set(range(1, 31))
                if len(samples) == 0:
                    print(
                        "sanity local->global:",
                        [
                            (i, edges[i], global_vars[i])
                            for i in range(min(5, len(edges)))
                        ],
                    )
            samples.append(
                {
                    "lits": [
                        global_vars[i] if value else -global_vars[i]
                        for i, value in enumerate(assignment)
                    ],
                    "edges": [list(e) for e in edges],
                    "global_vars": global_vars,
                    "vertices": sorted(W),
                }
            )
        rows.append(
            {
                "target_edges": target,
                "vertices": sorted(W),
                "edges": len(edges),
                "induced_triangles": len(triangles),
                "surviving_cubes": total,
                "all_cubes": 1 << len(edges),
                "compression_ratio": None if total is None else (1 << len(edges)) / total,
                "count_cache": str(cache_info),
                "samples": samples,
            }
        )
        compression = "unknown" if total is None else f"{((1 << len(edges)) / total):.3f}x"
        print(
            f"target={target} |W|={len(W)} |S|={len(edges)} "
            f"induced_triangles={len(triangles)} surviving={total} "
            f"of={1 << len(edges)} compression={compression}"
        )
    args.out.write_text(json.dumps(rows, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

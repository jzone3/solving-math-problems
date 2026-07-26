# Provenance: new Stage-7 fixed-pattern A minimizer using stage4.py and cegar.py.
"""Benchmark the A-side minimizers against the fixed T=0 S135 patterns."""

from __future__ import annotations

import argparse
import pickle
import random
import time
from collections import Counter

from pysat.examples.hitman import Hitman
from pysat.solvers import Solver

import cegar
import stage4


def fixed_a(L, a_edges, patterns):
    return cegar.cached_test(L, a_edges, patterns)


class AIncremental:
    """Incremental fixed-P oracle with gated induced-subgraph edges."""

    def __init__(self, vertices, a_edges, patterns):
        self.vertices = sorted(vertices)
        self.idx = {v: i for i, v in enumerate(self.vertices)}
        self.n = len(self.vertices)
        self.solver = Solver(name="glucose4")
        for i in range(self.n):
            vars_i = [4 * i + c + 1 for c in range(4)]
            self.solver.add_clause(vars_i)
            for c in range(4):
                for d in range(c):
                    self.solver.add_clause([-vars_i[c], -vars_i[d]])
        next_var = 4 * self.n + 1
        self.gates = []
        for u, v in a_edges:
            if u not in self.idx or v not in self.idx:
                continue
            gate = next_var
            next_var += 1
            self.gates.append((gate, u, v))
            iu, iv = self.idx[u], self.idx[v]
            for c in range(4):
                self.solver.add_clause([
                    -gate, -(4 * iu + c + 1), -(4 * iv + c + 1)
                ])
        for vs, cs in patterns:
            if all(v in self.idx for v in vs):
                self.solver.add_clause([
                    -(4 * self.idx[v] + c + 1)
                    for v, c in zip(vs, cs)
                ])

    def forcing(self, vertices):
        active = set(vertices)
        assumptions = [
            gate for gate, u, v in self.gates
            if u in active and v in active
        ]
        return not self.solver.solve(assumptions=assumptions)

    def close(self):
        self.solver.delete()


def incremental_greedy(
    L, vertices, a_edges, patterns, preserve, seed=1, max_queries=None
):
    oracle = AIncremental(vertices, a_edges, patterns)
    rng = random.Random(seed)
    current = set(L)
    try:
        queries = 0
        while True:
            changed = False
            order = list(current - set(preserve))
            rng.shuffle(order)
            for v in order:
                if max_queries is not None and queries >= max_queries:
                    return current, queries, True
                trial = current - {v}
                queries += 1
                if oracle.forcing(trial):
                    current = trial
                    changed = True
            if not changed:
                return current, queries, False
    finally:
        oracle.close()


def core_jump(L, a_edges, patterns, preserve, seed=1, max_queries=None):
    """Alternate DRAT core reduction and greedy deletion to a fixpoint."""
    current = set(L)
    trajectory = []
    while True:
        before = len(current)
        current = cegar.core_reduce(current, a_edges, patterns, preserve)
        core_size = len(current)
        current, queries, capped = incremental_greedy(
            current, set(v for e in a_edges for v in e),
            a_edges, patterns, preserve, seed=seed,
            max_queries=max_queries,
        )
        trajectory.append({
            "before": before,
            "core": core_size,
            "after": len(current),
            "queries": queries,
            "capped": capped,
        })
        if capped:
            return current, trajectory
        if len(current) >= before:
            return current, trajectory


def orbit_greedy(L, a_pool, points, a_edges, patterns, preserve, seed=1):
    """Delete complete lattice symmetry orbits when fixed-P remains UNSAT."""
    groups = stage4.a_orbits(points, a_pool)
    rng = random.Random(seed)
    current = set(L)
    history = []
    while True:
        candidates = [
            g for g in groups
            if g <= current and not (g & set(preserve))
        ]
        rng.shuffle(candidates)
        changed = False
        for group in candidates:
            trial = current - group
            if fixed_a(trial, a_edges, patterns):
                current = trial
                history.append(len(group))
                changed = True
        if not changed:
            return current, history


def ihs_lower_bound(patterns):
    """Solve the endpoint hitting set exactly as a structural lower bound.

    Every retained fixed-P pattern must have all of its endpoints present;
    singleton constraints therefore give a sound, deliberately conservative
    lower bound for any candidate that still means the same P.
    """
    endpoints = sorted({v for vs, _ in patterns for v in vs})
    with Hitman(bootstrap_with=[[v] for v in endpoints], htype="sorted") as hit:
        solution = hit.get()
    return len(solution), solution


def load_case(cache, pattern_pickle):
    points, labels, metadata, a_pool, b_pool, rec_a, rec_b = cegar.side_sets(
        cache, "record"
    )
    result = pickle.load(open(pattern_pickle, "rb"))
    if isinstance(result, dict):
        patterns = list(result["patterns"])
    elif isinstance(result, list) and result and isinstance(result[0], dict):
        patterns = list(result[0]["patterns"])
    elif isinstance(result, tuple):
        patterns = list(result[1])
    else:
        patterns = list(result)
    return (
        points, labels["AA"], a_pool, rec_a, patterns,
        metadata, labels,
    )


def run(cache, pattern_pickle, seeds=(1, 2, 3)):
    points, a_edges, a_pool, parts_L, patterns, metadata, labels = load_case(
        cache, pattern_pickle
    )
    preserve = {v for vs, _ in patterns for v in vs}
    lower, lower_set = ihs_lower_bound(patterns)
    outputs = []
    starts = {
        "parts_L374": set(parts_L),
    }
    # Stage-6's grown/core-reduced candidate is supplied separately by caller.
    for name, initial in starts.items():
        for seed in seeds:
            started = time.time()
            result, trajectory = core_jump(
                initial, a_edges, patterns, preserve, seed=seed
            )
            orbit_result, orbit_history = orbit_greedy(
                result, a_pool, points, a_edges, patterns, preserve, seed=seed
            )
            outputs.append({
                "start": name,
                "seed": seed,
                "A": len(result),
                "orbit_A": len(orbit_result),
                "trajectory": trajectory,
                "orbit_history": orbit_history,
                "seconds": time.time() - started,
            })
            print(outputs[-1], flush=True)
    return {
        "outputs": outputs,
        "patterns": patterns,
        "orders": dict(Counter(len(vs) for vs, _ in patterns)),
        "preserve": sorted(preserve),
        "ihs_lower_bound": lower,
        "ihs_solution": lower_set,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("patterns")
    ap.add_argument("--grown-ids", required=True)
    ap.add_argument("--starts-pkl")
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-queries", type=int)
    args = ap.parse_args()
    points, a_edges, a_pool, parts_L, patterns, metadata, labels = load_case(
        args.cache, args.patterns
    )
    preserve = {v for vs, _ in patterns for v in vs}
    lower, lower_set = ihs_lower_bound(patterns)
    outputs = []
    if args.starts_pkl:
        source = pickle.load(open(args.starts_pkl, "rb"))
        if isinstance(source, dict):
            starts = {"supplied": set(source["L"])}
        elif isinstance(source, list):
            starts = {"supplied": set(source[0]["L"])}
        else:
            starts = {"supplied": set(source)}
    else:
        grown = pickle.load(open(args.grown_ids, "rb"))
        if isinstance(grown, dict):
            grown_L = set(grown["L"])
        else:
            grown_L = set(grown[0]["L"])
        starts = {"parts_L374": set(parts_L), "stage6_A1080": grown_L}
    for name, initial in starts.items():
        for seed in [int(x) for x in args.seeds.split(",")]:
            started = time.time()
            result, trajectory = core_jump(
                initial, a_edges, patterns, preserve, seed=seed,
                max_queries=args.max_queries,
            )
            orbit_result, orbit_history = orbit_greedy(
                result, a_pool, points, a_edges, patterns, preserve, seed=seed
            )
            row = {
                "start": name,
                "seed": seed,
                "A": len(result),
                "orbit_A": len(orbit_result),
                "trajectory": trajectory,
                "orbit_history": orbit_history,
                "seconds": time.time() - started,
                "A_ids": sorted(orbit_result),
            }
            outputs.append(row)
            print({
                k: row[k] for k in
                ("start", "seed", "A", "orbit_A", "trajectory",
                 "orbit_history", "seconds")
            }, flush=True)
    out = {
        "outputs": outputs,
        "patterns": patterns,
        "orders": dict(Counter(len(vs) for vs, _ in patterns)),
        "preserve": sorted(preserve),
        "ihs_lower_bound": lower,
        "ihs_solution": lower_set,
    }
    pickle.dump(out, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()

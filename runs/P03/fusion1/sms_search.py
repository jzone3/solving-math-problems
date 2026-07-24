#!/usr/bin/env python3
"""SAT-modulo-properties search over reduced cubic DAGs.

The SAT layer proposes labelled topological-order representatives.  Every
proposal is checked by exact tau/CEGAR code; its complete edge assignment is
then blocked.  No isomorphism rejection is used, so a completed UNSAT result
is a closure of the encoded labelled class (and hence of the corresponding
unlabelled class).  Runs stopped by a budget are explicitly partial.
"""
import argparse
import itertools
import json
import os
import time

from pysat.formula import IDPool
from pysat.solvers import Glucose4

from harness import (has_k_disjoint_dijoins, is_planar,
                     is_source_sink_connected, rho, tau as harness_tau)
from structured_search import cegar_count, tau_mincut


def exact_degree(solver, lits, degree, guard=None):
    """Add an exact-cardinality constraint, optionally guarded by a literal."""
    prefix = [] if guard is None else [-guard]
    if degree == 0:
        for lit in lits:
            solver.add_clause(prefix + [-lit])
        return
    for subset in itertools.combinations(lits, degree + 1):
        solver.add_clause(prefix + [-x for x in subset])
    need = len(lits) - degree + 1
    for subset in itertools.combinations(lits, need):
        solver.add_clause(prefix + list(subset))


def at_least(solver, lits, degree):
    need = len(lits) - degree + 1
    for subset in itertools.combinations(lits, need):
        solver.add_clause(list(subset))


def build_solver(n, sources, sinks):
    pool = IDPool()
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    x = {e: pool.id(("e", e)) for e in edges}
    role_a = {}
    role_b = {}
    solver = Glucose4()

    internal = [v for v in range(n) if v not in sources and v not in sinks]
    a = len(internal) // 2
    for v in internal:
        role_a[v] = pool.id(("a", v))
        role_b[v] = pool.id(("b", v))
        solver.add_clause([role_a[v], role_b[v]])
        solver.add_clause([-role_a[v], -role_b[v]])
    exact_degree(solver, [role_a[v] for v in internal], a)
    # Topological symmetry reduction: all sources precede all internal
    # vertices, which precede all sinks.  This is WLOG for a DAG.
    for v in sources:
        incoming = [x[(u, v)] for u in range(v)]
        outgoing = [x[(v, w)] for w in range(v + 1, n)]
        exact_degree(solver, incoming, 0)
        exact_degree(solver, outgoing, 3)
    for v in sinks:
        incoming = [x[(u, v)] for u in range(v)]
        outgoing = [x[(v, w)] for w in range(v + 1, n)]
        exact_degree(solver, incoming, 3)
        exact_degree(solver, outgoing, 0)
    for v in internal:
        incoming = [x[(u, v)] for u in range(v)]
        outgoing = [x[(v, w)] for w in range(v + 1, n)]
        exact_degree(solver, incoming, 1, role_a[v])
        exact_degree(solver, outgoing, 2, role_a[v])
        exact_degree(solver, incoming, 2, role_b[v])
        exact_degree(solver, outgoing, 1, role_b[v])
    return solver, pool, x


def edge_set(model, edges, x):
    positive = set(model)
    return [(u, v) for u, v in edges if x[(u, v)] in positive]


def weakly_connected(n, arcs):
    adj = [[] for _ in range(n)]
    for u, v in arcs:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == n


def block_graph(solver, n, edges, x, arcs):
    aset = set(arcs)
    solver.add_clause([
        -x[(u, v)] if (u, v) in aset else x[(u, v)]
        for u, v in edges
    ])


def run_profile(n, s, seconds, max_candidates, out_path=None):
    sources = list(range(s))
    sinks = list(range(n - s, n))
    internal = list(range(s, n - s))
    if len(internal) % 2:
        return {"status": "invalid-profile", "n": n, "s": s}
    started = time.time()
    solver, pool, x = build_solver(n, sources, sinks)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    stats = {"n": n, "sources": s, "sinks": s, "candidates": 0,
             "tau_lt3": 0, "packed": 0, "out_safe_reject": 0,
             "rho_reject": 0, "status": "budget"}
    records = []
    while stats["candidates"] < max_candidates and time.time() - started < seconds:
        if not solver.solve():
            stats["status"] = "UNSAT"
            break
        arcs = edge_set(solver.get_model(), edges, x)
        stats["candidates"] += 1
        # For the target sizes, use the independent exact subset-based tau
        # routine.  This avoids relying on a min-cut heuristic for arbitrary
        # DAG source/sink pairs.
        t = harness_tau(n, arcs) if n <= 20 else tau_mincut(n, arcs)
        if t != 3:
            stats["tau_lt3"] += 1
            block_graph(solver, n, edges, x, arcs)
            continue
        if not weakly_connected(n, arcs):
            stats["connectivity_reject"] = stats.get("connectivity_reject", 0) + 1
            block_graph(solver, n, edges, x, arcs)
            continue
        if is_source_sink_connected(n, arcs) or is_planar(n, arcs):
            stats["out_safe_reject"] += 1
            block_graph(solver, n, edges, x, arcs)
            continue
        if rho(n, arcs, 3) < 4 or rho(n, list(reversed([(v, u)
                                                            for u, v in arcs])), 3) < 4:
            stats["rho_reject"] += 1
            block_graph(solver, n, edges, x, arcs)
            continue
        count, packed = cegar_count(n, arcs, 3, cap=1)
        if packed:
            stats["packed"] += 1
            block_graph(solver, n, edges, x, arcs)
            continue
        stats["status"] = "COUNTEREXAMPLE"
        rec = {"n": n, "s": s, "tau": t, "arcs": arcs}
        records.append(rec)
        if out_path:
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        # Do not continue after a possible counterexample.
        break
    solver.delete()
    stats["seconds"] = round(time.time() - started, 2)
    if records:
        stats["counterexamples"] = records
    print(json.dumps(stats), flush=True)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("s", type=int)
    ap.add_argument("--seconds", type=float, default=300)
    ap.add_argument("--max-candidates", type=int, default=10000)
    ap.add_argument("--out")
    args = ap.parse_args()
    run_profile(args.n, args.s, args.seconds, args.max_candidates, args.out)


if __name__ == "__main__":
    main()

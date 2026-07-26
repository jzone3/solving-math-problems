# Provenance: new stage-2 growth/CEGAR engine, using gadget.py's DRAT-core pattern.
"""Constructive forcing-subgraph search over the A half of a universe.

The forcing property is:

    4-colour(L) AND avoid(all forbidden interface patterns) is UNSAT.

Growth starts at the interface, repeatedly adds A-pool vertices that conflict
with the current model (or the most constraining frontier batch), and then
optionally applies DRAT-core and greedy deletion shrinking.
"""

from __future__ import annotations

import argparse
import pickle
import random
import time

from pysat.solvers import Cadical153

import gadget


def prop_clause(pattern):
    vertices, colors = pattern
    return [-gadget.color_var(v, c) for v, c in zip(vertices, colors)]


def relabel(current, edges, patterns):
    order = sorted(current)
    idx = {v: i for i, v in enumerate(order)}
    es = [(idx[u], idx[v]) for u, v in edges if u in idx and v in idx]
    ps = [
        (tuple(idx[v] for v in vs), colors)
        for vs, colors in patterns
        if all(v in idx for v in vs)
    ]
    return order, es, ps


def solve_model(current, edges, patterns):
    order, es, ps = relabel(current, edges, patterns)
    cls = gadget.build_cnf(len(order), es, [prop_clause(p) for p in ps])
    with Cadical153(bootstrap_with=cls) as solver:
        if not solver.solve():
            return None
        model = set(solver.get_model())
    colors = {}
    for i, old in enumerate(order):
        for c in range(4):
            if gadget.color_var(i, c) in model:
                colors[old] = c
                break
    return colors


def grow(a_ids, a_edges, patterns, interface, batch=8, seed_mode="interface", limit=1000):
    current = set(interface)
    if seed_mode == "onehop":
        for u, v in a_edges:
            if u in current:
                current.add(v)
            elif v in current:
                current.add(u)
    history = []
    for iteration in range(limit):
        colors = solve_model(current, a_edges, patterns)
        if colors is None:
            return current, history, "UNSAT"
        missing = []
        frontier = {}
        for v in a_ids - current:
            neigh = [
                u if u != v else w
                for u, w in a_edges
                if u == v and w in current or w == v and u in current
            ]
            seen = {colors[u] for u in neigh if u in colors}
            if len(seen) == 4:
                missing.append(v)
            elif seen:
                frontier[v] = (len(seen), len(neigh))
        if missing:
            chosen = set(missing[:batch])
            reason = "model-conflict"
        elif frontier:
            ranked = sorted(frontier, key=lambda v: frontier[v], reverse=True)
            chosen = set(ranked[:batch])
            reason = "frontier"
        else:
            remaining = sorted(a_ids - current)
            if not remaining:
                return current, history, "SAT"
            chosen = set(remaining[:batch])
            reason = "fallback"
        current.update(chosen)
        history.append(
            {"iteration": iteration, "added": len(chosen), "size": len(current), "reason": reason}
        )
    return current, history, "LIMIT"


def shrink(current, a_edges, patterns, preserve, greedy=True, seed=1, timeout=None):
    """DRAT-core reduction followed by greedy deletion with core jumps."""
    rng = random.Random(seed)
    current = set(current)
    while True:
        order, es, ps = relabel(current, a_edges, patterns)
        used = gadget.core_vertices(
            len(order),
            es,
            [prop_clause(p) for p in ps],
            {order.index(v) for v in preserve if v in current},
            timeout=timeout,
        )
        if used is None:
            return current, "SAT"
        new = {order[i] for i in used}
        if new == current:
            break
        current = new

    if not greedy:
        return current, "UNSAT"
    while True:
        changed = False
        candidates = list(current - set(preserve))
        rng.shuffle(candidates)
        for v in candidates:
            trial = current - {v}
            order, es, ps = relabel(trial, a_edges, patterns)
            used = gadget.core_vertices(
                len(order),
                es,
                [prop_clause(p) for p in ps],
                {order.index(u) for u in preserve if u in trial},
                timeout=timeout,
            )
            if used is None:
                continue
            current = {order[i] for i in used}
            changed = True
        if not changed:
            return current, "UNSAT"


def run(
    cache,
    pattern_file,
    engine="growth",
    shrink_result=True,
    batch=8,
    seed=1,
    seed_mode="interface",
):
    points, edges, labels, metadata = pickle.load(open(cache, "rb"))
    analysis = pickle.load(open(pattern_file, "rb"))
    a_n = metadata["A_candidates"]
    a_ids = set(range(a_n))
    a_edges = labels["AA"]
    patterns = [
        ((tuple(item[:2]), tuple(item[2])))
        for item in analysis["pairs"]
    ] + [
        (tuple(vs), tuple(cs))
        for vs, cs in analysis["triples"]
    ]
    interface = set(analysis["interface_a"])
    if not patterns:
        return {
            "status": "NO_PATTERNS",
            "vertices": None,
            "patterns": 0,
            "seconds": 0.0,
        }
    started = time.time()
    if engine == "growth":
        current, history, status = grow(
            a_ids, a_edges, patterns, interface, batch=batch, seed_mode=seed_mode
        )
    else:
        current = a_ids
        history = []
        status = "FULL"
    if shrink_result:
        current, shrink_status = shrink(
            current,
            a_edges,
            patterns,
            set(interface),
            seed=seed,
        )
        status = shrink_status
    return {
        "status": status,
        "vertices": sorted(current),
        "patterns": len(patterns),
        "interface": sorted(interface),
        "history": history,
        "seconds": time.time() - started,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("patterns")
    ap.add_argument("--engine", choices=("growth", "shrink"), default="growth")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seed-mode", choices=("interface", "onehop"), default="interface")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--no-shrink", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = run(
        args.cache,
        args.patterns,
        args.engine,
        not args.no_shrink,
        args.batch,
        args.seed,
        args.seed_mode,
    )
    print(
        f"status={result['status']} patterns={result['patterns']} "
        f"L={None if result['vertices'] is None else len(result['vertices'])} "
        f"time={result['seconds']:.2f}s"
    )
    if result.get("history"):
        print("growth:", " ".join(str(x["size"]) for x in result["history"]))
    if args.out:
        with open(args.out, "wb") as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()

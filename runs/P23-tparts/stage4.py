# Provenance: new stage-4 fixed-pattern/orbit-growth search using cegar.py and gadget.py.
"""Fixed-pattern alternating minimisation and symmetric A-side growth."""

from __future__ import annotations

import argparse
import pickle
import random
import time
from collections import Counter

import lattice

import cegar
import gadget


def pattern_clause(pattern, idx):
    vs, cs = pattern
    return [-gadget.color_var(idx[v], c) for v, c in zip(vs, cs)]


def a_orbits(points, a_pool):
    """Group lattice A points into the order-24 lattice symmetry orbits."""
    lookup = {}
    int_points = {}
    for i in a_pool:
        p = points[i]
        int_points[i] = (
            int(12 * p[0][0]),
            int(12 * p[0][5]),
            int(12 * p[1][1]),
            int(12 * p[1][4]),
        )
        lookup[int_points[i]] = i
    groups = []
    seen = set()
    for i in sorted(a_pool):
        if i in seen:
            continue
        orbit = {lookup[p] for p in lattice.orbit(int_points[i]) if p in lookup}
        groups.append(orbit)
        seen.update(orbit)
    return groups


def grow_orbits(L, a_pool, a_edges, patterns, points, batch=1, limit=1000):
    groups = a_orbits(points, a_pool)
    current = set(L)
    history = []
    for step in range(limit):
        coloring = cegar.color_a(current, a_edges, patterns)
        if coloring is None:
            return current, history, "UNSAT"
        candidates = []
        for group in groups:
            if group <= current:
                continue
            score = 0
            forced = False
            for v in group:
                neigh = [
                    w if u == v else u
                    for u, w in a_edges
                    if (u == v and w in current) or (w == v and u in current)
                ]
                seen = {coloring[u] for u in neigh if u in coloring}
                score = max(score, len(seen), len(neigh))
                forced |= len(seen) == 4
            candidates.append((forced, score, -len(group), group))
        if not candidates:
            return current, history, "EXTENDS_FULL_A"
        candidates.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
        chosen = set()
        for _, _, _, group in candidates[:batch]:
            chosen.update(group)
        current.update(chosen)
        history.append({"step": step, "added": len(chosen), "L": len(current)})
    return current, history, "LIMIT"


def a_fixed_test(L, a_edges, patterns):
    return cegar.cached_test(L, a_edges, patterns)


def b_fixed_test(S, b_edges, cross, patterns):
    theory = cegar.BTheory(S, cross, b_edges)
    ok = all(not theory.query(dict(zip(vs, cs))) for vs, cs in patterns)
    theory.close()
    return ok


def b_core_reduce(S, b_edges, cross, patterns):
    """Union per-pattern DRAT cores, preserving every still-needed B vertex."""
    current = set(S)
    while True:
        used_all = set()
        for vs, cs in patterns:
            oriented = [(a, b) for a, b in cross if b in current]
            bverts = set(current) | {b for _, b in oriented}
            iverts = {a for a, _ in oriented}
            order = sorted(bverts | iverts)
            idx = {v: i for i, v in enumerate(order)}
            edges = [
                (idx[u], idx[v]) for u, v in b_edges
                if u in idx and v in idx
            ]
            edges += [(idx[a], idx[b]) for a, b in oriented]
            props = [[gadget.color_var(idx[v], c)] for v, c in zip(vs, cs)]
            used = gadget.core_vertices(
                len(order),
                edges,
                props,
                set(),
                timeout=1800,
            )
            if used is None:
                return current, False
            used_all.update(order[i] for i in used if order[i] in current)
        if used_all == current:
            return current, True
        current = used_all


def a_greedy(L, a_edges, patterns, preserve, seed=1):
    rng = random.Random(seed)
    current = set(L)
    while True:
        changed = False
        order = list(current - set(preserve))
        rng.shuffle(order)
        for v in order:
            trial = current - {v}
            if a_fixed_test(trial, a_edges, patterns):
                current = trial
                changed = True
        if not changed:
            return current


def b_greedy(S, b_edges, cross, patterns, seed=1):
    rng = random.Random(seed)
    current = set(S)
    while True:
        changed = False
        order = list(current)
        rng.shuffle(order)
        for v in order:
            trial = current - {v}
            if b_fixed_test(trial, b_edges, cross, patterns):
                current = trial
                changed = True
        if not changed:
            return current


def fixed_minimise(points, a_pool, b_pool, a_edges, b_edges, cross, L, S,
                   patterns, seed=1, greedy=True):
    """Minimise both sides while preserving a fixed pattern set P."""
    preserve = {v for vs, _ in patterns for v in vs}
    L = cegar.core_reduce(L, a_edges, patterns, preserve)
    S, ok = b_core_reduce(S, b_edges, cross, patterns)
    if not ok:
        return L, S, "PATTERN_LOST"
    if greedy:
        L = a_greedy(L, a_edges, patterns, preserve, seed)
        S = b_greedy(S, b_edges, cross, patterns, seed)
    return L, S, "UNSAT"


def load_case(cache, pattern_pickle):
    points, labels, metadata, a_pool, b_pool, _, _ = cegar.side_sets(cache, "full")
    b_edges, cross = cegar.split_edges(labels, metadata)
    result = pickle.load(open(pattern_pickle, "rb"))
    if isinstance(result, dict):
        patterns = list(result["patterns"])
    elif isinstance(result, tuple) and len(result) >= 2 and isinstance(result[1], list):
        patterns = list(result[1])
    else:
        patterns = list(result)
    return points, metadata, a_pool, b_pool, labels["AA"], b_edges, cross, patterns


def run_curve(cache, pattern_pickle, counts, seed=1, fast=False):
    points, metadata, a_pool, b_pool, a_edges, b_edges, cross, all_patterns = load_case(
        cache, pattern_pickle
    )
    interface = {a for a, _ in cross}
    out = []
    for count in counts:
        patterns = all_patterns[:count]
        seed_l = interface | {v for vs, _ in patterns for v in vs}
        started = time.time()
        L, hist, grow_status = grow_orbits(
            seed_l, a_pool, a_edges, patterns, points, batch=1
        )
        if grow_status != "UNSAT":
            out.append({
                "patterns": count,
                "status": grow_status,
                "L": len(L),
                "S": len(b_pool),
                "total": len(L) + len(b_pool),
                "L_ids": sorted(L),
                "S_ids": sorted(b_pool),
                "seconds": time.time() - started,
            })
            continue
        if fast:
            L = cegar.core_reduce(
                L, a_edges, patterns,
                {v for vs, _ in patterns for v in vs},
            )
            S, status = b_pool, "CORE_ONLY"
        else:
            L, S, status = fixed_minimise(
                points, a_pool, b_pool, a_edges, b_edges, cross,
                L, b_pool, patterns, seed=seed,
            )
        out.append({
            "patterns": count,
            "status": status,
            "L": len(L),
            "S": len(S),
            "total": len(L) + len(S),
            "L_ids": sorted(L),
            "S_ids": sorted(S),
            "orders": dict(Counter(len(vs) for vs, _ in patterns)),
            "seconds": time.time() - started,
            "growth_steps": len(hist),
        })
        print(out[-1], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("patterns")
    ap.add_argument("--counts", default="all")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--fast", action="store_true",
                    help="A-side orbit growth plus core only; skip B/greedy deletion")
    args = ap.parse_args()
    result = pickle.load(open(args.patterns, "rb"))
    if isinstance(result, dict):
        pats = result["patterns"]
    elif isinstance(result, tuple) and len(result) >= 2 and isinstance(result[1], list):
        pats = result[1]
    else:
        pats = result
    counts = [len(pats)] if args.counts == "all" else [
        int(x) for x in args.counts.split(",")
    ]
    out = run_curve(args.cache, args.patterns, counts, args.seed, args.fast)
    if args.out:
        pickle.dump(out, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()

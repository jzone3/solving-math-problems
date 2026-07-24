#!/usr/bin/env python3
"""Exact searches in symmetric/algebraic Woodall families D1--D3."""
import itertools
import random
import sys
from collections import Counter

from pysat.solvers import Glucose4
from pysat.formula import IDPool

from harness import (is_dag, is_planar, is_source_sink_connected,
                     minimal_dicuts, rho, tau)


def min_dicuts(n, arcs, max_ideals=200000):
    pred = [0] * n
    succ = [[] for _ in range(n)]
    for u, v in arcs:
        pred[v] |= 1 << u
        succ[u].append(v)
    indeg = [x.bit_count() for x in pred]
    q = [v for v in range(n) if not indeg[v]]
    order = []
    for u in q:
        order.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if not indeg[v]:
                q.append(v)
    if len(order) != n:
        return None, None
    cuts = set()
    count = 0
    full = (1 << n) - 1
    def rec(i, chosen):
        nonlocal count
        count += 1
        if count > max_ideals:
            raise OverflowError
        if i == n:
            if chosen and chosen != full:
                c = frozenset(j for j, (u, v) in enumerate(arcs)
                              if chosen >> u & 1 and not (chosen >> v & 1))
                if c:
                    cuts.add(c)
            return
        rec(i + 1, chosen)
        v = order[i]
        if not (pred[v] & ~chosen):
            rec(i + 1, chosen | (1 << v))
    try:
        rec(0, 0)
    except OverflowError:
        return None, None
    minimal = []
    for c in sorted(cuts, key=len):
        if not any(m < c for m in minimal):
            minimal.append(c)
    return minimal, (len(minimal[0]) if minimal else None)


def pack_from_cuts(m, cuts, k):
    if any(len(c) < k for c in cuts):
        return False
    pool = IDPool()
    var = lambda a, c: pool.id((a, c))
    s = Glucose4()
    for a in range(m):
        s.add_clause([var(a, c) for c in range(k)])
        for c in range(k):
            for d in range(c):
                s.add_clause([-var(a, c), -var(a, d)])
    for cut in cuts:
        for c in range(k):
            s.add_clause([var(a, c) for a in cut])
    ans = s.solve()
    s.delete()
    return ans


def exact(n, arcs, k):
    cuts = minimal_dicuts(n, arcs) if n <= 14 else None
    if cuts is None:
        cuts, t = min_dicuts(n, arcs,
                             max_ideals=(5000000 if n <= 27 else 200000))
        if cuts is None:
            return None, None, None
    else:
        t = min(map(len, cuts), default=None)
    return t, len(cuts), pack_from_cuts(len(arcs), cuts, k) if t == k else None


def exact_bipartite(ns, arcs, k):
    """Exact cuts for source-to-sink incidence graphs.

    Sink inclusion never changes an out-cut, so every distinct dicut is
    represented by a nonempty subset of the source side.
    """
    if ns > 22:
        return None, None, None
    cuts = set()
    for mask in range(1, 1 << ns):
        c = frozenset(i for i, (u, v) in enumerate(arcs)
                      if mask >> u & 1 and v >= ns)
        if c:
            cuts.add(c)
    minimal = []
    for c in sorted(cuts, key=len):
        if not any(m < c for m in minimal):
            minimal.append(c)
    t = min(map(len, minimal), default=None)
    return t, len(minimal), pack_from_cuts(len(arcs), minimal, k) if t == k else None


def cyclic_sts(v):
    """Find a cyclic Steiner triple system by exact-covering pair differences."""
    pairs = {(i, j) for i in range(v) for j in range(i + 1, v)}
    seen = set()
    orbits = []
    for b in itertools.combinations(range(v), 3):
        blocks = {tuple(sorted((x + s) % v for x in b)) for s in range(v)}
        key = min(blocks)
        if key in seen:
            continue
        seen.add(key)
        covered = set()
        ok = True
        for x in blocks:
            for a, c in itertools.combinations(x, 2):
                q = tuple(sorted((a, c)))
                if q in covered:
                    ok = False
                covered.add(q)
        if ok:
            orbits.append((blocks, covered))
    bypair = {p: [] for p in pairs}
    for i, (_, cov) in enumerate(orbits):
        for p in cov:
            bypair[p].append(i)

    def rec(left, chosen):
        if not left:
            out = set()
            for i in chosen:
                out |= orbits[i][0]
            return sorted(out)
        p = min(left, key=lambda q: len(bypair[q]))
        for i in bypair[p]:
            cov = orbits[i][1]
            if cov <= left:
                ans = rec(left - cov, chosen + [i])
                if ans is not None:
                    return ans
        return None
    return rec(pairs, [])


def incidence(v, blocks, mult=1):
    return v + len(blocks), [
        (p, v + j) for j, b in enumerate(blocks)
        for p in b for _ in range(mult)
    ]


def check_family(name, cases, k):
    stats = Counter()
    best = None
    for label, n, arcs in cases:
        stats["built"] += 1
        indeg = [0] * n
        outdeg = [0] * n
        for u, v in arcs:
            indeg[v] += 1
            outdeg[u] += 1
        sources = [v for v in range(n) if indeg[v] == 0]
        sinks = [v for v in range(n) if outdeg[v] == 0]
        if sources and len(sources) + len(sinks) == n and max(sources + sinks) < n:
            remap = {v: i for i, v in enumerate(sources + sinks)}
            aa = [(remap[u], remap[v]) for u, v in arcs]
            t, nc, packed = exact_bipartite(len(sources), aa, k)
        else:
            t, nc, packed = exact(n, arcs, k)
        stats["deferred" if t is None else f"tau={t}"] += 1
        if t != k:
            continue
        stats["tau_k"] += 1
        if not is_source_sink_connected(n, arcs) and not is_planar(n, arcs):
            stats["out_safe"] += 1
            if rho(n, arcs, k) >= (4 if k == 3 else 3):
                stats["rho_ok"] += 1
                if packed:
                    stats["packed"] += 1
                else:
                    stats["candidates"] += 1
                    print("COUNTEREXAMPLE", name, label, n, arcs, flush=True)
        score = (nc or 0, len(arcs))
        if best is None or score > best[0]:
            best = (score, label, t, nc, packed)
    print(name, dict(stats), "near_miss_by_cuts=", best, flush=True)
    return stats


def run_d1(do_k4=True):
    cases3 = []
    for v in (7, 9, 13, 15):
        blocks = cyclic_sts(v)
        if v == 9:
            blocks = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),
                      (2,5,8),(0,4,8),(1,5,6),(2,3,7)]
        if blocks is None:
            print("NO_CYCLIC_STS", v)
            continue
        n, a = incidence(v, blocks, 1)
        cases3.append((f"STS{v}-lambda1", n, a))
    check_family("D1-k3", cases3, 3)
    if not do_k4:
        return
    cases4 = []
    for v, blocks in ((7, list(itertools.combinations(range(7), 4))),
                      (13, [tuple(sorted((x + s) % 13 for x in (0, 1, 3, 9)))
                            for s in range(13)])):
        for mult in (1, 2):
            n, a = incidence(v, blocks, mult)
            cases4.append((f"all4-{v}-lambda{mult}", n, a))
    check_family("D1-k4", cases4, 4)


def run_d2():
    solid = [(2,1),(12,1),(12,14),(15,14),(15,9),(6,9),(6,16),
             (6,16),(2,13),(2,13),(4,3),(4,17),(4,3),(18,17),
             (8,19),(8,20),(8,20),(0,5),(22,5),(22,23),(24,23),
             (24,7),(11,7),(0,21),(11,10),(26,19),(18,25),(26,25),
             (11,10),(0,21)]
    dash = [(11,19),(18,10),(18,13),(12,21),(0,14),(15,5),(8,9),
            (6,7),(22,16),(22,3),(4,23),(24,17),(12,20),(2,25),(26,1)]
    base = solid + dash
    print("D2 base_dag=", is_dag(27, base), flush=True)
    rng = random.Random(202503)
    cases = [("D27-base", 27, base)]
    for p in (2, 3, 5, 7):
        for z in range(12):
            volt = [rng.randrange(p) for _ in base]
            arcs = []
            for (u, v), g in zip(base, volt):
                for i in range(p):
                    arcs.append((u * p + i, v * p + ((i + g) % p)))
            cases.append((f"D27-lift-p{p}-{z}", 27 * p, arcs))
    check_family("D2", cases, 3)


def run_d3():
    cases3 = []
    for m in range(4, 7):
        for k in (2, 3):
            top = list(itertools.combinations(range(m), k))
            bot = list(itertools.combinations(range(m), k - 1))
            bi = {b: len(top) + i for i, b in enumerate(bot)}
            arcs = [(i, bi[b]) for i, a in enumerate(top)
                    for b in bot if set(b) < set(a)]
            cases3.append((f"J{m},{k}", len(top) + len(bot), arcs))
    check_family("D3", cases3, 3)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "d1"
    if cmd == "d1":
        run_d1()
    elif cmd == "d1k3":
        run_d1(False)
    elif cmd == "d2":
        run_d2()
    elif cmd == "d3":
        run_d3()

#!/usr/bin/env python3
"""Exact searches in symmetric/algebraic Woodall families D1--D3."""
import itertools
import random
import sys
from collections import Counter
import networkx as nx

from pysat.solvers import Glucose4
from pysat.formula import IDPool

from harness import (is_dag, is_planar, is_source_sink_connected,
                     minimal_dicuts, rho, tau)
from enum_pypy import _violated_cut, star_cuts


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


def tau_mincut(n, arcs):
    """Minimum nonempty dicut via source-to-sink directed min-cuts."""
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for u, v in arcs:
        G.add_edge(u, v, capacity=G.get_edge_data(u, v, {}).get("capacity", 0) + 1)
    sources = [v for v in G if G.in_degree(v) == 0]
    sinks = [v for v in G if G.out_degree(v) == 0]
    if not sources or not sinks:
        return None
    star = min([sum(1 for u, v in arcs if v == x) for x in sinks] +
               [sum(1 for u, v in arcs if u == x) for x in sources])
    UG = nx.MultiGraph()
    UG.add_nodes_from(range(n))
    UG.add_edges_from(arcs)
    comps = list(nx.connected_components(UG))
    if comps:
        conn = min(nx.edge_connectivity(UG.subgraph(c)) for c in comps
                   if len(c) > 1)
        if conn >= star:
            return star
    best = None
    for s in sources:
        for t in sinks:
            if best == 1:
                return best
            if s == t:
                continue
            try:
                value, (left, _) = nx.minimum_cut(G, s, t, capacity="capacity")
            except nx.NetworkXError:
                continue
            # Close the source side under predecessors; this is the valid
            # dicut side, whereas an arbitrary s-t cut need not be closed.
            closed = set(left)
            changed = True
            while changed:
                changed = False
                for u, v in arcs:
                    if v in closed and u not in closed:
                        closed.add(u)
                        changed = True
            if t in closed or not closed or len(closed) == n:
                continue
            cv = sum(1 for u, v in arcs if u in closed and v not in closed)
            if cv > 0 and (best is None or cv < best):
                best = cv
    return best


def cegar_count(n, arcs, k, cap=1):
    """Exact CEGAR packing and count modulo color permutation.

    The SAT instance starts with source/sink stars, then lazily receives a
    clause for every violated dicut discovered by the dijoin verifier.
    """
    m = len(arcs)
    cuts = [list(c) for c in star_cuts(n, arcs)]
    pool = IDPool()
    var = lambda a, c: pool.id((a, c))
    s = Glucose4()
    for a in range(m):
        s.add_clause([var(a, c) for c in range(k)])
        for c in range(k):
            for d in range(c):
                s.add_clause([-var(a, c), -var(a, d)])
    # Fix the first arc's color to remove global color permutation.
    if m:
        s.add_clause([var(0, 0)])
    def add_cut(cut, color=None):
        if color is None:
            for c in range(k):
                s.add_clause([var(a, c) for a in cut])
        else:
            s.add_clause([var(a, color) for a in cut])
    for cut in cuts:
        add_cut(cut)
    count = 0
    while count < cap and s.solve():
        model = {x for x in s.get_model() if x > 0}
        coloring = [next(c for c in range(k) if var(a, c) in model)
                    for a in range(m)]
        violated = None
        for c in range(k):
            violated = _violated_cut(n, arcs, coloring, c)
            if violated is not None:
                add_cut(violated, c)
                break
        if violated is not None:
            continue
        count += 1
        s.add_clause([-var(a, coloring[a]) for a in range(m)])
    s.delete()
    return count, count >= 1


def exact(n, arcs, k):
    if n <= 14:
        cuts = minimal_dicuts(n, arcs)
        t = min(map(len, cuts), default=None)
    else:
        cuts = None
        t = tau_mincut(n, arcs)
    if t is None:
        return None, None, None, None
    if t != k:
        return t, (len(cuts) if cuts is not None else None), None, None
    count, packed = cegar_count(n, arcs, k)
    return t, (len(cuts) if cuts is not None else None), packed, count


def exact_bipartite(ns, arcs, k):
    """Exact cuts for source-to-sink incidence graphs.

    Sink inclusion never changes an out-cut, so every distinct dicut is
    represented by a nonempty subset of the source side.
    """
    total = max(max(u, v) for u, v in arcs) + 1
    t = tau_mincut(total, arcs)
    if t != k:
        return t, None, None, None
    count, packed = cegar_count(total, arcs, k)
    return t, None, packed, count


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
            t, nc, packed, count = exact_bipartite(len(sources), aa, k)
        else:
            t, nc, packed, count = exact(n, arcs, k)
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
                    stats["partitions_sum"] += count
                    stats["partitions_min"] = min(stats.get("partitions_min", count), count)
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
    for v in (7, 9, 13, 15, 19, 21, 25):
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
    for p in (2, 3, 5, 7, 11):
        patterns = [
            ("zero", [0] * len(base)),
            ("one", [1 % p] * len(base)),
            ("typed01", [0 if i < len(solid) else 1 % p
                         for i in range(len(base))]),
            ("typed10", [1 % p if i < len(solid) else 0
                         for i in range(len(base))]),
        ]
        for z in range(12 if p < 11 else 0):
            patterns.append((f"random{z}", [rng.randrange(p) for _ in base]))
        for tag, volt in patterns:
            arcs = []
            for (u, v), g in zip(base, volt):
                for i in range(p):
                    arcs.append((u * p + i, v * p + ((i + g) % p)))
            cases.append((f"D27-lift-p{p}-{tag}", 27 * p, arcs))
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

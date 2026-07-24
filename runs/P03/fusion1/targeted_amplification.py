#!/usr/bin/env python3
"""Targeted exact perturbations of the tightest observed structured gadget."""
import itertools
import random
from collections import Counter

from structured_search import cegar_count, rho, tau_mincut
from harness import is_planar, is_source_sink_connected


def johnson(m=6, k=3):
    top = list(itertools.combinations(range(m), k))
    bot = list(itertools.combinations(range(m), k - 1))
    off = len(top)
    bi = {b: off + i for i, b in enumerate(bot)}
    arcs = [(i, bi[b]) for i, a in enumerate(top)
            for b in bot if set(b) < set(a)]
    return len(top) + len(bot), arcs


def lift(n, arcs, p, volt):
    return p * n, [(u * p + i, v * p + (i + g) % p)
                   for (u, v), g in zip(arcs, volt) for i in range(p)]


def check(label, n, arcs, out):
    t = tau_mincut(n, arcs)
    out["built"] += 1
    out[f"tau={t}"] += 1
    if t != 3:
        return
    out["tau3"] += 1
    if is_source_sink_connected(n, arcs) or is_planar(n, arcs) or rho(n, arcs, 3) < 4:
        return
    out["in_class"] += 1
    count, packed = cegar_count(n, arcs, 3, cap=1)
    if packed:
        out["packed"] += 1
    else:
        out["candidates"] += 1
        print("COUNTEREXAMPLE", label, n, arcs, flush=True)


def main():
    n, base = johnson()
    rng = random.Random(44117)
    stats = Counter()
    # Voltage lifts of the J(6,3) gadget, including structured assignments.
    for p in (2, 3, 5, 7):
        pats = [
            ("zero", [0] * len(base)),
            ("one", [1 % p] * len(base)),
            ("alternating", [i % p for i in range(len(base))]),
        ]
        for z in range(12):
            pats.append((f"random{z}", [rng.randrange(p) for _ in base]))
        for tag, volt in pats:
            nn, aa = lift(n, base, p, volt)
            check(f"J6,3-lift-p{p}-{tag}", nn, aa, stats)
    # Degree-preserving bipartite 2-switches around the base.
    for z in range(100):
        aa = list(base)
        i, j = rng.sample(range(len(aa)), 2)
        (u, v), (x, y) = aa[i], aa[j]
        if u != x and v != y and (u, y) not in aa and (x, v) not in aa:
            aa[i], aa[j] = (u, y), (x, v)
        check(f"J6,3-switch-{z}", n, aa, stats)
    # Amalgam: identify one sink of two copies.
    sink = 20
    second = [(u + n, v + n) for u, v in base]
    glued = list(base) + [(u, sink if v == n + sink else v)
                          for u, v in second]
    # The first copy's sink is 20; identify the corresponding second sink.
    check("J6,3-glue-sink", n * 2 - 1, glued, stats)
    print("TARGETED", dict(stats), flush=True)


if __name__ == "__main__":
    main()

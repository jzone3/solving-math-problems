"""Exhaustive Woodall check over multi-DAGs.

Reduction (see woodall.condense_multi): every digraph has the same tau and nu
as its condensation with parallel arcs kept, so any minimal counterexample is
a weakly-connected multi-DAG. WLOG vertices are topologically ordered, so the
support is a subset of {(u,v): u < v}; parallel multiplicities >= 1 on each
support arc. We enumerate all such instances with k vertices and total arc
count <= mmax, dedup up to isomorphism (min over all vertex permutations of
the sorted arc multiset -- exact), and test every instance with tau in
[3, tau_hi].

Usage: python3 multidag_exhaustive.py k mmax [tau_hi]
"""

import itertools
import sys
import time

from woodall import all_dicuts, max_packing
from search import weakly_connected


def compositions(s, total_max, mult_max):
    """All tuples of length s, entries in [1, mult_max], sum <= total_max."""
    def rec(i, left):
        if i == s:
            yield ()
            return
        # need at least (s - i) more units
        for v in range(1, min(mult_max, left - (s - i - 1)) + 1):
            for rest in rec(i + 1, left - v):
                yield (v,) + rest
    yield from rec(0, total_max)


def canon(k, arc_multiset):
    best = None
    for perm in itertools.permutations(range(k)):
        key = tuple(sorted((perm[u], perm[v], c) for (u, v), c in
                           arc_multiset.items()))
        if best is None or key < best:
            best = key
    return best


def run(k, mmax, tau_hi=6, tau_lo=3):
    pairs = [(u, v) for u in range(k) for v in range(u + 1, k)]
    t0 = time.time()
    seen = set()
    stats = {"instances": 0, "tau3+": 0, "gap>0": 0}
    for smask in range(1, 1 << len(pairs)):
        support = [pairs[i] for i in range(len(pairs)) if (smask >> i) & 1]
        s = len(support)
        if s < 3 or s > mmax:
            continue
        # every vertex must be covered (weak connectivity checked later)
        verts = set()
        for (u, v) in support:
            verts.add(u)
            verts.add(v)
        if len(verts) != k:
            continue
        if not weakly_connected(k, support):
            continue
        for mult in compositions(s, mmax, mmax):
            ms = {support[i]: mult[i] for i in range(s)}
            key = canon(k, ms)
            if key in seen:
                continue
            seen.add(key)
            stats["instances"] += 1
            arcs = []
            for (u, v), c in ms.items():
                arcs.extend([(u, v)] * c)
            cuts = all_dicuts(k, arcs)
            tau = min(len(c) for c in cuts)
            if tau < tau_lo or tau > tau_hi:
                continue
            stats["tau3+"] += 1
            _, nu = max_packing(k, arcs, tau=tau)
            if nu < tau:
                stats["gap>0"] += 1
                print("!!! GAP:", k, arcs, tau, nu, flush=True)
            if stats["tau3+"] % 2000 == 0:
                print(f"[{time.time()-t0:7.0f}s] {stats}", flush=True)
    print(f"DONE k={k} mmax={mmax} in {time.time()-t0:.0f}s: {stats}",
          flush=True)


if __name__ == "__main__":
    k = int(sys.argv[1])
    mmax = int(sys.argv[2])
    tau_hi = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    run(k, mmax, tau_hi=tau_hi)

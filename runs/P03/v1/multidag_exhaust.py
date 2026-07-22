#!/usr/bin/env python3
"""
Exhaustive search over multi-DAGs: all DAGs on n vertices in fixed topological
order (arcs i->j only for i<j), all arc-multiplicity assignments with total
number of arcs <= M.  Every multi-DAG on <= n vertices appears (in some
labeling), so this exhausts "parallel-arc" (integer-weighted) instances, the
regime where Schrijver's weighted counterexample lives.

Usage: multidag_exhaust.py N M [MOD RES]
"""
import sys, time
from itertools import combinations
from search import dicuts_and_tau, packs_into, report_counterexample


def compositions(total, k):
    """All k-tuples of ints >=1 summing to exactly total."""
    if k == 1:
        yield (total,)
        return
    for first in range(1, total - k + 2):
        for rest in compositions(total - first, k - 1):
            yield (first,) + rest


def main():
    n, M = int(sys.argv[1]), int(sys.argv[2])
    mod, res = 1, 0
    if len(sys.argv) >= 5:
        mod, res = int(sys.argv[3]), int(sys.argv[4])
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    t0 = time.time()
    checked = 0; bytau = {}; supp_i = 0
    for k in range(n - 1, len(pairs) + 1):
        for support in combinations(range(len(pairs)), k):
            supp_i += 1
            if supp_i % mod != res:
                continue
            base = [pairs[i] for i in support]
            # every vertex must be covered (weak connectivity checked later)
            verts = set()
            for (u, v) in base:
                verts.add(u); verts.add(v)
            if len(verts) != n:
                continue
            # dicut structure depends only on support? NO - multiplicities
            # change cut sizes. But cuts' arc-index SETS map from support cuts.
            for mult in compositions_upto(M, k):
                arcs = []
                for i, (u, v) in enumerate(base):
                    arcs.extend([(u, v)] * mult[i])
                cuts, tau = dicuts_and_tau(n, arcs)
                if cuts is None or tau < 2:
                    continue
                ok, _ = packs_into(len(arcs), cuts, tau)
                checked += 1
                bytau[tau] = bytau.get(tau, 0) + 1
                if not ok:
                    report_counterexample(n, arcs, tau)
                if checked % 200000 == 0:
                    print(f"[mdag n={n} M={M} {mod}/{res}] checked={checked} "
                          f"bytau={sorted(bytau.items())} t={time.time()-t0:.0f}s",
                          flush=True)
    print(f"[mdag n={n} M={M} {mod}/{res}] DONE checked={checked} "
          f"bytau={sorted(bytau.items())} t={time.time()-t0:.0f}s", flush=True)


def compositions_upto(M, k):
    """All k-tuples >=1 with sum <= M."""
    for total in range(k, M + 1):
        yield from compositions(total, k)


if __name__ == "__main__":
    main()

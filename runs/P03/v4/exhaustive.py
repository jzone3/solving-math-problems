"""Exhaustively verify Woodall (gap = 0) over ALL simple digraphs on n
vertices (no parallel arcs, no loops; 2-cycles allowed). For each isomorphism
class (exact dedup via min over all vertex permutations) that is weakly
connected, not strongly connected, and has tau >= 3, compute nu by ILP and
report any gap.

n = 4: 2^12 arc masks. n = 5: 2^20 arc masks (feasible with canon dedup).
"""

import itertools
import sys
import time

from woodall import all_dicuts, max_packing
from search import weakly_connected
from woodall import is_strongly_connected


def run(n, tau_lo=3, report_every=100000):
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    m_all = len(pairs)
    perms = list(itertools.permutations(range(n)))
    pair_idx = {p: i for i, p in enumerate(pairs)}
    # precompute permutation action on arc bit positions
    perm_maps = []
    for perm in perms:
        perm_maps.append([pair_idx[(perm[u], perm[v])] for (u, v) in pairs])
    t0 = time.time()
    seen_canon = set()
    stats = {"classes": 0, "tau3+": 0, "gap>0": 0}
    for mask in range(1, 1 << m_all):
        # canonical form: min over permutations of the permuted mask
        canon = mask
        for pm in perm_maps:
            x = 0
            mm = mask
            while mm:
                b = mm & -mm
                x |= 1 << pm[b.bit_length() - 1]
                mm ^= b
            if x < canon:
                canon = x
        if canon != mask:
            continue  # only process canonical representative
        stats["classes"] += 1
        arcs = [pairs[i] for i in range(m_all) if (mask >> i) & 1]
        if not weakly_connected(n, arcs):
            continue
        if is_strongly_connected(n, arcs):
            continue
        cuts = all_dicuts(n, arcs)
        tau = min(len(c) for c in cuts)
        if tau < tau_lo:
            continue
        stats["tau3+"] += 1
        _, nu = max_packing(n, arcs, tau=tau)
        if nu < tau:
            stats["gap>0"] += 1
            print("!!! GAP:", n, arcs, tau, nu, flush=True)
        if stats["tau3+"] % 500 == 0:
            print(f"[{time.time()-t0:7.0f}s] mask={mask}/{1<<m_all} "
                  f"{stats}", flush=True)
    print(f"DONE n={n} in {time.time()-t0:.0f}s: {stats}", flush=True)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 4)

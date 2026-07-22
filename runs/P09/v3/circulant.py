#!/usr/bin/env python3
"""Exhaustive circulant-graph sweep for P09.

For circulant C_n(S), eigenvalues are lam_j = sum_{s in S} 2cos(2*pi*j*s/n)
(with the n/2 term counted once). With t = (lam1^2+lam2^2)/(2m), a violation t > 1 - 1/omega is equivalent to
    omega < 1/(1 - t),   i.e.  omega <= kmax := ceil(1/(1-t)) - 1  (t < 1),
and t >= 1 is a violation for every omega (only K_n, which is excluded,
should approach that). So per graph we run a single has_clique(kmax + 1)
query: if a (kmax+1)-clique EXISTS the graph cannot violate; if none exists
it is a violation candidate. Dense circulants have large cliques, so the
query usually succeeds fast. Sweeps ALL connection sets S for each n.
"""
import argparse, itertools, math, sys
sys.setrecursionlimit(10000)
import numpy as np
from search import has_clique


def run_n(n):
    gens = list(range(1, n // 2 + 1))
    half = n // 2 if n % 2 == 0 else None
    j = np.arange(n)
    cos_table = {s: 2 * np.cos(2 * np.pi * j * s / n) for s in gens}
    if half is not None:
        # for s = n/2 the orbit {s, -s} is a single element; contribution is
        # exactly cos(2*pi*j*s/n) (i.e. (-1)^j), not doubled:
        cos_table[half] = np.cos(2 * np.pi * j * half / n)
    best = (-1.0, None)
    count = 0
    for r in range(1, len(gens) + 1):
        for S in itertools.combinations(gens, r):
            count += 1
            ev = np.zeros(n)
            m = 0
            for s in S:
                ev += cos_table[s]
                m += n if (half is None or s != half) else n // 2
            ev_sorted = np.sort(ev)
            l1, l2 = ev_sorted[-1], ev_sorted[-2]
            t = (l1 * l1 + l2 * l2) / (2 * m)
            if t > best[0]:
                best = (t, S)
            if len(S) == len(gens):
                continue  # complete graph, excluded by the conjecture
            if t < 1 - 1e-9:
                kmax = math.ceil(1 / (1 - t) - 1e-12) - 1
                if kmax < 2:
                    continue  # would need omega < 2: impossible (m > 0)
            else:
                kmax = n  # t >= 1 for a non-complete graph: automatic candidate
            # build adjacency bitsets; candidate iff NO (kmax+1)-clique
            adj = [0] * n
            for v in range(n):
                for s in S:
                    adj[v] |= 1 << ((v + s) % n)
                    adj[v] |= 1 << ((v - s) % n)
            if kmax >= n or not has_clique(adj, (1 << n) - 1, kmax + 1):
                print(f"CANDIDATE n={n} S={S} t={t:.9f} kmax={kmax}", flush=True)
    print(f"n={n}: swept {count} circulants, max t={best[0]:.9f} at S={best[1]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=5)
    ap.add_argument("--nmax", type=int, default=40)
    args = ap.parse_args()
    for n in range(args.nmin, args.nmax + 1):
        run_n(n)


if __name__ == "__main__":
    main()

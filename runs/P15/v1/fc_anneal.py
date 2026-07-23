#!/usr/bin/env python3
"""
Ruin-and-recreate local search for finite-LCM covers (P15 V1).

State: partial assignment {n -> a} over distinct moduli n | N, n >= M.
Recreate: jittered gain-density greedy (as fc_restart) until no gain.
Ruin: drop a random fraction of the chosen classes (biased toward classes
with few uniquely-covered cells). Keep the best state seen (min uncovered).

Usage: fc_anneal.py M N [total_seconds] [seed]
Writes /tmp/fca_M{M}.json on success.
"""
import json
import sys
import time

import numpy as np


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


class State:
    def __init__(self, M, N):
        self.N = N
        self.mods = [d for d in divisors(N) if d >= M and d > 1]
        self.cov = np.zeros(N, dtype=np.int16)   # multiplicity of coverage
        self.sel = {}                            # n -> a

    def add(self, n, a):
        self.sel[n] = a
        self.cov[a::n] += 1

    def drop(self, n):
        a = self.sel.pop(n)
        self.cov[a::n] -= 1

    def uncovered(self):
        return int((self.cov == 0).sum())


def recreate(st, rng, jitter):
    """Lazy greedy: gains only decrease as coverage grows, so a stale-max
    heap with on-pop rescoring is (near-)exact and ~|mods|x faster."""
    import heapq
    N = st.N
    unc = st.cov == 0

    def score(n):
        c = unc.reshape(N // n, n).sum(axis=0)
        g = int(c.max())
        if g == 0:
            return 0.0, 0
        near = np.flatnonzero(c >= max(1, int(g * (1 - jitter))))
        a = int(near[rng.integers(len(near))])
        return g / n, a

    heap = []
    for n in st.mods:
        if n not in st.sel:
            s, a = score(n)
            if s > 0:
                heap.append((-s, a, n))
    heapq.heapify(heap)
    while heap and unc.any():
        neg, a_old, n = heapq.heappop(heap)
        s, a = score(n)
        if s == 0:
            continue
        # standard lazy greedy: accept if still at least the (stale) runner-up
        if heap and -heap[0][0] > s:
            heapq.heappush(heap, (-s, a, n))
            continue
        st.add(n, a)
        unc = st.cov == 0


def ruin(st, rng, frac):
    ns = list(st.sel)
    # unique-coverage count per selected class
    uniq = []
    for n in ns:
        a = st.sel[n]
        sl = st.cov[a::n]
        uniq.append(int((sl == 1).sum()))
    order = np.argsort(uniq)  # weakest first
    k = max(1, int(len(ns) * frac))
    # drop the k weakest plus k random others
    drop_idx = set(order[:k].tolist())
    drop_idx.update(rng.choice(len(ns), size=min(k, len(ns)),
                               replace=False).tolist())
    for i in drop_idx:
        st.drop(ns[i])


def main():
    M, N = int(sys.argv[1]), int(sys.argv[2])
    total = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = np.random.default_rng(seed)
    st = State(M, N)
    recreate(st, rng, 0.05)
    best = st.uncovered()
    print("M=%d N=%d mods=%d initial uncovered=%d"
          % (M, N, len(st.mods), best), flush=True)
    t0 = time.time()
    it = 0
    while time.time() - t0 < total:
        it += 1
        frac = float(rng.uniform(0.05, 0.4))
        jit = float(rng.uniform(0.0, 0.3))
        ruin(st, rng, frac)
        recreate(st, rng, jit)
        u = st.uncovered()
        if u < best:
            best = u
            print("  it=%d uncovered=%d (t=%.0fs)" % (it, u, time.time() - t0),
                  flush=True)
        if u == 0:
            congs = sorted(((a, n) for n, a in st.sel.items()),
                           key=lambda x: x[1])
            fn = "/tmp/fca_M%d.json" % M
            json.dump({"minmod": M,
                       "congruences": [[int(a), int(n)] for a, n in congs]},
                      open(fn, "w"))
            print("SUCCESS M=%d N=%d congs=%d it=%d t=%.0fs -> %s"
                  % (M, N, len(congs), it, time.time() - t0, fn))
            return
    print("FAILED M=%d N=%d best=%d it=%d" % (M, N, best, it))


if __name__ == "__main__":
    main()

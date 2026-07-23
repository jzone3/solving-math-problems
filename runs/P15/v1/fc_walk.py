#!/usr/bin/env python3
"""
WalkSAT-style local search for finite-LCM covers (P15 V1, third push).

State: every modulus n | N (n >= M) is assigned some residue a(n).
Objective: number of uncovered cells of Z_N (coverage multiplicity 0).
Move: pick a random uncovered cell x; pick a modulus n (biased toward
cheap ones, occasionally random); reassign a(n) := x mod N ... i.e. the
class through x. Incremental delta via the multiplicity array: removing
class (n, a_old) uncovers cells with cov==1 on it; adding (n, a_new)
covers cells with cov==0. Greedy-with-noise acceptance (always accept the
best of a small candidate sample; random walk with prob p).

Usage: fc_walk.py M N [total_seconds] [seed]
Writes /tmp/fcw_M{M}.json on success.
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


class Walk:
    def __init__(self, M, N, rng):
        self.N = N
        self.rng = rng
        self.mods = [d for d in divisors(N) if d >= M and d > 1]
        self.cov = np.zeros(N, dtype=np.int16)
        self.assign = {}
        # greedy-jitter initial assignment (lazy heap, as fc_anneal)
        import heapq
        unc_any = True

        def score(n):
            c = (self.cov[: (N // n) * n].reshape(N // n, n) == 0).sum(axis=0)
            g = int(c.max())
            if g == 0:
                return 0.0, int(rng.integers(n))
            near = np.flatnonzero(c >= max(1, int(g * 0.95)))
            a = int(near[rng.integers(len(near))])
            return g / n, a

        heap = []
        for n in self.mods:
            s, a = score(n)
            heap.append((-s, a, n))
        heapq.heapify(heap)
        while heap:
            neg, a_old, n = heapq.heappop(heap)
            s, a = score(n)
            if heap and -heap[0][0] > s:
                heapq.heappush(heap, (-s, a, n))
                continue
            self.assign[n] = a
            self.cov[a::n] += 1

    def uncovered(self):
        return int((self.cov == 0).sum())

    def init_unc(self):
        self.unc = set(np.flatnonzero(self.cov == 0).tolist())

    def delta_remove(self, n, a):
        sl = self.cov[a::n]
        return int((sl == 1).sum())     # cells that would become uncovered

    def delta_add(self, n, a):
        sl = self.cov[a::n]
        return int((sl == 0).sum())     # cells that would become covered

    def reassign(self, n, a_new):
        a_old = self.assign[n]
        idx = np.arange(a_old, self.N, n)
        newly_unc = idx[self.cov[idx] == 1]
        self.cov[idx] -= 1
        idx2 = np.arange(a_new, self.N, n)
        newly_cov = idx2[self.cov[idx2] == 0]
        self.cov[idx2] += 1
        self.assign[n] = a_new
        self.unc.update(newly_unc.tolist())
        self.unc.difference_update(newly_cov.tolist())

    def run(self, total, report=30.0):
        rng = self.rng
        N = self.N
        t0 = time.time()
        self.init_unc()
        best = len(self.unc)
        print("initial uncovered=%d" % best, flush=True)
        last = t0
        it = 0
        unc_list = list(self.unc)
        while time.time() - t0 < total:
            it += 1
            if not self.unc:
                return True
            if it % 64 == 0 or not unc_list:
                unc_list = list(self.unc)
            x = unc_list[rng.integers(len(unc_list))]
            if x not in self.unc:
                unc_list = list(self.unc)
                if not unc_list:
                    return True
                x = unc_list[rng.integers(len(unc_list))]
            # candidate moduli: sample, biased toward the larger (cheap,
            # fine-grained) half; move class of n through x
            half = len(self.mods) // 2
            k = min(24, len(self.mods) - half)
            cand = half + rng.choice(len(self.mods) - half, size=k,
                                      replace=False)
            if rng.random() < 0.2:
                cand = rng.choice(len(self.mods), size=k, replace=False)
            best_mv, best_d = None, None
            for ci in cand:
                n = self.mods[int(ci)]
                a_new = x % n
                a_old = self.assign[n]
                if a_new == a_old:
                    continue
                d = self.delta_remove(n, a_old) - self.delta_add(n, a_new)
                if best_d is None or d < best_d:
                    best_d, best_mv = d, (n, a_new)
            if best_mv is None:
                continue
            if best_d <= 0 or rng.random() < 0.25:
                self.reassign(*best_mv)
            u = len(self.unc)
            if u < best:
                best = u
            if time.time() - last > report:
                print("  it=%d uncovered=%d best=%d t=%.0fs"
                      % (it, u, best, time.time() - t0), flush=True)
                last = time.time()
        return False


def main():
    M, N = int(sys.argv[1]), int(sys.argv[2])
    total = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = np.random.default_rng(seed)
    w = Walk(M, N, rng)
    ok = w.run(total)
    if ok:
        congs = sorted(((a, n) for n, a in w.assign.items()),
                       key=lambda t: t[1])
        fn = "/tmp/fcw_M%d.json" % M
        json.dump({"minmod": M,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  open(fn, "w"))
        print("SUCCESS M=%d N=%d congs=%d -> %s" % (M, N, len(congs), fn))
    else:
        print("FAILED M=%d N=%d best=%d" % (M, N, w.uncovered()))


if __name__ == "__main__":
    main()

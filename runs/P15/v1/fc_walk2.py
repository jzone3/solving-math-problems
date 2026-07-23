#!/usr/bin/env python3
"""
fc_walk with an exact finisher phase (P15 V1, third push).

Phase 1: sampled WalkSAT moves (as fc_walk).
Phase 2 (uncovered below threshold): for a random uncovered cell x,
score ALL moduli exactly: gain(n) = #uncovered cells in class (x mod n)
computed by vectorized modulo over the uncovered array; loss(n) =
uniquely-covered count of n's current class. Apply the best net move.

Usage: fc_walk2.py M N [total_seconds] [seed] [finish_threshold]
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
    def __init__(self, M, N, rng, init_frac=0.95):
        self.N = N
        self.rng = rng
        self.mods = [d for d in divisors(N) if d >= M and d > 1]
        self.marr = np.array(self.mods, dtype=np.int64)
        self.cov = np.zeros(N, dtype=np.int16)
        self.assign = {}
        import heapq

        def score(n):
            c = (self.cov.reshape(N // n, n) == 0).sum(axis=0)
            g = int(c.max())
            if g == 0:
                return 0.0, int(rng.integers(n))
            near = np.flatnonzero(c >= max(1, int(g * init_frac)))
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
        self.unc = set(np.flatnonzero(self.cov == 0).tolist())
        self.rem_cache = {}          # n -> stale unique-coverage cost
        self.rem_age = {}
        self.clock = 0

    def rem_cost(self, n):
        """Cached delta_remove of n's current class (staleness-tolerant)."""
        age = self.rem_age.get(n, -10**9)
        if self.clock - age > 200:
            self.rem_cache[n] = self.delta_remove(n, self.assign[n])
            self.rem_age[n] = self.clock
        return self.rem_cache[n]

    def delta_remove(self, n, a):
        sl = self.cov[a::n]
        return int((sl == 1).sum())

    def delta_add(self, n, a):
        sl = self.cov[a::n]
        return int((sl == 0).sum())

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
        self.rem_age[n] = -10**9    # invalidate own cache

    def sampled_move(self, x):
        rng = self.rng
        half = len(self.mods) // 2
        k = min(24, len(self.mods) - half)
        cand = half + rng.choice(len(self.mods) - half, size=k, replace=False)
        if rng.random() < 0.2:
            cand = rng.choice(len(self.mods), size=k, replace=False)
        best_mv, best_d = None, None
        for ci in cand:
            n = self.mods[int(ci)]
            a_new = x % n
            if a_new == self.assign[n]:
                continue
            d = self.delta_remove(n, self.assign[n]) - self.delta_add(n, a_new)
            if best_d is None or d < best_d:
                best_d, best_mv = d, (n, a_new)
        if best_mv and (best_d <= 0 or
                        (best_d <= 50 and rng.random() < 0.25)):
            self.reassign(*best_mv)

    def exact_move(self, x, unc_arr):
        # gain(n) = #unc cells y with y ≡ x (mod n)
        diffs = unc_arr - x
        gains = (diffs[None, :] % self.marr[:, None] == 0).sum(axis=1)
        order = np.argsort(-gains)
        self.clock += 1
        best_mv, best_d = None, None
        for oi in order[:24]:
            n = self.mods[int(oi)]
            a_new = x % n
            if a_new == self.assign[n]:
                continue
            d = self.rem_cost(n) - int(gains[oi])
            if best_d is None or d < best_d:
                best_d, best_mv = d, (n, a_new)
            if best_d is not None and best_d < 0:
                break
        # verify with exact remove cost before applying
        if best_mv is not None:
            n, a_new = best_mv
            best_d = self.delta_remove(n, self.assign[n]) - \
                self.delta_add(n, a_new)
        if best_mv is None:
            return
        if (best_d < 0 or (best_d == 0 and self.rng.random() < 0.3)
                or (best_d <= 3 and self.rng.random() < 0.02)):
            self.reassign(*best_mv)

    def run(self, total, thresh, report=60.0):
        rng = self.rng
        t0 = time.time()
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
            x = unc_list[int(rng.integers(len(unc_list)))]
            if x not in self.unc:
                continue
            u = len(self.unc)
            if u <= thresh:
                self.exact_move(x, np.fromiter(self.unc, dtype=np.int64))
            else:
                self.sampled_move(x)
            if u < best:
                best = u
            if time.time() - last > report:
                print("  it=%d uncovered=%d best=%d t=%.0fs"
                      % (it, len(self.unc), best, time.time() - t0),
                      flush=True)
                last = time.time()
        return False


def main():
    M, N = int(sys.argv[1]), int(sys.argv[2])
    total = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    thresh = int(sys.argv[5]) if len(sys.argv) > 5 else 30000
    init_frac = float(sys.argv[6]) if len(sys.argv) > 6 else 0.95
    rng = np.random.default_rng(seed)
    w = Walk(M, N, rng, init_frac)
    ok = w.run(total, thresh)
    if ok:
        congs = sorted(((a, n) for n, a in w.assign.items()),
                       key=lambda t: t[1])
        fn = "/tmp/fcw2_M%d.json" % M
        json.dump({"minmod": M,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  open(fn, "w"))
        print("SUCCESS M=%d N=%d congs=%d -> %s" % (M, N, len(congs), fn))
    else:
        print("FAILED M=%d N=%d best=%d" % (M, N, len(w.unc)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Randomized-restart backtracking for finite-LCM covers (P15 V1).

Like finite_cover_np.py, but each restart perturbs the greedy choice of
modulus and residue (choose randomly among near-best), with a short time
budget per restart. Rich-N candidates only.

Usage: fc_restart.py M [total_seconds] [per_restart] [jitter] [seed] [Ncap]
"""
import json
import sys
import time
from fractions import Fraction

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


def search(M, N, rng, time_limit=20.0, branch=3, jitter=0.15):
    mods = [d for d in divisors(N) if d >= M and d > 1]
    mods.sort()
    unc = np.ones(N, dtype=bool)
    cnt = [N]
    chosen = []
    unused = mods[:]
    t0 = time.time()
    nodes = [0]

    def counts_for(n):
        return unc.reshape(N // n, n).sum(axis=0)

    def pick_mod():
        scored = []
        for n in unused:
            c = counts_for(n)
            a = int(c.argmax())
            g = int(c[a])
            if g:
                scored.append((g / n, a, n, c))
        if not scored:
            return None
        scored.sort(key=lambda t: -t[0])
        top = scored[0][0]
        pool_ = [s for s in scored if s[0] >= top * (1 - jitter)][:4]
        return pool_[rng.integers(len(pool_))]

    def rec():
        nodes[0] += 1
        if cnt[0] == 0:
            return True
        if time.time() - t0 > time_limit:
            raise TimeoutError
        if sum(Fraction(1, n) for n in unused) < Fraction(cnt[0], N):
            return False
        got = pick_mod()
        if got is None:
            return False
        _, _, n, c = got
        order = list(np.argsort(-c)[:branch])
        rng.shuffle(order)
        unused.remove(n)
        for a in order:
            a = int(a)
            if c[a] == 0:
                continue
            idx = np.arange(a, N, n)
            hit = idx[unc[idx]]
            unc[hit] = False
            cnt[0] -= len(hit)
            chosen.append((a, n))
            if rec():
                return True
            chosen.pop()
            unc[hit] = True
            cnt[0] += len(hit)
        unused.append(n)
        unused.sort()
        return False

    try:
        ok = rec()
    except TimeoutError:
        return None
    return chosen if ok else None


def main():
    M = int(sys.argv[1])
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
    per = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
    jit = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 12345
    ncap = int(float(sys.argv[6])) if len(sys.argv) > 6 else 5 * 10 ** 6
    rng = np.random.default_rng(seed)
    # richest Ns first
    cands = []
    for a in range(3, 11):
        for b in range(1, 7):
            for c in range(0, 4):
                for d in range(0, 3):
                    for e in range(0, 2):
                        N = 2**a * 3**b * 5**c * 7**d * 11**e
                        if N <= ncap:
                            r = sum(1.0 / x for x in divisors(N)
                                    if x >= M and x > 1)
                            if r >= 1.15:
                                cands.append((r, N))
    cands.sort(reverse=True)
    cands = cands[:12]
    print("M=%d candidates: %s" % (M, [(round(r, 2), N) for r, N in cands]),
          flush=True)
    t0 = time.time()
    restarts = 0
    while time.time() - t0 < total:
        for r, N in cands:
            restarts += 1
            res = search(M, N, rng, time_limit=per, jitter=jit)
            if res:
                fn = "/tmp/fcr_M%d.json" % M
                json.dump({"minmod": M,
                           "congruences": [[int(a), int(n)] for a, n in res]},
                          open(fn, "w"))
                print("SUCCESS M=%d N=%d congs=%d restarts=%d t=%.0fs -> %s"
                      % (M, N, len(res), restarts, time.time() - t0, fn))
                return
        print("  ...%d restarts, %.0fs" % (restarts, time.time() - t0),
              flush=True)
    print("FAILED M=%d after %d restarts %.0fs" % (M, restarts,
                                                   time.time() - t0))


if __name__ == "__main__":
    main()

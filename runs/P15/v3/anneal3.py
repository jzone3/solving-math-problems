#!/usr/bin/env python3
"""anneal2 with incremental hole tracking: per-move cost O(N/n + #holes)
instead of O(N), enabling lcms in the millions.

Usage: anneal3.py N m time_s [out.json] [seed]
"""
import json, sys, time
import numpy as np


def divisors(N):
    ds = []
    i = 1
    while i * i <= N:
        if N % i == 0:
            ds.append(i)
            if i != N // i:
                ds.append(N // i)
        i += 1
    return sorted(ds)


def run(N, m, budget, out=None, seed=1):
    rng = np.random.default_rng(seed)
    mods = [d for d in divisors(N) if d >= m and d > 1]
    cnt = np.zeros(N, dtype=np.int32)
    res = np.zeros(len(mods), dtype=np.int64)
    for i, n in enumerate(mods):  # greedy init, incremental holes not needed yet
        if i == 0:
            res[i] = 0
        else:
            holes0 = np.flatnonzero(cnt == 0)
            gain = np.bincount(holes0 % n, minlength=n)
            res[i] = int(gain.argmax())
        cnt[res[i]::n] += 1
    hole_arr = np.flatnonzero(cnt == 0)
    holes = set(int(h) for h in hole_arr)
    w = np.ones(N)
    energy = len(holes)
    best = energy
    best_state = res.copy()
    t0 = time.time()
    it = 0
    stall = 0
    while energy and time.time() - t0 < budget:
        it += 1
        i = int(rng.integers(0, len(mods)))
        n = mods[i]
        a_old = int(res[i])
        # weighted hole mass per residue of n — over current holes only
        h_np = np.fromiter(holes, dtype=np.int64, count=len(holes))
        gain = np.bincount(h_np % n, weights=w[h_np], minlength=n) \
            if len(holes) else np.zeros(n)
        sl = slice(a_old, N, n)
        seg = cnt[sl]
        uniq_pos = a_old + n * np.flatnonzero(seg == 1)
        lose = float(w[uniq_pos].sum())
        delta = gain - lose
        delta[a_old] = 0.0
        if rng.random() < 0.01:
            b = int(rng.integers(0, n))
        else:
            dmax = delta.max()
            cands = np.flatnonzero(delta >= dmax - 1e-9)
            b = int(cands[rng.integers(0, len(cands))])
        if b != a_old:
            cnt[a_old::n] -= 1
            new_holes = a_old + n * np.flatnonzero(cnt[a_old::n] == 0)
            for t in new_holes:
                holes.add(int(t))
            covered = b + n * np.flatnonzero(cnt[b::n] == 0)
            cnt[b::n] += 1
            for t in covered:
                holes.discard(int(t))
            res[i] = b
            energy = len(holes)
        if energy < best:
            best = energy
            best_state = res.copy()
            stall = 0
            print(f"best={best} it={it} t={time.time()-t0:.1f}s", flush=True)
        else:
            stall += 1
            if stall >= 4 * len(mods):
                hb = np.fromiter(holes, dtype=np.int64, count=len(holes))
                w[hb] += 1.0
                stall = 0
    if energy == 0:
        sol = sorted(((int(res[i]), n) for i, n in enumerate(mods)),
                     key=lambda x: x[1])
        cov = bytearray(N)
        for a, n in sol:
            for t in range(a, N, n):
                cov[t] = 1
        assert all(cov)
        print(f"SOLVED size={len(sol)} t={time.time()-t0:.1f}s it={it}", flush=True)
        if out:
            json.dump({"m": m, "N": N, "cover": sol}, open(out, "w"))
        return sol
    print(f"NOSOLUTION best={best} t={time.time()-t0:.1f}s it={it}", flush=True)
    return None


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    out = sys.argv[4] if len(sys.argv) > 4 else None
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    run(N, m, budget, out, seed)

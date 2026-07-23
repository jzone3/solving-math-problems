#!/usr/bin/env python3
"""Weighted min-conflicts (breakout method) for covering systems, numpy-fast.

Same state space as anneal.py; holes carry dynamic weights that are bumped when
search stagnates, deforming the landscape to escape local minima. Move choice:
reassign a modulus to the residue with max weighted gain (ties random).

Usage: anneal2.py N m time_s [out.json] [seed]
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
    idx = {n: i for i, n in enumerate(mods)}
    cnt = np.zeros(N, dtype=np.int32)
    tmod = {n: np.arange(N) % n for n in mods}
    # greedy init: smallest moduli first, each takes the residue hitting most holes
    res = np.zeros(len(mods), dtype=np.int64)
    for i, n in enumerate(mods):
        holes = cnt == 0
        gain = np.bincount(tmod[n][holes], minlength=n)
        res[i] = int(gain.argmax())
        cnt[res[i]::n] += 1
    w = np.ones(N)
    energy = int((cnt == 0).sum())
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
        holes = cnt == 0
        # weighted hole mass per residue class of n
        gain = np.bincount(tmod[n][holes], weights=w[holes], minlength=n)
        sl = slice(a_old, N, n)
        lose = float(w[sl][cnt[sl] == 1].sum())
        delta = gain - lose
        delta[a_old] = 0.0
        dmax = delta.max()
        if rng.random() < 0.01:
            b = int(rng.integers(0, n))
        else:
            cands = np.flatnonzero(delta >= dmax - 1e-9)
            b = int(cands[rng.integers(0, len(cands))])
        if b != a_old:
            cnt[a_old::n] -= 1
            cnt[b::n] += 1
            res[i] = b
            energy = int((cnt == 0).sum())
        if energy < best:
            best = energy
            best_state = res.copy()
            stall = 0
            print(f"best={best} it={it} t={time.time()-t0:.1f}s", flush=True)
        else:
            stall += 1
            if stall >= 4 * len(mods):  # breakout: bump weights of current holes
                w[cnt == 0] += 1.0
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
    # endgame repair: restore best state, strip moduli that cover nothing
    # uniquely, and let kissat place them exactly onto the remaining holes
    res = best_state
    cnt[:] = 0
    for i, n in enumerate(mods):
        cnt[int(res[i])::n] += 1
    uniq = []
    for i, n in enumerate(mods):
        sl = cnt[int(res[i])::n]
        uniq.append((int((sl == 1).sum()), i))
    uniq.sort()
    freed = []
    n_free = min(40, len(mods) // 2)
    for _, i in uniq[:n_free]:
        n = mods[i]
        cnt[int(res[i])::n] -= 1
        freed.append(n)
    holes = np.flatnonzero(cnt == 0)
    print(f"repair: {len(holes)} holes, {len(freed)} freed mods", flush=True)
    if len(holes) and len(freed) and len(holes) < 100000:
        from layered2 import sat_final
        sol, status = sat_final([int(h) for h in holes], freed, 1800)
        print(f"repair SAT: {status}", flush=True)
        if sol is not None:
            fixed = {n for _, n in sol}
            cover = sol + [(int(res[i]), n) for i, n in enumerate(mods)
                           if n not in freed]
            cover += [(int(res[i]), n) for i, n in enumerate(mods)
                      if n in freed and n not in fixed]
            cov = bytearray(N)
            ms = [n for _, n in cover]
            assert len(ms) == len(set(ms)) and min(ms) >= m
            for a, n in cover:
                for t in range(a % n, N, n):
                    cov[t] = 1
            assert all(cov)
            print(f"SOLVED-REPAIR size={len(cover)}", flush=True)
            if out:
                json.dump({"m": m, "N": N,
                           "cover": sorted(cover, key=lambda x: x[1])},
                          open(out, "w"))
            return cover
    print(f"NOSOLUTION best={best} t={time.time()-t0:.1f}s it={it}", flush=True)
    return None


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    out = sys.argv[4] if len(sys.argv) > 4 else None
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    run(N, m, budget, out, seed)

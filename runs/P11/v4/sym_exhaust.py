#!/usr/bin/env python3
"""Exhaustive search over multiplier-symmetric ternary sequences for CW(n,k).

For a multiplier subgroup <t> <= Z_n^* with orbits O_1..O_m on Z_n, any
sequence fixed by t is constant x_o in {-1,0,+1} on each orbit. Weight
k = sum_{x_o != 0} |O_o| (subset-sum over orbit sizes) and
DC = sum x_o |O_o| = +-s. This enumerates ALL such sequences:
  1. DFS over subsets of orbits with sizes summing exactly to k,
  2. DFS over sign patterns with running DC bound,
  3. exact autocorrelation check at leaves via precomputed pairwise
     cross-correlation tables C[o][p][shift].
Result is DEFINITIVE for the subgroup: either a witness or a proof that no
CW(n,k) is fixed by t.

Usage: sym_exhaust.py n s t [max_leaves]
Exit: 0 witness found / 2 exhausted-none / 3 skipped (too big or t not unit)
"""
import sys
from math import gcd
import numpy as np

def orbits_of(n, t):
    seen = [False]*n; parts = []
    for i in range(n):
        if not seen[i]:
            cur = []; j = i
            while not seen[j]:
                seen[j] = True; cur.append(j); j = (j*t) % n
            parts.append(sorted(cur))
    return parts

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2]); t = int(sys.argv[3])
    max_leaves = int(sys.argv[4]) if len(sys.argv) > 4 else 200_000_000
    k = s*s
    if gcd(t, n) != 1:
        print(f"SKIP n={n} t={t}: not a unit"); return 3
    parts = orbits_of(n, t)
    m = len(parts)
    sizes = [len(p) for p in parts]

    # DP count of (subset,sign) leaves: each orbit contributes 0 or |O| to weight,
    # with 2 sign choices when included.
    from functools import lru_cache
    order = sorted(range(m), key=lambda o: -sizes[o])
    suffix = [0]*(m+1)
    for i in range(m-1, -1, -1): suffix[i] = suffix[i+1] + sizes[order[i]]
    cnt = {}
    def count(i, w):
        if w == k: return 1
        if i >= m or w > k or w + suffix[i] < k: return 0
        key = (i, w)
        if key in cnt: return cnt[key]
        r = count(i+1, w) + count(i+1, w + sizes[order[i]]) * 2
        cnt[key] = r
        return r
    total = count(0, 0)
    print(f"n={n} s={s} t={t} m={m} sizes={sorted(sizes)} approx_leaves={total}", flush=True)
    if total > max_leaves:
        print(f"SKIP n={n} t={t}: too many leaves ({total} > {max_leaves})"); return 3

    # pairwise cross-correlation tables: C[o][p][sh] = # {(i,j) in O_o x O_p : j-i = sh}
    ind = np.zeros((m, n), dtype=np.int64)
    for o, p in enumerate(parts):
        ind[o, p] = 1
    F = np.fft.rfft(ind, axis=1)
    C = np.empty((m, m, n), dtype=np.int64)
    for o in range(m):
        cc = np.fft.irfft(np.conj(F[o])[None, :] * F, n, axis=1)
        C[o] = np.rint(cc).astype(np.int64)

    R = np.zeros(n, dtype=np.int64)   # running autocorrelation of chosen orbits
    chosen = []                        # list of (orbit, sign)
    sol = []
    leaves = 0

    def dfs(i, w, dc):
        nonlocal leaves
        if sol: return
        if w == k:
            leaves += 1
            if dc in (s, -s) and R[0] == k and not R[1:].any():
                x = np.zeros(n, dtype=int)
                for (o, sg) in chosen:
                    x[parts[o]] = sg
                sol.append(x.copy())
            return
        if i >= m or w + suffix[i] < k: return
        o = order[i]
        sz = sizes[o]
        # skip orbit o
        dfs(i+1, w, dc)
        if sol: return
        if w + sz <= k:
            for sg in (1, -1):
                R_add = 0
                # update R: self-correlation + cross with already-chosen
                R[:] += C[o, o]
                for (p, sp) in chosen:
                    q = sg * sp
                    R[:] += q * (C[p, o] + C[o, p])
                chosen.append((o, sg))
                # valid prune: remaining weight is exactly rem, so DC can move by at most rem
                rem = k - w - sz
                dcn = dc + sg*sz
                if min(abs(s - dcn), abs(-s - dcn)) <= rem:
                    dfs(i+1, w+sz, dcn)
                chosen.pop()
                R[:] -= C[o, o]
                for (p, sp) in chosen:
                    q = sg * sp
                    R[:] -= q * (C[p, o] + C[o, p])
                if sol: return

    dfs(0, 0, 0)
    if sol:
        vec = ''.join('+' if v > 0 else ('-' if v < 0 else '0') for v in sol[0])
        print(f"SOLUTION n={n} k={k} t={t} vec={vec}", flush=True)
        return 0
    print(f"EXHAUSTED n={n} k={k} t={t} m={m}: no multiplier-symmetric solution (leaves={leaves})", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

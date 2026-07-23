#!/usr/bin/env python3
"""Exhaustive Hamming-ball polish in orbit space around a near-solution.

Given a multiplier-symmetric near-miss (full vec string) for CW(n,s^2) with
multiplier t, enumerate ALL orbit-value vectors within Hamming distance <= r
(each changed orbit takes any of its 2 other ternary values) and report the
minimum exact energy E = sum_{sh!=0} R(sh)^2 + (wt-k)^2.  Definitive within
the ball.

Usage: ball.py n s t r vec
"""
import sys
from math import gcd
from itertools import combinations, product
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
    n = int(sys.argv[1]); s = int(sys.argv[2]); t = int(sys.argv[3]); r = int(sys.argv[4])
    vec = sys.argv[5]
    k = s*s
    parts = orbits_of(n, t); m = len(parts)
    a = np.array([1 if c=='+' else (-1 if c=='-' else 0) for c in vec])
    x = np.zeros(m, dtype=int)
    for o,p in enumerate(parts):
        vals = set(int(a[i]) for i in p)
        assert len(vals)==1, f"vec not constant on orbit {o}"
        x[o] = vals.pop()

    exp_idx = np.zeros(n, dtype=int)
    for o,p in enumerate(parts):
        for i in p: exp_idx[i]=o

    def batch_E(X):        # X: (B,m) orbit values -> exact E
        Be = X[:, exp_idx].astype(float)
        wt = np.sum(Be*Be, axis=1).astype(np.int64)
        rr = np.fft.irfft(np.abs(np.fft.rfft(Be, axis=1))**2, n, axis=1)
        ri = np.rint(rr).astype(np.int64)
        return np.sum(ri[:,1:]**2, axis=1) + (wt-k)**2

    E0 = int(batch_E(x[None,:])[0])
    print(f"start E={E0} m={m}", flush=True)
    best = (E0, x.copy())
    alt = {v: [w for w in (-1,0,1) if w!=v] for v in (-1,0,1)}
    for rad in range(1, r+1):
        cnt = 0
        batch = []
        for orbs in combinations(range(m), rad):
            for vals in product(*[alt[x[o]] for o in orbs]):
                y = x.copy()
                for o,v in zip(orbs, vals): y[o]=v
                batch.append(y)
                if len(batch)==4096:
                    E = batch_E(np.array(batch))
                    j = int(np.argmin(E)); cnt += len(batch)
                    if E[j] < best[0]: best = (int(E[j]), batch[j].copy())
                    batch=[]
        if batch:
            E = batch_E(np.array(batch)); j=int(np.argmin(E)); cnt += len(batch)
            if E[j] < best[0]: best=(int(E[j]), batch[j].copy())
        print(f"radius {rad}: {cnt} candidates, bestE={best[0]}", flush=True)
        if best[0]==0: break
    vecb = ''.join('+' if v>0 else ('-' if v<0 else '0') for v in best[1][exp_idx])
    print(f"{'SOLUTION' if best[0]==0 else 'BALLBEST'} n={n} k={k} t={t} E={best[0]} vec={vecb}", flush=True)
    return 0 if best[0]==0 else 2

if __name__ == "__main__":
    sys.exit(main())

"""Find the smallest n where some graphical (threshold) sequence violates (*)
(g > 0), searching integer block-threshold configs with <= 4 blocks per n.
By Schur-convexity the max of g over graphical sequences is attained at a
threshold sequence, and small-block thresholds appear to dominate; this scan
gives a strong upper estimate of the true n0 (exact for the searched class).
"""
import itertools, sys
import numpy as np
from blocks import objectives
from scipy.optimize import minimize

def max_g(n):
    best = (-1e18, None, None)
    for k in (2, 3, 4):
        for types in itertools.product([0, 1], repeat=k):
            if not any(types): continue
            if any(types[i] == types[i+1] for i in range(k-1)): continue
            def neg(x):
                sizes = np.concatenate([x, [n - x.sum()]])
                if np.any(sizes < 1.0): return 1e6
                r = objectives(sizes, types, n)
                return 1e6 if r is None else -r[1]
            for w0 in range(5):
                rng = np.random.default_rng(97 * k + w0)
                x0 = rng.dirichlet(np.ones(k))[:-1] * n
                res = minimize(neg, x0, method='Nelder-Mead',
                               options={'maxiter': 3000, 'fatol': 1e-15})
                sizes = np.concatenate([res.x, [n - res.x.sum()]])
                base = np.maximum(np.round(sizes).astype(int), 1)
                base[-1] += int(n - base.sum())
                if base[-1] < 1: continue
                cur = list(base)
                def ev(sz):
                    if any(x < 1 for x in sz) or sum(sz) != n: return -1e18
                    r = objectives(np.array(sz, float), types, n)
                    return -1e18 if r is None else r[1]
                curv = ev(cur)
                improved = True
                while improved:
                    improved = False
                    for i in range(k):
                        for j in range(k):
                            if i == j: continue
                            cand = cur[:]; cand[i] += 1; cand[j] -= 1
                            v2 = ev(cand)
                            if v2 > curv + 1e-15:
                                cur, curv, improved = cand, v2, True
                if curv > best[0]:
                    best = (curv, types, tuple(cur))
    return best

lo_pos = None
for n in list(range(20, 200, 10)) + list(range(200, 760, 25)):
    v, types, sizes = max_g(n)
    flag = " <-- POSITIVE" if v > 1e-12 else ""
    print(f"n={n}: max g = {v:.3e} types={types} sizes={sizes}{flag}", flush=True)
    if v > 1e-12 and lo_pos is None:
        lo_pos = n
        break
if lo_pos:
    lo = lo_pos - (10 if lo_pos <= 200 else 25); hi = lo_pos
    for n in range(lo + 1, hi + 1):
        v, types, sizes = max_g(n)
        if v > 1e-12:
            print(f"FIRST positive n (block-threshold class): {n} g={v:.3e} "
                  f"types={types} sizes={sizes}")
            break

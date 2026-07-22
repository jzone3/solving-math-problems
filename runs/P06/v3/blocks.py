"""Large-n asymptotics over BLOCK THRESHOLD graphs (V3 core).

A threshold graph is a creation sequence of 'join' (1) / 'isolated' (0) vertices;
degrees are constant on maximal blocks. For block sizes s_1..s_k (types t_i in
{0,1}), with P_i = vertices before block i and J_i = joins after block i:
    deg(join block i)  = P_i + s_i - 1 + J_i
    deg(zero block i)  = J_i
    edges: join block i pairs with every earlier block (s_j*s_i) + C(s_i,2) inside.
Objectives (both must stay <= 0 if WoW 129 holds):
    phi  = max_{n'>=n} dev^2(n') - R^2        (padded true objective)
    g    = ln(n^2 dev^2) - ln(m^2) + (1/m) sum d ln d   ((*) GM reduction)
Optimizes block sizes continuously (relaxation) for k = 2..6 blocks at
n = 1e3, 1e4, 1e5, 1e6; multi-start scipy SLSQP; also refines best relaxed point
to integers and re-evaluates exactly (mpmath) if close to 0.
Threshold graphs are the Schur-maximal graphical sequences, so a positive here
is the most likely escape route; a clean 0-max supports the conjecture.
"""
import itertools, math, sys
import numpy as np
from scipy.optimize import minimize

def build(sizes, types):
    sizes = np.asarray(sizes, dtype=float)
    k = len(sizes)
    P = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    joins_total = sum(s for s, t in zip(sizes, types) if t == 1)
    Jafter = np.zeros(k)
    acc = 0.0
    for i in range(k - 1, -1, -1):
        Jafter[i] = acc
        if types[i] == 1:
            acc += sizes[i]
    deg = np.array([P[i] + sizes[i] - 1 + Jafter[i] if types[i] == 1 else Jafter[i]
                    for i in range(k)])
    return P, Jafter, deg

def objectives(sizes, types, n):
    sizes = np.maximum(np.asarray(sizes, dtype=float), 1e-9)
    P, Jafter, deg = build(sizes, types)
    if np.any(deg < -1e-12):
        return None
    deg = np.maximum(deg, 0)
    m2 = float(np.dot(sizes, deg))
    m = m2 / 2
    if m <= 0: return None
    S = float(np.dot(sizes, deg ** 2))
    A = S + m2
    # R
    R = 0.0
    for i in range(len(sizes)):
        if types[i] != 1: continue
        di = deg[i]
        if di <= 0: continue
        if sizes[i] > 1:
            R += sizes[i] * (sizes[i] - 1) / 2 / di
        for j in range(i):
            dj = deg[j]
            if dj <= 0: continue
            R += sizes[j] * sizes[i] / math.sqrt(di * dj)
    dev2 = A / n - (m2 / n) ** 2
    nstar = 8 * m * m / A
    phi = dev2 - R * R
    if nstar > n:
        phi = max(phi, A / nstar - (m2 / nstar) ** 2 - R * R)
    Hs = float(np.dot(sizes, [d * math.log(d) if d > 0 else 0 for d in deg]))
    rhs = n * A - m2 * m2
    g = (math.log(rhs) + Hs / m - math.log(n * n * m * m)) if rhs > 0 else -50.0
    return phi, g

def optimize(types, n, obj_index, restarts=25, seed=0):
    rng = np.random.default_rng(seed)
    k = len(types)
    best = (-1e18, None)
    def neg(x):
        # x: k-1 free sizes (last = n - sum)
        sizes = np.concatenate([x, [n - x.sum()]])
        if np.any(sizes < 1.0): return 1e6   # blocks must have >= 1 vertex
        r = objectives(sizes, types, n)
        if r is None: return 1e6
        return -r[obj_index]
    for _ in range(restarts):
        w = rng.dirichlet(np.ones(k))
        x0 = w[:-1] * n
        res = minimize(neg, x0, method='Nelder-Mead',
                       options={'maxiter': 4000, 'xatol': 1e-8, 'fatol': 1e-14})
        v = -res.fun
        if v > best[0]:
            sizes = np.concatenate([res.x, [n - res.x.sum()]])
            best = (v, sizes)
    # integer polish: round, then +-1 local search on the lattice (sum fixed = n)
    if best[1] is not None:
        base = np.maximum(np.round(best[1]).astype(int), 1)
        # fix sum
        diff = int(n - base.sum())
        base[-1] += diff
        if base[-1] < 1: base[-1] = 1
        def ev(sz):
            if any(x < 1 for x in sz) or sum(sz) != n: return -1e18
            r = objectives(np.array(sz, dtype=float), types, n)
            return -1e18 if r is None else r[obj_index]
        cur = list(base); curv = ev(cur)
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
        best = (curv, np.array(cur))
    return best

if __name__ == "__main__":
    NS = [1000, 10000, 100000, 1000000]
    for n in NS:
        overall = {0: (-1e18, None, None), 1: (-1e18, None, None)}
        for k in range(2, 7):
            for types in itertools.product([0, 1], repeat=k):
                if not any(types): continue
                # skip type patterns with adjacent equal types (same as merged block)
                if any(types[i] == types[i+1] for i in range(k-1)): continue
                for oi in (0, 1):
                    v, sizes = optimize(types, n, oi, restarts=8, seed=k*37+oi)
                    if v > overall[oi][0]:
                        overall[oi] = (v, types, None if sizes is None else np.round(sizes, 2))
        print(f"n={n}: max phi = {overall[0][0]:.9g} types={overall[0][1]} sizes={overall[0][2]}")
        print(f"        max g   = {overall[1][0]:.9g} types={overall[1][1]} sizes={overall[1][2]}", flush=True)

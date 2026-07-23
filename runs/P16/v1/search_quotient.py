#!/usr/bin/env python3
"""P16 v1: direct counterexample search for BHS bounds 44 and 46 over
equitable-partition quotient graphs, with simulated annealing on the
violation margin.

Bounds (EXACT forms from DHS arXiv:2606.14550 LaTeX source, Table 2 --
note the "2 +" is OUTSIDE the square root):
  Bound 44: mu(G) <= max_{ij in E} 2 + sqrt(2((d_i-1)^2 + (d_j-1)^2 + m_i m_j - d_i d_j))
  Bound 46: mu(G) <= max_{ij in E} 2 + sqrt(2(d_i^2 + d_j^2) - 16 d_i d_j/(m_i + m_j) + 4)

State: cell sizes n_1..n_k and nonnegative-integer quotient matrix B,
realizable per DHS Lemma (b_ii <= n_i - 1, b_ii or n_i even,
b_ij <= n_j, n_i b_ij = n_j b_ji), quotient connected across cells.
mu(G) >= rho(L_B) where L_B = diag(s) - B; search maximizes
margin = rho(L_B) - RHS(B).  Float search only; exact certification is
done separately in verify_p16.py.
"""
import math
import random
import sys
import numpy as np


def profile(n, B):
    """Return s (degrees) and m (avg neighbor degrees) per cell; None if invalid."""
    k = len(n)
    s = [sum(B[i]) for i in range(k)]
    if any(x < 1 for x in s):
        return None
    m = [sum(B[i][j] * s[j] for j in range(k)) / s[i] for i in range(k)]
    return s, m


def realizable(n, B):
    k = len(n)
    for i in range(k):
        if B[i][i] > n[i] - 1:
            return False
        if B[i][i] % 2 == 1 and n[i] % 2 == 1:
            return False
        for j in range(k):
            if i != j:
                if B[i][j] > n[j]:
                    return False
                if n[i] * B[i][j] != n[j] * B[j][i]:
                    return False
    # connectivity of the cell graph (across-cell edges only), unless k == 1
    if k == 1:
        return B[0][0] >= 1
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in range(k):
            if v not in seen and u != v and B[u][v] > 0:
                seen.add(v)
                stack.append(v)
    return len(seen) == k


def cell_edges(n, B):
    k = len(n)
    E = []
    for i in range(k):
        if B[i][i] > 0:
            E.append((i, i))
        for j in range(i + 1, k):
            if B[i][j] > 0:
                E.append((i, j))
    return E


def bound_value(which, di, mi, dj, mj):
    if which == 44:
        inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    elif which == 46:
        inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    else:
        raise ValueError(which)
    if inner < 0:
        return None  # bound expression not real on this edge
    return 2 + math.sqrt(inner)


def rhs(which, n, B, prof):
    s, m = prof
    vals = []
    for (i, j) in cell_edges(n, B):
        v = bound_value(which, s[i], m[i], s[j], m[j])
        if v is None:
            return None  # skip: want clean counterexamples with real RHS
        vals.append(v)
    return max(vals)


def quotient_mu(n, B):
    """rho(L_B) via symmetrized similarity: M_ij = -e_ij/sqrt(n_i n_j), diag s_i."""
    k = len(n)
    M = np.zeros((k, k))
    for i in range(k):
        M[i][i] = sum(B[i])
        for j in range(k):
            if i != j:
                M[i][j] = -B[i][j] * math.sqrt(n[i] / n[j])
    # M symmetric because n_i b_ij = n_j b_ji; but b_ii stays on diagonal via s
    return float(np.max(np.linalg.eigvalsh((M + M.T) / 2)))


def margin(which, n, B):
    if not realizable(n, B):
        return None
    prof = profile(n, B)
    if prof is None:
        return None
    r = rhs(which, n, B, prof)
    if r is None:
        return None
    return quotient_mu(n, B) - r


def random_state(rng, kmax=5, nmax=60, bmax=12):
    k = rng.randint(1, kmax)
    n = [rng.randint(1, nmax) for _ in range(k)]
    B = [[0] * k for _ in range(k)]
    for i in range(k):
        for j in range(i, k):
            if i == j:
                lim = min(bmax, n[i] - 1)
                if lim >= 0:
                    v = rng.randint(0, max(0, lim))
                    if v % 2 == 1 and n[i] % 2 == 1:
                        v -= 1
                    B[i][i] = max(0, v)
            else:
                bij = rng.randint(0, min(bmax, n[j]))
                # enforce n_i b_ij = n_j b_ji
                if (n[i] * bij) % n[j] == 0:
                    bji = n[i] * bij // n[j]
                    if bji <= n[i]:
                        B[i][j], B[j][i] = bij, bji
    return n, B


def neighbor(rng, n, B, nmax=400, bmax=200):
    k = len(n)
    n = list(n)
    B = [row[:] for row in B]
    move = rng.random()
    if move < 0.35 and k >= 1:
        # tweak an off-diagonal pair keeping n_i b_ij = n_j b_ji
        if k >= 2:
            i, j = rng.sample(range(k), 2)
            d = rng.choice([-1, 1])
            g = math.gcd(n[i], n[j])
            step_i = n[j] // g  # b_ij must change in multiples of n_j/g
            B[i][j] += d * step_i
            B[j][i] += d * (n[i] // g)
    elif move < 0.55:
        i = rng.randrange(k)
        d = rng.choice([-2, 2]) if n[i] % 2 == 0 else rng.choice([-1, 1, 2, -2])
        B[i][i] += d
    elif move < 0.9:
        i = rng.randrange(k)
        d = rng.choice([-1, 1, rng.randint(-5, 5)])
        newn = n[i] + d
        if 1 <= newn <= nmax:
            n[i] = newn
    else:
        # duplicate or drop a cell
        if rng.random() < 0.5 and k < 6:
            i = rng.randrange(k)
            newrow = B[i][:] + [0]
            for r in range(k):
                B[r].append(B[r][i] if r != i else 0)
            B.append(newrow)
            n.append(n[i])
        elif k > 1:
            i = rng.randrange(k)
            n.pop(i)
            B.pop(i)
            for row in B:
                row.pop(i)
    if any(x < 0 for row in B for x in row) or any(x > bmax for row in B for x in row):
        return None
    return n, B


def anneal(which, seed, iters=200000, log=None):
    rng = random.Random(seed)
    best = (-1e9, None)
    cur = None
    curval = None
    T0, T1 = 1.0, 0.01
    for t in range(iters):
        if cur is None:
            cand = random_state(rng)
            v = margin(which, *cand)
            if v is None:
                continue
            cur, curval = cand, v
            continue
        nb = neighbor(rng, *cur)
        if nb is None:
            continue
        v = margin(which, *nb)
        if v is None:
            continue
        T = T0 * (T1 / T0) ** (t / iters)
        if v > curval or rng.random() < math.exp((v - curval) / T):
            cur, curval = nb, v
            if v > best[0]:
                best = (v, nb)
                if log and v > -0.5:
                    print(f"[{which}] seed={seed} t={t} margin={v:.6f} n={nb[0]} B={nb[1]}", flush=True)
        if rng.random() < 0.0005:
            cur = None  # restart
    return best


if __name__ == "__main__":
    which = int(sys.argv[1])
    nseeds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    overall = (-1e9, None)
    for s in range(seed0, seed0 + nseeds):
        v, st = anneal(which, s, log=True)
        print(f"[{which}] seed={s} BEST margin={v:.6f} state={st}", flush=True)
        if v > overall[0]:
            overall = (v, st)
    print(f"[{which}] OVERALL best margin={overall[0]:.6f} state={overall[1]}")

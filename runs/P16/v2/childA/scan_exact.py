"""Wide instance sweep over 4-cell and 6-cell symmetric bipartite quotient
perturbations of the d-regular equality manifold.

Float screening (numpy) at several concrete d; any instance with gap below
threshold goes to an EXACT rational Sturm confirmation (sympy; no floats on
the accept path).  All quotient matrices are symmetric integer matrices =>
realizable as equitable partitions with equal large even cell sizes (DHS
Lemma 2.3), so a confirmed violation would be a genuine counterexample.
"""
import itertools
import math
import random
from fractions import Fraction

import numpy as np
import sympy as sp

random.seed(1616)

D_VALUES = (50, 200, 1000)
THRESH = -1e-9


def gap_float(Q, dv, bound):
    """Q: k x k integer numpy (full symmetric quotient, entries at d=dv).
    Returns max-edge-term - mu (float)."""
    s = Q.sum(axis=1).astype(float)
    if (s <= 0).any():
        return None
    m = (Q @ s) / s
    L = np.diag(s) - Q
    mu = np.linalg.eigvalsh(L.astype(float))[-1]
    best = -math.inf
    k = len(s)
    for i in range(k):
        for j in range(i, k):
            if Q[i, j] > 0:
                di, dj, mi, mj = s[i], s[j], m[i], m[j]
                if bound == 44:
                    arg = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
                else:
                    arg = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
                if arg >= 0:
                    best = max(best, 2 + math.sqrt(arg))
    return best - mu


def exact_check(Q, bound):
    """Exact: does mu(L_Q) exceed ALL edge terms? Returns (violated, detail)."""
    k = len(Q)
    s = [int(sum(Q[i])) for i in range(k)]
    m = [Fraction(sum(Q[i][j] * s[j] for j in range(k)), s[i]) for i in range(k)]
    max_arg = None
    for i in range(k):
        for j in range(i, k):
            if Q[i][j] > 0:
                di, dj, mi, mj = map(Fraction, (s[i], s[j], m[i], m[j]))
                if bound == 44:
                    arg = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
                else:
                    arg = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
                if arg >= 0 and (max_arg is None or arg > max_arg):
                    max_arg = arg
    if max_arg is None:
        return True, "all edge terms undefined (-inf): trivial violation"
    x = sp.Symbol('x')
    L = sp.Matrix([[ (s[i] if i == j else 0) - Q[i][j] for j in range(k)] for i in range(k)])
    poly = sp.Poly(L.charpoly(x).as_expr(), x)
    # mu > 2 + sqrt(max_arg)  <=>  exists root lam with lam > 2 and (lam-2)^2 > max_arg
    # bisect a rational lower bound on mu
    lo, hi = sp.Rational(0), sp.Rational(4 * max(s) + 4)
    for _ in range(80):
        mid = (lo + hi) / 2
        if sp.polys.polytools.count_roots(poly, inf=mid, sup=None) >= 1:
            lo = mid
        else:
            hi = mid
    lam_lo = lo
    ok = lam_lo > 2 and (lam_lo - 2) ** 2 > sp.Rational(max_arg)
    return bool(ok), f"lam_lo={sp.nsimplify(lam_lo, rational=True)} max_arg={max_arg}"


def full_from_blocks(P):
    """P: kxk' integer block (left x right). Return full symmetric quotient."""
    kl, kr = P.shape
    Q = np.zeros((kl + kr, kl + kr), dtype=np.int64)
    Q[:kl, kl:] = P
    Q[kl:, :kl] = P.T
    return Q


def sweep4():
    print("== sweep 4-cell: w in 1..6, p in -3..3^4, d in", D_VALUES)
    n = 0
    best = (math.inf, None)
    cands = []
    for w in range(1, 7):
        for p in itertools.product(range(-3, 4), repeat=4):
            for dv in D_VALUES:
                P = np.array([[dv - w + p[0], w + p[1]], [w + p[2], dv - w + p[3]]])
                if (P < 0).any():
                    continue
                Q = full_from_blocks(P)
                for bound in (44, 46):
                    g = gap_float(Q, dv, bound)
                    if g is None:
                        continue
                    n += 1
                    if g < best[0]:
                        best = (g, (w, p, dv, bound))
                    if g < THRESH:
                        cands.append((Q.tolist(), bound, (w, p, dv), g))
    print(f"  {n} evals; min gap {best[0]:.3e} at {best[1]}; {len(cands)} candidates")
    return cands


def sweep6():
    print("== sweep 6-cell: random blocks, d in", D_VALUES)
    n = 0
    best = (math.inf, None)
    cands = []
    trials = []
    for u, v in itertools.product(range(1, 5), repeat=2):
        base = [[-u - v, u, v], [u, -u - v, v], [v, v, -2 * v]]  # offsets from d on diag
        for (i, j), delta in itertools.product(itertools.product(range(3), repeat=2),
                                               (-2, -1, 1, 2)):
            pert = [[0] * 3 for _ in range(3)]
            pert[i][j] = delta
            trials.append((base, pert))
    for _ in range(30000):
        u, v = random.randint(1, 4), random.randint(1, 4)
        base = [[-u - v, u, v], [u, -u - v, v], [v, v, -2 * v]]
        pert = [[random.randint(-2, 2) for _ in range(3)] for _ in range(3)]
        trials.append((base, pert))
    for base, pert in trials:
        for dv in D_VALUES:
            P = np.array([[(dv if i == j else 0) + base[i][j] + pert[i][j]
                           for j in range(3)] for i in range(3)])
            if (P < 0).any():
                continue
            Q = full_from_blocks(P)
            for bound in (44, 46):
                g = gap_float(Q, dv, bound)
                if g is None:
                    continue
                n += 1
                if g < best[0]:
                    best = (g, (base, pert, dv, bound))
                if g < THRESH:
                    cands.append((Q.tolist(), bound, (base, pert, dv), g))
    print(f"  {n} evals; min gap {best[0]:.3e} at {best[1]}; {len(cands)} candidates")
    return cands


if __name__ == "__main__":
    cands = sweep4() + sweep6()
    print(f"\n{len(cands)} float candidates -> exact Sturm check")
    for Q, bound, meta, g in cands:
        ok, detail = exact_check(Q, bound)
        print(f"  bound {bound} meta {meta} float gap {g:.3e}: "
              f"{'VIOLATION CONFIRMED' if ok else 'refuted (float noise)'} [{detail}]")
    if not cands:
        print("  none")

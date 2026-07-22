"""
P06/V1 frontier claim: conjecture 129 holds for ALL graphs on n <= N_MAX vertices.

Method: dev(L(G)) depends only on the degree sequence d (dev^2 = Var(d)+dbar),
and R(G) >= R_lb(d) for every realization G of d (each vertex's neighbor weight
sum is at least the sum of its d_u smallest available weights, w = d^{-1/2}).
So it suffices that dev(d) <= R_lb(d) for every graphical sequence d of length n.

Rigor: enumerate all non-increasing graphical sequences (Erdos-Gallai);
score with floats; any sequence with float score > -1e-6 is re-checked with
mpmath at 60 digits (float error across <= n^2 term sums is << 1e-6).
A counterexample sequence must satisfy the mpmath check dev > R_lb; none may.

Prints per-n summary: #sequences, #near-zero re-checked, max exact-ish score.
"""
import math
import sys
import time

from mpmath import mp, mpf, sqrt as msqrt

sys.path.insert(0, ".")
from degseq_search import erdos_gallai, dev, randic_lb

mp.dps = 60


def score_mp(seq):
    n = len(seq)
    s1, s2 = sum(seq), sum(x * x for x in seq)
    dev2 = mpf(s1 + s2) / n - (mpf(s1) / n) ** 2
    devv = msqrt(dev2) if dev2 > 0 else mpf(0)
    pos = sorted(x for x in seq if x > 0)
    w = sorted(1 / msqrt(mpf(x)) for x in pos)
    pref = [mpf(0)]
    for x in w:
        pref.append(pref[-1] + x)
    total = mpf(0)
    for d_u in pos:
        w_u = 1 / msqrt(mpf(d_u))
        k = d_u
        s = pref[k]
        if w_u <= w[k - 1]:
            s = s - w_u + w[k]
        total += w_u * s
    return devv - total / 2


def run(n, report_every=5.0):
    cnt = [0]
    near = []
    best = [-1e18, None]
    t0 = time.time()
    last = [t0]
    seq = []

    def rec(i, maxd):
        if i == n:
            if erdos_gallai(seq):
                cnt[0] += 1
                s = dev(seq) - randic_lb(seq)
                if s > best[0]:
                    best[0], best[1] = s, list(seq)
                if s > -1e-6:
                    near.append(list(seq))
            return
        for d in range(min(maxd, n - 1), -1, -1):
            seq.append(d)
            rec(i + 1, d)
            seq.pop()
        if time.time() - last[0] > report_every:
            last[0] = time.time()
            print(f"  n={n}: {cnt[0]} seqs so far, {time.time()-t0:.0f}s", flush=True)

    rec(0, n - 1)
    worst_exact = None
    viol = []
    exact_zero = []
    for s in near:
        e = score_mp(s)
        if worst_exact is None or e > worst_exact:
            worst_exact = e
        if e > mpf(10) ** -30:
            viol.append((float(e), s))
        elif abs(e) <= mpf(10) ** -30:
            # ties at 60 digits: settle exactly with sympy
            import sympy as sp
            n_ = len(s)
            s1, s2 = sum(s), sum(x * x for x in s)
            dev2 = sp.Rational(s1 + s2, n_) - sp.Rational(s1, n_) ** 2
            pos = sorted(x for x in s if x > 0)
            w = sorted([1 / sp.sqrt(sp.Integer(x)) for x in pos])
            tot = sp.Integer(0)
            for d_u in pos:
                w_u = 1 / sp.sqrt(sp.Integer(d_u))
                ss = sum(w[:d_u])
                if w_u <= w[d_u - 1]:
                    ss = ss - w_u + w[d_u]
                tot += w_u * ss
            diff = sp.simplify(dev2 - (tot / 2) ** 2)
            if sp.simplify(diff) > 0:
                viol.append(("exact>0", s))
            else:
                exact_zero.append(s)
    print(f"n={n}: {cnt[0]} graphical seqs, float max={best[0]:+.3e} at {best[1]}; "
          f"{len(near)} near-zero re-checked at 60 digits, "
          f"max exact score={float(worst_exact) if worst_exact is not None else None}; "
          f"exact-zero seqs: {exact_zero}; "
          f"VIOLATIONS: {viol if viol else 'none'}", flush=True)


if __name__ == "__main__":
    for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        run(n)

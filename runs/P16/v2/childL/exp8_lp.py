"""exp8: LP search for a nonnegative-multiplier certificate of (B).

For heavy edges e (z1_e > rho0(e)) collect Delta = E_e - sum_f E_f (>0
empirically, min 1) and candidate slack features (all >= 0 by construction):

  pi  = z1_e - rho0            (premise slack)
  be  = rho0 - arg44_e
  F1  = sum_{f~e} (rho0 - arg44_f)
  F2  = sum_{f=ik~e} d_k (rho0 - arg44_f)   (outer-endpoint weighted)
  F3  = sum_{f~e} sum_{h~f} (rho0 - arg44_h)   (2-walk weighted 2nd shell)
  F4  = sum_{f~e} (s_f - 2)(rho0 - arg44_f)

LP: max t  s.t.  Delta_i - sum_t c_t F_t,i >= t  for all samples, c >= 0.
If t* > 0, a linear certificate exists on the sample set; inspect c.
"""
import itertools
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

from common import geng, gentreeg, g6_adj, edge_env


def samples():
    gens = itertools.chain(
        itertools.chain.from_iterable(geng(n) for n in range(3, 9)),
        itertools.chain.from_iterable(gentreeg(n) for n in range(3, 15)),
        (l.strip() for l in open("../childE/n10_fails.txt")),
        (l.strip() for l in open("../childH/n9_sumfails.txt")),
    )
    for g6 in gens:
        if not g6:
            continue
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        for a in range(ne):
            if z1[a] <= rho0[a]:
                continue
            r0 = rho0[a]
            nb = [b for b in range(ne) if AL[a, b]]
            Delta = (z1[a] - r0) - sum(z1[b] - r0 for b in nb)
            pi = z1[a] - r0
            be = r0 - a44[a]
            F1 = sum(r0 - a44[b] for b in nb)
            F2 = Fraction(0)
            for b in nb:
                ib, jb = E[b]
                # outer endpoint = the one not shared with e
                ia, ja = E[a]
                outer = ib if ib not in (ia, ja) else jb
                F2 += int(d[outer]) * (r0 - a44[b])
            F3 = sum((r0 - a44[c]) for b in nb for c in range(ne) if AL[b, c])
            F4 = sum((s[b] - 2) * (r0 - a44[b]) for b in nb)
            yield float(Delta), [float(v) for v in (pi, be, F1, F2, F3, F4)], g6, a


def main():
    D = []; F = []; meta = []
    for delta, feats, g6, a in samples():
        D.append(delta); F.append(feats); meta.append((g6, a))
    D = np.array(D); F = np.array(F)
    print("samples:", len(D), "min Delta:", D.min())
    nf = F.shape[1]
    # variables: c (nf), t ; maximize t
    # constraints: F c + t <= D  ; c >= 0, t free
    A_ub = np.hstack([F, np.ones((len(D), 1))])
    b_ub = D
    cobj = np.zeros(nf + 1); cobj[-1] = -1
    bounds = [(0, None)] * nf + [(None, None)]
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
                  method="highs")
    print("status:", res.status, res.message)
    print("t* =", -res.fun if res.success else None)
    if res.success:
        print("c =", dict(zip(["pi", "be", "F1", "F2", "F3", "F4"], res.x[:-1])))
        resid = D - F @ res.x[:-1]
        k = np.argsort(resid)[:10]
        print("tightest residuals:")
        for idx in k:
            print("  ", resid[idx], meta[idx])


if __name__ == "__main__":
    main()

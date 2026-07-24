"""exp7b: vectorized cross-graph conflict search for clause (a) (see exp7).

Float prefilter over all (heavy, light) cross pairs; exact Fraction recheck
of candidates. A 'conflict' = pair of 2-ball configurations from DIFFERENT
graphs whose q_{e,f}(rho) < 0 for some admissible rho
(rho >= max(rho0_e, rho0_f), z1_f <= rho <= z1_e).
Conjecture J asserts such pairs can never occur inside ONE graph; each
conflict is a transplant target for a counterexample attempt.
"""
import itertools, pickle
from fractions import Fraction
import numpy as np

from common import geng, gentreeg, g6_adj, edge_env


def pool_graphs():
    for n in range(3, 9):
        for g in geng(n):
            yield g
    for n in range(3, 18):
        for t in gentreeg(n):
            yield t
    for fn in ("../childE/n10_fails.txt", "../childH/n9_sumfails.txt"):
        for line in open(fn):
            if line.strip():
                yield line.strip()


def main():
    light, heavy = {}, {}
    for g6 in pool_graphs():
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        for a in range(len(E)):
            w = zs[a] - s[a] * z1[a]
            key = (s[a], z1[a], zs[a], rho0[a])
            if w > 0 and key not in light:
                light[key] = (g6, a)
            if z1[a] > rho0[a] and key not in heavy:
                heavy[key] = (g6, a)
    print("light:", len(light), "heavy:", len(heavy), flush=True)
    lk = list(light.keys()); hk = list(heavy.keys())
    Ls = np.array([float(k[0]) for k in lk]); Lz1 = np.array([float(k[1]) for k in lk])
    Lzs = np.array([float(k[2]) for k in lk]); Lr0 = np.array([float(k[3]) for k in lk])
    conflicts = []
    for hi, (se, z1e, zse, r0e) in enumerate(hk):
        sef, z1ef, zsef, r0ef = map(float, (se, z1e, zse, r0e))
        lo = np.maximum(np.maximum(Lr0, r0ef), Lz1)
        hi_ = z1ef
        ok = lo <= hi_
        if not ok.any():
            continue
        # q(r) = (se-sf) r^2 + B r + C ; evaluate min over [lo,hi]
        a2 = sef - Ls
        B = Ls * z1ef + Lzs - sef * Lz1 - zsef
        C = -Lzs * z1ef + zsef * Lz1

        def qv(r):
            return a2 * r * r + B * r + C
        qmin = np.minimum(qv(lo), qv(np.full_like(lo, hi_)))
        with np.errstate(divide="ignore", invalid="ignore"):
            crit = -B / (2 * a2)
        inside = ok & (a2 != 0) & (crit > lo) & (crit < hi_)
        qmin = np.where(inside, np.minimum(qmin, qv(crit)), qmin)
        cand = np.where(ok & (qmin < 1e-6))[0]
        for li in cand:
            sf, z1f, zsf, r0f = lk[li]
            loF = max(r0f, r0e, Fraction(z1f)); hiF = Fraction(z1e)
            if loF > hiF:
                continue

            def q(r):
                return (r * sf - zsf) * (z1e - r) - (r * se - zse) * (z1f - r)
            cands = [loF, hiF]
            aq = se - sf
            Bq = sf * z1e + zsf - se * z1f - zse
            if aq != 0:
                cr = Fraction(-Bq, 2 * aq)
                if loF < cr < hiF:
                    cands.append(cr)
            mn = min(q(r) for r in cands)
            if mn < 0:
                conflicts.append((mn, lk[li], light[lk[li]], hk[hi], heavy[hk[hi]]))
        if hi % 500 == 0:
            print("  heavy", hi, "conflicts so far", len(conflicts), flush=True)
    conflicts.sort(key=lambda t: t[0])
    print("conflicting cross pairs:", len(conflicts))
    for c in conflicts[:25]:
        print("  qmin=%s light=%s %s heavy=%s %s" % (c[0], c[1], c[2], c[3], c[4]))
    with open("exp7_conflicts.pkl", "wb") as f:
        pickle.dump(conflicts, f)


if __name__ == "__main__":
    main()

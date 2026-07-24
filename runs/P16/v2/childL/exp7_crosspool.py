"""exp7: adversarial cross-graph conflict search for Conjecture J clause (a),
with realization attempts.

Phase 1 (pool): for each graph in a pool (trees 3..17, connected n<=8,
childE/childH hard sets), for each edge record the exact tuple
(s, z1, zs, rho0, w) plus (g6, edge index).  Keep:
  - light candidates: w > 0 (else L <= -s <= -3 never beats any U, by (B))
  - heavy candidates: all edges (U candidates need z1_e > rho somewhere,
    i.e. z1_e > rho0_e).

Phase 2 (conflicts): for each cross pair (e heavy from G1, f light from G2),
minimize q_{e,f}(rho) exactly over I = [max(rho0_e, rho0_f, z1_f), z1_e].
Record pairs with min q < 0 (these violate J *if* both 2-balls could
coexist in one graph at that level).

Phase 3 (realization): for each conflicting pair, join G1 and G2 by a path
of length L (6, 8) between vertices farthest from the two binding edges,
recompute exact invariants in the merged graph, and test clauses (a),(b)
for the transplanted pair directly.  Any surviving violation is a
counterexample to Conjecture J.
"""
from fractions import Fraction
import itertools
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
        try:
            for line in open(fn):
                if line.strip():
                    yield line.strip()
        except OSError:
            pass


def qmin_on_interval(sf, z1f, zsf, se, z1e, zse, lo, hi):
    """exact min of q(rho) over [lo,hi] (endpoints + stationary point)."""
    # q = (rho sf - zsf)(z1e - rho) - (rho se - zse)(z1f - rho)
    def q(r):
        return (r * sf - zsf) * (z1e - r) - (r * se - zse) * (z1f - r)
    cands = [lo, hi]
    a = se - sf  # leading coeff of q is (sf*(-1) ... ) compute: q = -sf r^2 + ... + se r^2 => (se - sf) r^2
    # q'(r) = 2(se-sf) r + linear; solve exactly
    # expand: q = (se - sf) r^2 + B r + C
    B = sf * z1e + zsf - se * z1f - zse
    if a != 0:
        crit = Fraction(-B, 2 * a)
        if lo < crit < hi:
            cands.append(crit)
    return min(q(r) for r in cands)


def main():
    pool_light = {}
    pool_heavy = {}
    ngr = 0
    for g6 in pool_graphs():
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ngr += 1
        for a in range(len(E)):
            w = zs[a] - s[a] * z1[a]
            key = (s[a], z1[a], zs[a], rho0[a])
            if w > 0 and key not in pool_light:
                pool_light[key] = (g6, a)
            if z1[a] > rho0[a] and key not in pool_heavy:
                pool_heavy[key] = (g6, a)
    print("pool graphs:", ngr, "light:", len(pool_light),
          "heavy:", len(pool_heavy), flush=True)

    conflicts = []
    for (sf, z1f, zsf, r0f), src_f in pool_light.items():
        for (se, z1e, zse, r0e), src_e in pool_heavy.items():
            lo = max(r0e, r0f, Fraction(z1f))
            hi = Fraction(z1e)
            if lo > hi:
                continue
            mn = qmin_on_interval(sf, z1f, zsf, se, z1e, zse, lo, hi)
            if mn < 0:
                conflicts.append((mn, (sf, z1f, zsf, r0f), src_f,
                                  (se, z1e, zse, r0e), src_e))
    conflicts.sort(key=lambda t: t[0])
    print("cross-graph conflicting pairs:", len(conflicts), flush=True)
    for c in conflicts[:20]:
        print("  qmin=%s f=%s %s e=%s %s" % (c[0], c[1], c[2], c[3], c[4]))
    np.save("exp7_conflicts.npy", np.array(conflicts, dtype=object),
            allow_pickle=True)


if __name__ == "__main__":
    main()

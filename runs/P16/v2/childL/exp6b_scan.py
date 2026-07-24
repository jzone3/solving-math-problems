"""exp6b: fast exact scan of the residual R (see exp6) over graphs.

R = sum_sides [2 N_i m_i + P_i - W_i - 3 m_i x^2 + 2 m_i x + x^3 - 2 x^2]
    - 4 m_i m_j + 4 x y
Scan all edges of all connected graphs n<=8 + trees n<=16; report min and
count of negatives (R >= 0 for heavy-edge 1-balls would prove (B)).
Also scan restricted to heavy edges (z1_e > rho0(e)).
"""
from fractions import Fraction
import itertools
from common import geng, gentreeg, g6_adj, edge_env


def side(xv, mi_, Ni_, Pi_, Wi_):
    return (2 * Ni_ * mi_ + Pi_ - Wi_ - 3 * mi_ * xv * xv + 2 * mi_ * xv
            + xv**3 - 2 * xv * xv)


def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "geng"
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    gens = (itertools.chain.from_iterable(geng(n) for n in range(3, nmax + 1))
            if mode == "geng" else
            itertools.chain.from_iterable(gentreeg(n) for n in range(3, nmax + 1)))
    minall = None; negall = 0
    minheavy = None; negheavy = 0
    tot = 0
    for g6 in gens:
        A = g6_adj(g6)
        n = A.shape[0]
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        dv = A.sum(1)
        P = [sum(Fraction(int(dv[k]) ** 2) for k in range(n) if A[i, k]) for i in range(n)]
        W = [sum(Fraction(int(dv[k])) * m[k] for k in range(n) if A[i, k]) for i in range(n)]
        N = [sum(m[k] for k in range(n) if A[i, k]) for i in range(n)]
        for a, (i, j) in enumerate(E):
            xv, yv = int(dv[i]), int(dv[j])
            R = (side(xv, m[i], N[i], P[i], W[i])
                 + side(yv, m[j], N[j], P[j], W[j])
                 - 4 * m[i] * m[j] + 4 * xv * yv)
            tot += 1
            if minall is None or R < minall[0]:
                minall = (R, g6, (i, j))
            if R < 0:
                negall += 1
            if z1[a] > rho0[a]:
                if minheavy is None or R < minheavy[0]:
                    minheavy = (R, g6, (i, j))
                if R < 0:
                    negheavy += 1
    print("edges:", tot)
    print("all edges: min R =", minall, "neg:", negall)
    print("heavy edges: min R =", minheavy, "neg:", negheavy)


if __name__ == "__main__":
    main()

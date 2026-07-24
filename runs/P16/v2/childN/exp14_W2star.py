"""childN exp14: abstract 2-shell W2* test (tree-like), exact Fractions.

At rho = z1 (the (W=) point), per i-side neighbor k of degree t, maximize
S = sum of k's other-neighbor degrees (so m_k=(x+S)/t), subject to:
  (C1) 2((x-1)^2+(t-1)^2+m_i m_k - x t) <= rho
  (C2) every entry c of the multiset (t-1 entries, integers >=1) satisfies
       psi_m(c) = 2((t-1)^2+(c-1)^2+m_k (t+c-1)/c - t c) <= rho
       [relaxation m_u >= (t+c-1)/c; pendant c=1 exact]
  feasible multiset exists <=> (t-1)*c1(m) <= S <= (t-1)*c2(m) where
  [c1,c2] = contiguous feasible integer range (psi convex in c).
Pendant t=1: m_k = x, require arg44_ik <= rho.
Claim W2*: w_max <= 0 over all configs with arg44_e <= z1.
"""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

def feas_range(t, m, rho):
    """integer c range with psi_m(c) <= rho; returns (c1,c2) or None."""
    def psi(c):
        return 2 * ((t - 1) ** 2 + (c - 1) ** 2) + 2 * m * Fraction(t + c - 1, c) - 2 * t * c
    # find any feasible c by scanning up to bound
    cmax_bound = int(float(rho) ** 0.5) + 2 * t + 4
    lo = None
    for c in range(1, cmax_bound + 1):
        if psi(c) <= rho:
            lo = c
            break
    if lo is None:
        return None
    hi = lo
    c = lo
    while c <= cmax_bound:
        c += 1
        if psi(c) <= rho:
            hi = c
        else:
            break
    return lo, hi

def side_max_S(t, X, mX, rho):
    """max S for a neighbor of degree t on side with endpoint degree X and
    avg-neighbor-degree mX; None if infeasible."""
    if t == 1:
        if 2 * ((X - 1) ** 2 + mX * X - X) <= rho:
            return 0
        return None
    capC1 = (Fraction(rho, 1) / 2 - (X - 1) ** 2 - (t - 1) ** 2 + X * t) / mX
    S1 = (capC1 * t).__floor__() - X  # S <= S1
    best = None
    S = S1
    while S >= t - 1:
        m = Fraction(X + S, t)
        r = feas_range(t, m, rho)
        if r is not None and (t - 1) * r[0] <= S <= (t - 1) * r[1]:
            best = S
            break
        S -= 1
    return best

def main(xmax, dmax):
    bad = []
    tot = 0
    wmax = None
    for x in range(1, xmax + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, dmax + 1), x - 1):
                mi = Fraction(y + sum(dk), x)
                for dl in cwr(range(1, dmax + 1), y - 1):
                    mj = Fraction(x + sum(dl), y)
                    s = x + y
                    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
                    if 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y) > z1:
                        continue
                    rho = z1
                    w = y * (mj - y) + x * (mi - x)
                    ok = True
                    for (ds, X, Y, mX) in ((dk, x, y, mi), (dl, y, x, mj)):
                        for t in ds:
                            S = side_max_S(t, X, mX, rho)
                            if S is None:
                                ok = False
                                break
                            mk = Fraction(X + S, t)
                            w += (t - Y) * (t + Y - 4) + t * (mk - Y)
                        if not ok:
                            break
                    if not ok:
                        continue
                    tot += 1
                    if wmax is None or w > wmax[0]:
                        wmax = (w, x, y, dk, dl)
                    if w > 0:
                        bad.append((x, y, dk, dl, w))
            print(f"x={x} y={y} bad={len(bad)} wmax={wmax}", flush=True)
    print("TOTAL bad:", len(bad), "of", tot)
    for b in bad[:100]:
        print(b)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6,
         int(sys.argv[2]) if len(sys.argv) > 2 else 10)

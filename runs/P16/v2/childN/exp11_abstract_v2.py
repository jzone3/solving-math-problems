"""childN exp11: abstract 2-shell (tree-like) relaxation of (B).

Config: x,y, dk (x-1 degrees), dl (y-1 degrees).  m_i=(y+sum dk)/x,
m_j=(x+sum dl)/y, z1=(s-2)^2+x m_i+y m_j-2xy, arg44_e as usual.
For neighbor k (degree t=d_k, on i-side), the second shell of k is a
(t-1)-multiset of degrees c (>=1), giving m_k=(x+sum c)/t.  Constraints at
level rho:
  (C1) arg44_ik = 2((x-1)^2+(t-1)^2+m_i m_k - x t) <= rho
  (C2) for each c in the multiset: 2((t-1)^2+(c-1)^2+m_k*(t+c-1)/c - t c) <= rho
       [valid relaxation: m_u >= (t+c-1)/c]
Special: t=1 => m_k = x exactly (k pendant, its only neighbor is i).
w = sum_k (t-y)(t+y-4) + y(m_j-y)+ sum_k t(m_k - y)
    + sum_l (u-x)(u+x-4) + x(m_i-x) + sum_l u(m_l - x)
D(rho) = -w - (s-3)(z1-rho).   (B) abstract: D(rho)>0 for all admissible
rho in [max(arg44 constraints active), z1).

For each config and each rho on a grid, maximize w by choosing for each k
the c-multiset maximizing sum c subject to (C1),(C2) at that rho
(exhaustive over equal-ish multisets: search best c-multiset greedily:
try all c-multisets with entries in 1..CMAX for t-1<=3, else equal-c +
perturbation).  Report min D over grid; flag <=0.
"""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

CMAX = 60

def max_mk(t, x, mi, rho):
    """max feasible m_k for neighbor of degree t on i-side (exact Fractions),
    returns Fraction or None if even minimal config violates.
    Also enforces (C1)."""
    if t == 1:
        mk = Fraction(x)
        c1 = 2 * ((x - 1) ** 2 + 0 + mi * mk - x)
        return mk if c1 <= rho else None
    best = None
    # search c-multisets: all entries equal c0 with optional mixture two values
    # exhaustive for t-1 <= 3, else two-value patterns
    def ok(cs):
        mk = Fraction(x + sum(cs), t)
        c1 = 2 * ((x - 1) ** 2 + (t - 1) ** 2 + mi * mk - x * t)
        if c1 > rho:
            return None
        for c in set(cs):
            c2 = 2 * ((t - 1) ** 2 + (c - 1) ** 2 + mk * Fraction(t + c - 1, c) - t * c)
            if c2 > rho:
                return None
        return mk
    if t - 1 <= 3:
        for cs in cwr(range(1, CMAX + 1), t - 1):
            mk = ok(cs)
            if mk is not None and (best is None or mk > best):
                best = mk
    else:
        for c0 in range(1, CMAX + 1):
            for c1v in range(c0, CMAX + 1):
                for splits in range(t):  # splits entries at c1v, rest c0
                    cs = [c1v] * splits + [c0] * (t - 1 - splits)
                    mk = ok(cs)
                    if mk is not None and (best is None or mk > best):
                        best = mk
    return best

def check_config(x, y, dk, dl, rho_grid=24):
    mi = Fraction(y + sum(dk), x)
    mj = Fraction(x + sum(dl), y)
    s = x + y
    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
    a44e = 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y)
    if a44e >= z1:
        return None
    worst = None
    for gi in range(rho_grid):
        rho = a44e + (z1 - a44e) * Fraction(gi, rho_grid)  # in [a44e, z1)
        wtot = x * (mi - x) + y * (mj - y)
        feas = True
        for t in dk:
            mk = max_mk(t, x, mi, rho)
            if mk is None:
                feas = False
                break
            wtot += (t - y) * (t + y - 4) + t * (mk - y)
        if feas:
            for u in dl:
                ml = max_mk(u, y, mj, rho)
                if ml is None:
                    feas = False
                    break
                wtot += (u - x) * (u + x - 4) + u * (ml - x)
        if not feas:
            continue
        # w also includes k=j and l=i terms: y(m_j-y) + x(m_i-x)?? already added
        D = -wtot - (s - 3) * (z1 - rho)
        if worst is None or D < worst[0]:
            worst = (D, rho)
    return worst

def main(xmax=4, dmax=6):
    bad = []
    for x in range(1, xmax + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, dmax + 1), x - 1):
                for dl in cwr(range(1, dmax + 1), y - 1):
                    r = check_config(x, y, dk, dl)
                    if r is not None and r[0] <= 0:
                        bad.append((x, y, dk, dl, float(r[0]), float(r[1])))
            print(f"x={x} y={y} done bad={len(bad)}", flush=True)
    print("TOTAL bad:", len(bad))
    for b in bad[:100]:
        print(b)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4,
         int(sys.argv[2]) if len(sys.argv) > 2 else 6)

"""Fast float version of exp11: abstract 2-shell relaxation of (B), with the
second shell relaxed to all-equal REAL c >= 1 (a superset of integer multisets
when maximizing m_k, since w is increasing in each m_k and the feasible-m_k
region is the union over multisets; equal-real-c is checked to dominate via
convexity of the constraint in c... we additionally take max over c on a fine
grid INCLUDING the best of mixed patterns being dominated -- treated as a
heuristic relaxation here; exact confirmation later).

max_mk(t,x,mi,rho): max over real c>=1 of m(c)=(x+(t-1)c)/t subject to
  (C1) 2((x-1)^2+(t-1)^2) + 2 mi m(c) - 2xt <= rho
  (C2) 2((t-1)^2+(c-1)^2) + 2 m(c)(t+c-1)/c - 2tc <= rho
m increasing in c, so binary search the largest feasible c (C2 eventually
violated as c grows since (c-1)^2 dominates... note 2m(c)(t+c-1)/c ~ 2(t-1)c
and -2tc: net (c-1)^2 growth => yes violated for large c).  Then cap by (C1).
"""
import sys
from itertools import combinations_with_replacement as cwr

def max_mk(t, x, mi, rho):
    if t == 1:
        mk = float(x)
        return mk if 2 * ((x - 1) ** 2 + mi * mk - x) <= rho + 1e-12 else None
    def c2(c):
        m = (x + (t - 1) * c) / t
        return 2 * ((t - 1) ** 2 + (c - 1) ** 2) + 2 * m * (t + c - 1) / c - 2 * t * c
    if c2(1.0) > rho + 1e-12:
        # even c=1 infeasible? then try... c small: no feasible second shell
        return None
    lo, hi = 1.0, 1.0
    while c2(hi) <= rho and hi < 1e7:
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if c2(mid) <= rho:
            lo = mid
        else:
            hi = mid
    cbest = lo
    mk = (x + (t - 1) * cbest) / t
    # cap with C1
    m_c1 = (rho / 2 - (x - 1) ** 2 - (t - 1) ** 2 + x * t) / mi if mi > 0 else None
    if m_c1 is None or m_c1 < (x + (t - 1) * 1.0) / t - 1e-12:
        # C1 infeasible even at minimal m_k => neighbor impossible
        if m_c1 is not None and m_c1 < (x + (t - 1)) / t - 1e-9:
            return None
    mk = min(mk, m_c1)
    if mk < (x + (t - 1)) / t - 1e-9:
        return None
    return mk

def check_config(x, y, dk, dl, grid=32):
    mi = (y + sum(dk)) / x
    mj = (x + sum(dl)) / y
    s = x + y
    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
    a44e = 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y)
    if a44e >= z1 - 1e-12:
        return None
    worst = None
    for gi in range(grid):
        rho = a44e + (z1 - a44e) * gi / grid
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
        D = -wtot - (s - 3) * (z1 - rho)
        if worst is None or D < worst[0]:
            worst = (D, rho)
    return worst

def main(xmax, dmax):
    bad = []
    tot = 0
    minD = None
    for x in range(1, xmax + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, dmax + 1), x - 1):
                for dl in cwr(range(1, dmax + 1), y - 1):
                    r = check_config(x, y, dk, dl)
                    if r is None:
                        continue
                    tot += 1
                    if minD is None or r[0] < minD[0]:
                        minD = (r[0], x, y, dk, dl, r[1])
                    if r[0] <= 1e-9:
                        bad.append((x, y, dk, dl, r[0], r[1]))
            print(f"x={x} y={y} bad={len(bad)} minD={minD}", flush=True)
    print("TOTAL bad:", len(bad), "of", tot)
    for b in bad[:200]:
        print(b)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5,
         int(sys.argv[2]) if len(sys.argv) > 2 else 8)

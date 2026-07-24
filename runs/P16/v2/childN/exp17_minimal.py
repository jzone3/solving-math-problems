"""childN exp17: minimal tree counterexample search for (B), and (W=) probe.

Tree family: e=ij, x=deg(i), y=deg(j); first-shell branch degrees dk (x-1),
dl (y-1); each branch vertex k of degree t has t-1 children with integer
degrees c>=1; each child of degree c gets c-1 leaf children (m_u=(t+c-1)/c).
2-ball arg44 list: e, ik/jl edges, ku/lu edges.  Heavy iff all < z1 (then
rho0<z1);  (B) violated iff w >= 0 ... indeed D = (s-3)(rho0-z1) - w < 0
whenever w >= 0 > (s-3)(rho0-z1). Also record equality cases for (W=):
need max arg44 == z1 exactly and w > 0.

Enumerate x,y<=XM, t<=TM, per-branch feasible (sumc -> min vertices) sets,
combine choosing per-branch sumc from its feasible set to reach w>=0 with
min total vertices.
"""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr
from functools import lru_cache

XM, TM, CM = 6, 9, 12

def branch_options(t, X, mX, z1, strict=True):
    """Return dict sumc -> True for feasible c-multisets of a degree-t branch
    on side with endpoint degree X, endpoint avg mX; all arg44 in branch < z1
    (<= if not strict).  Also C1 (edge X-t) must pass."""
    def lt(a, b):
        return a < b if strict else a <= b
    opts = set()
    if t == 1:
        mk = Fraction(X)
        if lt(2 * ((X - 1) ** 2 + mX * mk - X), z1):
            opts.add(0)
        return opts
    for cs in cwr(range(1, CM + 1), t - 1):
        S = sum(cs)
        mk = Fraction(X + S, t)
        if not lt(2 * ((X - 1) ** 2 + (t - 1) ** 2 + mX * mk - X * t), z1):
            continue
        ok = True
        for c in set(cs):
            mu = Fraction(t + c - 1, c)
            if not lt(2 * ((t - 1) ** 2 + (c - 1) ** 2 + mk * mu - t * c), z1):
                ok = False
                break
        if ok:
            opts.add(S)
    return opts

def main():
    best = None
    eq_found = []
    for x in range(2, XM + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, TM + 1), x - 1):
                mi = Fraction(y + sum(dk), x)
                for dl in cwr(range(1, TM + 1), y - 1):
                    mj = Fraction(x + sum(dl), y)
                    s = x + y
                    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
                    if 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y) >= z1:
                        continue
                    # w = base + total_sumc  where base uses m_k=(X+S)/t:
                    # sum_k [(t-y)(t+y-4) + t((X+S)/t - y)] = (t-y)(t+y-4)+X+S-ty
                    base = y * (mj - y) + x * (mi - x)
                    for t in dk:
                        base += (t - y) * (t + y - 4) + x - t * y
                    for u in dl:
                        base += (u - x) * (u + x - 4) + y - u * x
                    need = -base  # need total_sumc >= need for w >= 0
                    # per-branch options
                    okall = True
                    branch = []
                    for t in dk:
                        o = branch_options(t, x, mi, z1)
                        if not o:
                            okall = False
                            break
                        branch.append((t, o))
                    if okall:
                        for u in dl:
                            o = branch_options(u, y, mj, z1)
                            if not o:
                                okall = False
                                break
                            branch.append((u, o))
                    if not okall:
                        continue
                    maxtot = sum(max(o) for _, o in branch)
                    if maxtot < need:
                        continue
                    # minimize total sumc >= need with per-branch min
                    mintot = sum(min(o) for _, o in branch)
                    # greedy: it's enough to know minimal achievable total >= need;
                    # options sets are dense enough: compute via DP
                    tot_opts = {0}
                    for _, o in branch:
                        tot_opts = {a + b for a in tot_opts for b in o}
                    feas_tots = [T for T in tot_opts if T >= need]
                    if not feas_tots:
                        continue
                    Tbest = min(feas_tots)
                    # vertex count
                    N = 2 + (x - 1) + (y - 1) + sum(t - 1 for t, _ in branch) \
                        + (Tbest - sum(t - 1 for t, _ in branch))  # sum(c-1) = T - #children
                    # careful: leaves count = sum over children (c-1) = T - nchildren
                    w = base + Tbest
                    if best is None or N < best[0]:
                        best = (N, x, y, dk, dl, Tbest, w, float(z1))
                        print("new best:", best, flush=True)
    print("BEST:", best)

if __name__ == "__main__":
    main()

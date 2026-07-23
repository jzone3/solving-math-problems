"""childH exp6: EXACT (Fraction) recheck of ord2-sum feasibility on the hard
graphs (childE 190 + 8 n<=9 sum-failures). No floats anywhere."""
from fractions import Fraction
import sys

from common import g6_adj


def exact_feasible(g6):
    A = g6_adj(g6)
    n = A.shape[0]
    adj = [[j for j in range(n) if A[i, j]] for i in range(n)]
    d = [Fraction(len(adj[i])) for i in range(n)]
    m = [sum(d[k] for k in adj[i]) / d[i] for i in range(n)]
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    R = max(2 * ((d[i] - 1) ** 2 + (d[j] - 1) ** 2 + m[i] * m[j] - d[i] * d[j])
            for i, j in E)
    if R < 0:
        return False
    idx = {e: a for a, e in enumerate(E)}
    nbrs = [[] for _ in E]
    for a, (i, j) in enumerate(E):
        for k in adj[i]:
            if k != j:
                nbrs[a].append(idx[(min(i, k), max(i, k))])
        for l in adj[j]:
            if l != i:
                nbrs[a].append(idx[(min(j, l), max(j, l))])
    s = [d[i] + d[j] for i, j in E]
    one = [Fraction(1)] * len(E)

    def AL(x):
        return [sum(x[b] for b in nbrs[a]) for a in range(len(E))]

    zs, z1 = AL(AL(s)), AL(AL(one))
    lo, hi, lo_strict = -min(s), None, True  # c > -min s (strict)
    for a in range(len(E)):
        coef = z1[a] - R
        rhs = R * s[a] - zs[a]
        if coef > 0:
            u = rhs / coef
            if hi is None or u < hi:
                hi = u
        elif coef < 0:
            l = rhs / coef
            if l > lo or (l == lo and lo_strict):
                lo, lo_strict = l, False
        elif rhs < 0:
            return False
    if hi is None:
        return True
    return (lo < hi) or (lo == hi and not lo_strict)


if __name__ == "__main__":
    bad = 0
    for path in sys.argv[1:]:
        gs = [l.strip() for l in open(path) if l.strip()]
        f = [g for g in gs if not exact_feasible(g)]
        bad += len(f)
        print(f"{path}: {len(gs)} graphs, exact ord2-sum infeasible: {len(f)} {f[:10]}")
    print("EXACT RECHECK", "FAILED" if bad else "PASSED")

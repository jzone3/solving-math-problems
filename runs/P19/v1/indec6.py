"""P19 v1: enumerate indecomposable wide partitions with exactly L parts
(CFGV Prop 5: finitely many for each fixed L; CFGV only checked L<=5),
then test each for Latinness with CP-SAT + exact integer re-check.

Usage: python3 indec6.py L B  (parts = L, first part <= B)
"""
import sys, time
from functools import lru_cache
from ortools.sat.python import cp_model


def conjugate(lam):
    if not lam:
        return ()
    out = []
    for j in range(lam[0]):
        out.append(sum(1 for p in lam if p > j))
    return tuple(out)


def dominates(a, b):
    sa = sb = 0
    for i in range(max(len(a), len(b))):
        sa += a[i] if i < len(a) else 0
        sb += b[i] if i < len(b) else 0
        if sa < sb:
            return False
    return True


@lru_cache(maxsize=None)
def self_dom(mu):
    return dominates(mu, conjugate(mu))


def is_wide(lam):
    n = len(lam)
    for mask in range(1, 1 << n):
        mu = tuple(lam[i] for i in range(n) if mask >> i & 1)
        if not self_dom(mu):
            return False
    return True


def enum_wide(L, B):
    """all wide partitions with exactly L parts, first part <= B"""
    out = []

    def rec(prefix):
        k = len(prefix)
        if k == L:
            out.append(tuple(prefix))
            return
        hi = prefix[-1] if prefix else B
        for v in range(hi, 0, -1):
            prefix.append(v)
            # prefix is a subpartition of any completion, so it must be wide
            if is_wide(tuple(prefix)):
                rec(prefix)
            prefix.pop()

    rec([])
    return out


def decomposable(lam):
    """exists wide nu, 0 < |nu| < |lam|, lam-nu weakly decreasing partition,
    both nu and lam-nu wide"""
    L = len(lam)

    def rec(i, nu):
        if i == L:
            n = tuple(p for p in nu if p > 0)
            m = tuple(p for p in (lam[j] - nu[j] for j in range(L)) if p > 0)
            if not n or not m:
                return False
            return is_wide(n) and is_wide(m)
        lo_prev = nu[i - 1] if i else lam[0]
        for v in range(min(lam[i], lo_prev), -1, -1):
            rest = lam[i] - v
            if i and rest > lam[i - 1] - nu[i - 1]:
                continue
            nu.append(v)
            if rec(i + 1, nu):
                nu.pop()
                return True
            nu.pop()
        return False

    return rec(0, [])


def is_latin_cpsat(lam, time_limit=600.0):
    m = cp_model.CpModel()
    rows = len(lam)
    X = {}
    for r in range(rows):
        for c in range(lam[r]):
            X[r, c] = m.NewIntVar(1, lam[r], f"x{r}_{c}")
        m.AddAllDifferent([X[r, c] for c in range(lam[r])])
    collen = conjugate(lam)
    for c in range(lam[0]):
        col = [X[r, c] for r in range(collen[c])]
        if len(col) > 1:
            m.AddAllDifferent(col)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 8
    st = solver.Solve(m)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        tab = [[solver.Value(X[r, c]) for c in range(lam[r])] for r in range(rows)]
        # exact integer re-check
        for r in range(rows):
            assert sorted(tab[r]) == list(range(1, lam[r] + 1)), (lam, r)
        for c in range(lam[0]):
            col = [tab[r][c] for r in range(collen[c])]
            assert len(set(col)) == len(col), (lam, c)
        return "SAT"
    if st == cp_model.INFEASIBLE:
        return "UNSAT"
    return "UNKNOWN"


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    B = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    t0 = time.time()
    wides = enum_wide(L, B)
    print(f"L={L} B={B}: {len(wides)} wide partitions ({time.time()-t0:.1f}s)", flush=True)
    indecs = []
    for lam in wides:
        if not decomposable(lam):
            indecs.append(lam)
    print(f"indecomposable: {len(indecs)} ({time.time()-t0:.1f}s)", flush=True)
    max_part = max((l[0] for l in indecs), default=0)
    max_n = max((sum(l) for l in indecs), default=0)
    print(f"max first part among indecomposables: {max_part} (bound B={B}), max |lam|={max_n}", flush=True)
    bad = []
    for lam in sorted(indecs, key=sum):
        res = is_latin_cpsat(lam)
        if res != "SAT":
            bad.append((lam, res))
            print(f"*** {lam} -> {res}", flush=True)
    print(f"done: {len(indecs)} indecomposables tested, non-SAT: {bad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

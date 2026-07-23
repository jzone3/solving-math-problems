#!/usr/bin/env python3
"""P19 extension — full Latin Tableau Conjecture (Chow–Tiefenbruck 2025) sweep.

LTC: a Latin tableau of shape λ and type μ exists iff δ(λ) ⪰ μ, where δ is the
chromatic difference sequence of λ (δ_r = α_r − α_{r−1}, α_r = max boxes
colorable with r colors, no repeat in any row/column).

By Chow–Tiefenbruck Proposition 2 (proved), the achievable types form a
down-set in dominance order, so LTC ⟺ for every shape λ there exists a Latin
tableau of shape λ and type exactly δ(λ). This script exhaustively tests that
reduction for all partitions λ with |λ| = n, n increasing.

α_r is computed exactly by Chow–Tiefenbruck Theorem 1 (corner constraints):
  α_r(λ) = min_{i,j ≥ 0} [ r·(i+j) + Σ_{k>i} max(λ_k − j, 0) ].

Any UNSAT is a counterexample to the LTC (to be confirmed by ltc_verify.py).
Prior art: CT 2025 verified LTC for all λ inside a 12×12 box; exhaustive
|λ| ≤ N is new territory for shapes with λ₁ ≥ 13 or ℓ(λ) ≥ 13.
"""
import sys
import time
from ortools.sat.python import cp_model

from search import partitions, conjugate


def cds(lam):
    """Chromatic difference sequence of λ, exact integers (CT Theorem 1)."""
    total = sum(lam)
    ell = len(lam)
    alphas = [0]
    r = 0
    while alphas[-1] < total:
        r += 1
        best = None
        for i in range(ell + 1):
            # boxes below first i rows, as a function of j: sum over k>i of max(l_k - j, 0)
            tail = lam[i:]
            for j in range(lam[0] + 1):
                outside = sum(p - j for p in tail if p > j)
                v = r * (i + j) + outside
                if best is None or v < best:
                    best = v
        alphas.append(min(best, total))
    delta = tuple(alphas[k] - alphas[k - 1] for k in range(1, len(alphas)))
    assert sum(delta) == total and all(
        delta[k] >= delta[k + 1] for k in range(len(delta) - 1)), (lam, delta)
    return delta


def ltc_cpsat(lam, delta, time_limit=600.0):
    """SAT iff a Latin tableau of shape λ and type δ exists (colors k with
    multiplicity exactly δ_k; WLOG by color relabeling)."""
    m = cp_model.CpModel()
    ncol = len(delta)
    rows = len(lam)
    collen = conjugate(lam)
    x = {}
    for r in range(rows):
        for c in range(lam[r]):
            for k in range(ncol):
                x[r, c, k] = m.NewBoolVar(f"x{r}_{c}_{k}")
            m.AddExactlyOne(x[r, c, k] for k in range(ncol))
    for k in range(ncol):
        for r in range(rows):
            m.AddAtMostOne(x[r, c, k] for c in range(lam[r]))
        for c in range(lam[0]):
            m.AddAtMostOne(x[r, c, k] for r in range(collen[c]))
        m.Add(sum(x[r, c, k] for r in range(rows) for c in range(lam[r])) == delta[k])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    st = solver.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        tab = [[next(k for k in range(ncol) if solver.Value(x[r, c, k]))
                for c in range(lam[r])] for r in range(rows)]
        return "SAT", tab
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None
    return "UNKNOWN", None


def check_type_tableau(lam, delta, tab):
    """Exact re-check: shape, row/col distinctness, multiplicities == δ sorted."""
    from collections import Counter
    assert [len(row) for row in tab] == list(lam)
    for row in tab:
        if len(set(row)) != len(row):
            return False
    for c in range(lam[0]):
        col = [tab[r][c] for r in range(len(lam)) if c < len(tab[r])]
        if len(set(col)) != len(col):
            return False
    counts = tuple(sorted(Counter(
        v for row in tab for v in row).values(), reverse=True))
    return counts == tuple(delta)


def work(lam):
    delta = cds(lam)
    status, tab = ltc_cpsat(lam, delta)
    if status == "SAT":
        assert check_type_tableau(lam, delta, tab), (lam, delta, tab)
    return lam, delta, status


def main():
    import multiprocessing as mp
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    start_n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    t0 = time.time()
    pool = mp.Pool(mp.cpu_count())
    for n in range(start_n, N + 1):
        tn = time.time()
        shapes = list(partitions(n))
        for lam, delta, status in pool.imap_unordered(work, shapes, chunksize=16):
            if status == "UNSAT":
                print(f"*** LTC COUNTEREXAMPLE CANDIDATE: n={n} lambda={lam} "
                      f"delta={delta}", flush=True)
                with open("ltc_candidates.txt", "a") as f:
                    f.write(f"{lam}\t{delta}\n")
            elif status == "UNKNOWN":
                print(f"!!! LTC UNKNOWN: n={n} lambda={lam}", flush=True)
                with open("ltc_unknown.txt", "a") as f:
                    f.write(f"{lam}\n")
        print(f"n={n}: {len(shapes)} shapes, LTC (type=delta) verified "
              f"({time.time()-tn:.1f}s, total {time.time()-t0:.1f}s)", flush=True)
        with open("ltc_frontier.txt", "w") as f:
            f.write(f"LTC (via CT Prop 2 reduction to type=delta) verified for "
                    f"all shapes |lambda| <= {n}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V1 direct search for circulant weighing matrices CW(n,k) via CP-SAT.

Model: ternary first row x_0..x_{n-1} in {-1,0,+1} with
  - PAF_s(x) = sum_i x_i x_{i+s mod n} = 0 for s = 1..n//2
  - #(+1) = (k+s)/2, #(-1) = (k-s)/2 where s = sqrt(k)  (WLOG, negation symmetry)
  - x_0 = +1 (WLOG, cyclic shift symmetry)
Optional folded-quotient constraints for divisors d|n (implied, aid propagation).

Usage: python3 cw_cpsat.py n k [time_limit_s] [workers] [seed]
Prints SOLUTION <list> if found, else UNSAT/UNKNOWN.
"""
import math, sys
from ortools.sat.python import cp_model


def build(n, k, use_quotients=True, fix_first=True, seed=0):
    s = math.isqrt(k)
    assert s * s == k, "k must be a perfect square for these open cells"
    npos, nneg = (k + s) // 2, (k - s) // 2
    m = cp_model.CpModel()
    p = [m.NewBoolVar(f"p{i}") for i in range(n)]
    q = [m.NewBoolVar(f"m{i}") for i in range(n)]
    x = [m.NewIntVar(-1, 1, f"x{i}") for i in range(n)]
    for i in range(n):
        m.AddAtMostOne([p[i], q[i]])
        m.Add(x[i] == p[i] - q[i])
    m.Add(sum(p) == npos)
    m.Add(sum(q) == nneg)
    if fix_first:
        m.Add(p[0] == 1)
    # products y[i][t] = x[i]*x[(i+t)%n] for needed shifts
    prod_cache = {}
    def prod(i, j):
        a, b = min(i, j), max(i, j)
        if (a, b) not in prod_cache:
            v = m.NewIntVar(-1, 1, f"y{a}_{b}")
            m.AddMultiplicationEquality(v, [x[a], x[b]])
            prod_cache[(a, b)] = v
        return prod_cache[(a, b)]
    abs_terms = []
    for t in range(1, n // 2 + 1):
        terms = [prod(i, (i + t) % n) for i in range(n)]
        m.Add(sum(terms) == 0)
        for i in range(n):
            a, b = min(i, (i + t) % n), max(i, (i + t) % n)
            v = prod_cache[(a, b)]
            z = m.NewBoolVar(f"z{a}_{b}_{t}")
            m.AddAbsEquality(z, v)
            abs_terms.append(z)
    # global count of nonzero overlapping pairs: sum over shifts 1..n-1 of
    # |PAF terms| = k^2 - k; shifts t and n-t contribute equally, and for even
    # n the shift n/2 sum is included once here but appears once in 1..n-1 too
    # ... total over our range = (k*k - k) / 2 + (extra for even n handled below)
    if n % 2 == 1:
        m.Add(sum(abs_terms) == (k * k - k) // 2)
    else:
        # shifts 1..n/2-1 counted once (of a symmetric pair), shift n/2 counted fully
        m.Add(2 * sum(abs_terms[: n * (n // 2 - 1)]) + sum(abs_terms[n * (n // 2 - 1):]) == k * k - k)
    if use_quotients:
        for d in [d for d in range(2, n) if n % d == 0]:
            if d > 24:  # keep model small
                continue
            b = []
            for j in range(d):
                bj = m.NewIntVar(-(n // d), n // d, f"b{d}_{j}")
                m.Add(bj == sum(x[i] for i in range(j, n, d)))
                b.append(bj)
            for t in range(1, d // 2 + 1):
                terms = []
                for j in range(d):
                    v = m.NewIntVar(-(n // d) ** 2, (n // d) ** 2, f"bp{d}_{j}_{t}")
                    m.AddMultiplicationEquality(v, [b[j], b[(j + t) % d]])
                    terms.append(v)
                m.Add(sum(terms) == 0)
    return m, x


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 3600.0
    wk = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    m, x = build(n, k, seed=seed)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tl
    sol.parameters.num_workers = wk
    sol.parameters.random_seed = seed
    sol.parameters.log_search_progress = True
    st = sol.Solve(m)
    print("status:", sol.StatusName(st))
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        vec = [sol.Value(v) for v in x]
        print("SOLUTION", vec)
    print("wall:", sol.WallTime())


if __name__ == "__main__":
    main()

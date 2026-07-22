"""Inner oracles for P02 (Brandt regular supergraph), V4 run.

Key reduction (machine-cross-checked in test_oracle.py against ILP over d):
  G has a regular triangle-free supergraph by vertex multiplications
  <=> exists integer x_v >= 1 with sum_{u in N(v)} x_u = d (const) for all v
  <=> exists RATIONAL x_v >= 1 with A x = c*1 for some c   [scale by common denom]
  <=> LP feasibility, exactly decidable in rational arithmetic.

Farkas certificate of infeasibility: y in Q^n with
  1^T y = 0,  (A y)_v >= 0 for all v,  1^T A y > 0.
Then for any x >= 1: y^T A x >= 1^T A y > 0 but y^T (c 1) = 0, contradiction.

Second oracle LP2: does the (twin-free) graph H admit ANY blowup G with
  delta(G) >= n(G)/3 ?  <=> exists rational w_v >= 1 with
  3 * sum_{u in N(v)} w_u >= sum_u w_u  for all v.
(rational -> integer by scaling since constraints homogeneous + w>=1 scalable)
"""

from fractions import Fraction


def neighborhoods(n, edges):
    N = [set() for _ in range(n)]
    for a, b in edges:
        N[a].add(b)
        N[b].add(a)
    return N


def is_triangle_free(n, edges):
    N = neighborhoods(n, edges)
    return all(not (N[a] & N[b]) for a, b in edges)


def is_maximal_tf(n, edges):
    N = neighborhoods(n, edges)
    es = {frozenset(e) for e in edges}
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in es and not (N[u] & N[v]):
                return False
    return True


def is_twin_free(n, edges):
    N = neighborhoods(n, edges)
    for u in range(n):
        for v in range(u + 1, n):
            if N[u] == N[v]:
                return False
    return True


# ---------- exact rational simplex (Phase I feasibility) ----------
# Solve: does {z : M z = b, z >= 0} have a solution?  (standard form)
# Big-M free implementation via artificial variables, Bland's rule.

def _simplex_feasible(M, b):
    """M: list of rows (Fraction), b: list of Fraction. Returns (feasible, z or farkas_y).

    If feasible: (True, z) with M z = b, z >= 0.
    If infeasible: (False, y) with y^T M <= 0 componentwise and y^T b > 0.
    """
    m = len(M)
    nv = len(M[0]) if m else 0
    # make b >= 0
    M = [row[:] for row in M]
    b = b[:]
    sign = [1] * m
    for i in range(m):
        if b[i] < 0:
            M[i] = [-x for x in M[i]]
            b[i] = -b[i]
            sign[i] = -1
    # tableau with artificials; track basis
    # columns: nv original + m artificial
    T = [M[i] + [Fraction(1) if j == i else Fraction(0) for j in range(m)] + [b[i]]
         for i in range(m)]
    basis = [nv + i for i in range(m)]
    # objective: minimize sum of artificials -> row of reduced costs
    cost = [Fraction(0)] * (nv + m) + [Fraction(0)]
    for j in range(nv, nv + m):
        cost[j] = Fraction(1)
    # canonical form: subtract basic rows
    obj = [Fraction(0)] * (nv + m + 1)
    for j in range(nv + m + 1):
        obj[j] = cost[j] if j < nv + m else Fraction(0)
    for i in range(m):
        for j in range(nv + m + 1):
            obj[j] -= T[i][j]
    # obj holds negative reduced costs convention: we minimize; entering col with obj[j] < 0
    while True:
        piv_j = -1
        for j in range(nv + m):
            if obj[j] < 0:
                piv_j = j
                break  # Bland
        if piv_j == -1:
            break
        piv_i, best = -1, None
        for i in range(m):
            if T[i][piv_j] > 0:
                ratio = T[i][-1] / T[i][piv_j]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[piv_i]):
                    best, piv_i = ratio, i
        if piv_i == -1:
            break  # unbounded (cannot happen in phase I)
        # pivot
        pv = T[piv_i][piv_j]
        T[piv_i] = [x / pv for x in T[piv_i]]
        for i in range(m):
            if i != piv_i and T[i][piv_j] != 0:
                f = T[i][piv_j]
                T[i] = [a - f * c for a, c in zip(T[i], T[piv_i])]
        if obj[piv_j] != 0:
            f = obj[piv_j]
            obj = [a - f * c for a, c in zip(obj, T[piv_i])]
        basis[piv_i] = piv_j
    opt = -obj[-1]  # objective value = sum of artificials
    if opt == 0:
        z = [Fraction(0)] * nv
        for i, bj in enumerate(basis):
            if bj < nv:
                z[bj] = T[i][-1]
        return True, z
    # infeasible: dual y from reduced costs of artificial columns
    # reduced cost of artificial j (col nv+j) is obj[nv+j]; y_i = cost_i - reduced = 1 - (1+obj)? Standard:
    # y^T = c_B^T B^{-1}; artificial col e_i => y_i = 1 - obj[nv+i]... derive: obj[j] = c_j - y^T A_j.
    # For artificial i: A_j = e_i (after sign flip), c_j = 1 => obj[nv+i] = 1 - y_i => y_i = 1 - obj[nv+i].
    y = [Fraction(1) - obj[nv + i] for i in range(m)]
    # undo sign flips: original row i was multiplied by sign[i]
    y = [sign[i] * y[i] for i in range(m)]
    return False, y


def _simplex_minimize(M, b, c):
    """Exact: min c'z s.t. M z = b, z >= 0. Assumes feasible & bounded.
    Returns (opt_value, z). Phase I via _simplex_feasible-style artificials,
    then Phase II with Bland's rule."""
    m = len(M)
    nv = len(M[0])
    M = [row[:] for row in M]
    b = b[:]
    for i in range(m):
        if b[i] < 0:
            M[i] = [-x for x in M[i]]
            b[i] = -b[i]
    T = [M[i] + [Fraction(1) if j == i else Fraction(0) for j in range(m)] + [b[i]]
         for i in range(m)]
    basis = [nv + i for i in range(m)]

    def run(obj_costs, allowed):
        # canonical reduced-cost row
        obj = [Fraction(x) for x in obj_costs] + [Fraction(0)]
        for i in range(m):
            if obj_costs[basis[i]] != 0:
                f = obj[basis[i]]
                obj[:] = [a - f * cc for a, cc in zip(obj, T[i])]
        while True:
            piv_j = -1
            for j in allowed:
                if obj[j] < 0:
                    piv_j = j
                    break
            if piv_j == -1:
                return obj
            piv_i, best = -1, None
            for i in range(m):
                if T[i][piv_j] > 0:
                    r = T[i][-1] / T[i][piv_j]
                    if best is None or r < best or (r == best and basis[i] < basis[piv_i]):
                        best, piv_i = r, i
            assert piv_i != -1, "unbounded"
            pv = T[piv_i][piv_j]
            T[piv_i][:] = [x / pv for x in T[piv_i]]
            for i in range(m):
                if i != piv_i and T[i][piv_j] != 0:
                    f = T[i][piv_j]
                    T[i][:] = [a - f * cc for a, cc in zip(T[i], T[piv_i])]
            if obj[piv_j] != 0:
                f = obj[piv_j]
                obj[:] = [a - f * cc for a, cc in zip(obj, T[piv_i])]
            basis[piv_i] = piv_j

    # phase I: minimize sum of artificials
    p1 = [Fraction(0)] * nv + [Fraction(1)] * m
    obj = run(p1, range(nv + m))
    assert -obj[-1] == 0, "infeasible"
    # drive artificials out of basis if possible (pivot on any nonzero orig col)
    for i in range(m):
        if basis[i] >= nv:
            for j in range(nv):
                if T[i][j] != 0:
                    pv = T[i][j]
                    T[i][:] = [x / pv for x in T[i]]
                    for k in range(m):
                        if k != i and T[k][j] != 0:
                            f = T[k][j]
                            T[k][:] = [a - f * cc for a, cc in zip(T[k], T[i])]
                    basis[i] = j
                    break
    # phase II on original columns only
    p2 = [Fraction(x) for x in c] + [Fraction(0)] * m
    obj = run(p2, range(nv))
    z = [Fraction(0)] * nv
    for i, bj in enumerate(basis):
        if bj < nv:
            z[bj] = T[i][-1]
    val = sum(ci * zi for ci, zi in zip(c, z))
    return val, z


def fractional_total_domination(n, edges):
    """Exact d_f(G) = min 1'x s.t. A x >= 1, x >= 0 (rational)."""
    N = neighborhoods(n, edges)
    # vars: x_0..x_{n-1}, slacks s_0..s_{n-1}: Ax - s = 1
    nv = 2 * n
    M, b, c = [], [], [Fraction(1)] * n + [Fraction(0)] * n
    for v in range(n):
        row = [Fraction(1 if u in N[v] else 0) for u in range(n)]
        row += [Fraction(-1) if u == v else Fraction(0) for u in range(n)]
        M.append(row)
        b.append(Fraction(1))
    val, z = _simplex_minimize(M, b, c)
    x = z[:n]
    for v in range(n):
        assert sum(x[u] for u in N[v]) >= 1
    assert sum(x) == val
    return val, x


def ax_eq_1_nonneg_feasible(n, edges):
    """Feasibility of A x = 1, x >= 0 (Brandt Conjecture 5.1 conclusion)."""
    N = neighborhoods(n, edges)
    M = [[Fraction(1 if u in N[v] else 0) for u in range(n)] for v in range(n)]
    b = [Fraction(1)] * n
    ok, res = _simplex_feasible(M, b)
    if ok:
        for v in range(n):
            assert sum(res[u] for u in N[v]) == 1
    return ok, res


def lp1_multiplication_feasible(n, edges):
    """Feasibility of {x >= 1, A x = c 1}. Returns (feasible, witness_or_certificate).

    feasible -> (True, (x list Fractions, c Fraction))
    infeasible -> (False, y) Farkas: 1^T y = 0, A y >= 0, 1^T A y > 0.
    """
    N = neighborhoods(n, edges)
    # variables: s_v = x_v - 1 >= 0 (n vars), c >= 0 split not needed (c>=degree>0), use c >= 0.
    # constraints: sum_{u in N(v)} (s_u + 1) - c = 0  =>  sum s_u - c = -deg(v)
    nv = n + 1  # s_0..s_{n-1}, c
    M, b = [], []
    for v in range(n):
        row = [Fraction(0)] * nv
        for u in N[v]:
            row[u] = Fraction(1)
        row[n] = Fraction(-1)
        M.append(row)
        b.append(Fraction(-len(N[v])))
    ok, res = _simplex_feasible(M, b)
    if ok:
        x = [res[v] + 1 for v in range(n)]
        c = res[n]
        # sanity
        for v in range(n):
            assert sum(x[u] for u in N[v]) == c
        return True, (x, c)
    y = res
    # sanity Farkas: y^T M <= 0 comp-wise, y^T b > 0 translates to our cert; convert:
    # y^T rows: for var u: sum_{v: u in N(v)} y_v = (A y)_u <= 0 ... careful signs.
    Ay = [sum(y[v] for v in range(n) if u in N[v]) for u in range(n)]
    ysum = sum(y)
    # y^T M <= 0: (A y)_u <= 0 for all u and -(sum y) <= 0.
    # y^T b > 0: -sum_v deg(v) y_v > 0 i.e. 1^T A y < 0.
    assert all(a <= 0 for a in Ay) and -ysum <= 0 and sum(len(N[v]) * y[v] for v in range(n)) < 0
    # Standard-form cert here: with x>=1 and c>=0: y^T(Ax - c) has Ax part <= via Ay<=0... produce
    # normalized certificate yy = -y: A yy >= 0, 1^T A yy > 0, and 1^T yy <= 0 (c side).
    yy = [-t for t in y]
    return False, yy


def lp2_blowup_degree_feasible(n, edges):
    """Exists rational w >= 1 with 3*sum_{u in N(v)} w_u >= sum_u w_u for all v?"""
    N = neighborhoods(n, edges)
    # w_v = s_v + 1, s >= 0; slack t_v >= 0:
    # 3*sum_{u in N(v)} s_u - sum_u s_u - t_v = n - 3*deg(v)
    nv = n + n
    M, b = [], []
    for v in range(n):
        row = [Fraction(0)] * nv
        for u in range(n):
            row[u] = (Fraction(3) if u in N[v] else Fraction(0)) - 1
        row[n + v] = Fraction(-1)
        M.append(row)
        b.append(Fraction(n - 3 * len(N[v])))
    ok, res = _simplex_feasible(M, b)
    if not ok:
        return False, None
    w = [res[v] + 1 for v in range(n)]
    for v in range(n):
        assert 3 * sum(w[u] for u in N[v]) >= sum(w)
    return True, w

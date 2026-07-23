"""P16 childC — CP-SAT search for an equitable-quotient counterexample to BHS
Bounds 44 / 46 with an *eigenvector-certificate* encoding, k = 4..10 cells.

Key idea. Restrict to quotient matrices whose support is a TREE on the k cells
(with zero diagonal). Then:
  * realizability (DHS Lemma 2.3) is automatic: ratio consistency along a tree
    never fails, and cell sizes can be scaled up (search_common.quotient_ok);
  * the quotient graph is bipartite, so L_B = diag(s) - B is sign-similar to
    the entrywise-NONNEGATIVE matrix Q_B = diag(s) + B, hence
    lam_max(L_B) = lam_max(Q_B) and Collatz-Wielandt applies:
        lam_max(Q_B) >= min_i (Q_B x)_i / x_i  for any positive vector x.

CP-SAT model (all-integer, polynomial constraints):
  variables  B_ij >= 1 on tree edges (both directions independent), x_i >= 1,
             T (eigenvalue lower bound scaled by W).
  s_i  = sum_j B_ij                     (cell degree)
  P_i  = sum_j B_ij * s_j = s_i * m_i   (integer neighbor-degree sum)
  certificate:   W * sum_j Q_ij x_j  >=  T * x_i          for all i
  violation, Bound 44 (cleared of denominators, s_i m_i = P_i):
      (T - 2W)^2 * s_i s_j  >  W^2 * 2*( ((s_i-1)^2 + (s_j-1)^2 - s_i s_j) * s_i s_j
                                          + P_i P_j )                for every tree edge ij
  violation, Bound 46:
      (T - 2W)^2 * (P_i s_j + P_j s_i)
          >  W^2 * ( (2(s_i^2+s_j^2)+4)(P_i s_j + P_j s_i) - 16 (s_i s_j)^2 )
      (m_i + m_j = (P_i s_j + P_j s_i)/(s_i s_j) > 0 always, so no -inf case)
  and T > 2W (needed for the squared form to be equivalent).

A feasible solution is (up to the certificate being exact-integer) already a
counterexample; it is then re-verified with the exact rational/Sturm verifier
runs/P16/v2/verify_p16.py (verify_quotient) before being claimed.

Infeasibility within the given entry/vector bounds is *negative search
evidence* for this structured family, not a proof.
"""
import argparse
import itertools
import sys
import time

import networkx as nx
import numpy as np
from ortools.sat.python import cp_model

sys.path.insert(0, "..")  # runs/P16/v2
import search_common  # noqa: E402


W = 32  # eigenvalue denominator scale


def tree_supports(k):
    """All nonisomorphic trees on k nodes, as edge lists."""
    return [list(T.edges()) for T in nx.nonisomorphic_trees(k)]


def build_model(k, edges, E, X, bound):
    m = cp_model.CpModel()
    adj = {}
    for (a, b) in edges:
        adj[(a, b)] = m.NewIntVar(1, E, f"B_{a}_{b}")
        adj[(b, a)] = m.NewIntVar(1, E, f"B_{b}_{a}")
    smax = k * E
    s = [m.NewIntVar(1, smax, f"s_{i}") for i in range(k)]
    for i in range(k):
        m.Add(s[i] == sum(adj[(i, j)] for j in range(k) if (i, j) in adj))
    # P_i = sum_j B_ij * s_j
    Pmax = smax * smax
    P = [m.NewIntVar(1, Pmax, f"P_{i}") for i in range(k)]
    prod_cache = {}
    for i in range(k):
        terms = []
        for j in range(k):
            if (i, j) in adj:
                p = m.NewIntVar(1, E * smax, f"Bs_{i}_{j}")
                m.AddMultiplicationEquality(p, [adj[(i, j)], s[j]])
                terms.append(p)
        m.Add(P[i] == sum(terms))
    # certificate
    Tmax = (2 * smax + 4) * W
    T = m.NewIntVar(2 * W + 1, Tmax, "T")
    x = [m.NewIntVar(1, X, f"x_{i}") for i in range(k)]
    for i in range(k):
        # W * (s_i x_i + sum_j B_ij x_j) >= T * x_i
        lhs_terms = []
        sx = m.NewIntVar(1, smax * X, f"sx_{i}")
        m.AddMultiplicationEquality(sx, [s[i], x[i]])
        lhs_terms.append(sx)
        for j in range(k):
            if (i, j) in adj:
                bx = m.NewIntVar(1, E * X, f"bx_{i}_{j}")
                m.AddMultiplicationEquality(bx, [adj[(i, j)], x[j]])
                lhs_terms.append(bx)
        Tx = m.NewIntVar(0, Tmax * X, f"Tx_{i}")
        m.AddMultiplicationEquality(Tx, [T, x[i]])
        m.Add(W * sum(lhs_terms) >= Tx)
    # (T-2W)^2
    Tm = m.NewIntVar(1, Tmax, "Tm")
    m.Add(Tm == T - 2 * W)
    T2 = m.NewIntVar(1, Tmax * Tmax, "T2")
    m.AddMultiplicationEquality(T2, [Tm, Tm])

    def prod(vars_, lo, hi, name):
        v = m.NewIntVar(lo, hi, name)
        m.AddMultiplicationEquality(v, vars_)
        return v

    for (a, b) in edges:
        ss = prod([s[a], s[b]], 1, smax * smax, f"ss_{a}_{b}")
        if bound == 44:
            # lhs = T2 * ss ;  rhs = W^2 * 2*(C*ss + P_a P_b), C = (s_a-1)^2+(s_b-1)^2-s_a s_b
            sa1 = m.NewIntVar(0, smax, f"sa1_{a}_{b}")
            m.Add(sa1 == s[a] - 1)
            sb1 = m.NewIntVar(0, smax, f"sb1_{a}_{b}")
            m.Add(sb1 == s[b] - 1)
            qa = prod([sa1, sa1], 0, smax * smax, f"qa_{a}_{b}")
            qb = prod([sb1, sb1], 0, smax * smax, f"qb_{a}_{b}")
            C = m.NewIntVar(-smax * smax, 2 * smax * smax, f"C_{a}_{b}")
            m.Add(C == qa + qb - ss)
            Css = prod([C, ss], -smax ** 4, 2 * smax ** 4, f"Css_{a}_{b}")
            PP = prod([P[a], P[b]], 1, Pmax * Pmax, f"PP_{a}_{b}")
            lhs = prod([T2, ss], 0, Tmax * Tmax * smax * smax, f"lhs_{a}_{b}")
            m.Add(lhs > 2 * W * W * (Css + PP))
        else:
            # D = P_a s_b + P_b s_a
            Ps1 = prod([P[a], s[b]], 1, Pmax * smax, f"Ps1_{a}_{b}")
            Ps2 = prod([P[b], s[a]], 1, Pmax * smax, f"Ps2_{a}_{b}")
            D = m.NewIntVar(2, 2 * Pmax * smax, f"D_{a}_{b}")
            m.Add(D == Ps1 + Ps2)
            qa = prod([s[a], s[a]], 1, smax * smax, f"qa_{a}_{b}")
            qb = prod([s[b], s[b]], 1, smax * smax, f"qb_{a}_{b}")
            F = m.NewIntVar(4, 4 * smax * smax + 4, f"F_{a}_{b}")
            m.Add(F == 2 * qa + 2 * qb + 4)
            FD = prod([F, D], 0, (4 * smax * smax + 4) * 2 * Pmax * smax, f"FD_{a}_{b}")
            ss2 = prod([ss, ss], 1, smax ** 4, f"ss2_{a}_{b}")
            lhs = prod([T2, D], 0, Tmax * Tmax * 2 * Pmax * smax, f"lhs46_{a}_{b}")
            m.Add(lhs > W * W * (FD - 16 * ss2))
    return m, adj, s, T, x


def run(k, E, X, bound, budget):
    found = []
    sups = tree_supports(k)
    per = max(budget / max(len(sups), 1), 5.0)
    for edges in sups:
        model, adj, s, T, x = build_model(k, edges, E, X, bound)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = per
        solver.parameters.num_workers = 8
        st = solver.Solve(model)
        name = solver.StatusName(st)
        print(f"k={k} bound={bound} tree={edges} E={E} X={X} -> {name}", flush=True)
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            B = np.zeros((k, k), dtype=int)
            for (i, j), v in adj.items():
                B[i, j] = solver.Value(v)
            print("CANDIDATE B =", B.tolist(), "T/W =", solver.Value(T) / W,
                  "x =", [solver.Value(v) for v in x], flush=True)
            found.append((B, solver.Value(T)))
    return found


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kmin", type=int, default=4)
    ap.add_argument("--kmax", type=int, default=10)
    ap.add_argument("--bound", type=int, required=True)
    ap.add_argument("--budget", type=float, default=600.0, help="seconds per k")
    args = ap.parse_args()
    t0 = time.time()
    all_found = []
    for k in range(args.kmin, args.kmax + 1):
        # entry bound chosen to keep CP-SAT products < 2^62
        smax_target = 600
        E = max(smax_target // k, 30)
        # check overflow bounds
        smax = k * E
        Tmax = (2 * smax + 4) * W
        worst = Tmax * Tmax * 2 * (smax * smax) * smax  # lhs46 domain
        assert worst < 2 ** 62, (k, E, worst)
        found = run(k, E, X=2000, bound=args.bound, budget=args.budget)
        all_found.extend(found)
    print(f"TOTAL candidates: {len(all_found)}  elapsed {time.time()-t0:.0f}s", flush=True)

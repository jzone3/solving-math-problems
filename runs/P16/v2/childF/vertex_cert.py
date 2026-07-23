"""Vertex-certificate scan for Conjecture D1 (P16 childF).

D1: K = diag(arg46) - A_L^2 >= 0 for connected delta>=2 graphs.

Reformulation chain (all rigorous):
  1. A_L^2 is symmetric nonnegative.  Generalized diagonal dominance:
     for any y > 0,  diag((A_L^2 y)/y) - A_L^2 >= 0.
     Hence  exists y>0 with A_L^2 y <= arg46 * y  ==>  D1 for that graph.
     (Conversely, if diag(arg) - A_L^2 > 0 strictly, such y exists:
      Perron theory on diag(arg)^{-1} A_L^2.)
  2. Ansatz  y = diag(w) R^T Z,  w_e = 1/(arg46(e) - 4 + eps),  Z > 0 vertex vec.
     Then A_L^2 y = R^T (Q-4I) R y + 4 y  and  R y = H_eps Z,
     H_eps = R diag(w) R^T (weighted signless Laplacian), so
       A_L^2 y <= (arg46 + eps) y   <==>   R^T[ (Q-4I) H_eps Z - Z ] <= 0  (edgewise)
     which is implied by the vertexwise condition (Q-4I) H_eps Z <= Z.
     Taking eps -> 0+ recovers K >= 0 (closed cone).

This script scans all connected delta>=2 graphs (nauty-geng) and checks:
  (a) closed-form Z candidates for the vertex condition v := (Q-4I)H Z - Z <= 0,
  (b) the weaker edge condition R^T v <= 0,
  (c) LP feasibility of exists Z>0 with (Q-4I)H Z <= Z (vertexwise),
  (d) LP feasibility of the edge version.
"""
import sys, subprocess
import numpy as np
from scipy.optimize import linprog

def graphs(n, extra="-d2"):
    p = subprocess.Popen(["nauty-geng", "-c", extra, str(n)], stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()

def g6_adj(g6):
    data = [ord(c) - 63 for c in g6]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]; idx += 1
    return A

def build(A, eps):
    n = A.shape[0]
    d = A.sum(1)
    m = (A @ d) / d
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    E = len(edges)
    R = np.zeros((n, E))
    arg = np.zeros(E)
    for k, (i, j) in enumerate(edges):
        R[i, k] = R[j, k] = 1
        arg[k] = 2*(d[i]**2 + d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
    w = 1.0/(arg - 4 + eps)
    H = R @ np.diag(w) @ R.T
    Q = np.diag(d) + A
    M = (Q - 4*np.eye(n)) @ H          # need  M Z <= Z
    return d, m, edges, R, arg, M

def check(n_lo, n_hi, eps=1e-6, tol=1e-9):
    cand_fail = {}; lp_v_fail = []; lp_e_fail = []; count = 0
    for n in range(n_lo, n_hi+1):
        for g6 in graphs(n):
            count += 1
            A = g6_adj(g6)
            d, m, edges, R, arg, M = build(A, eps)
            n_ = len(d)
            B = M - np.eye(n_)          # need B Z <= 0
            # (a) closed-form candidates
            cands = {
                "ones": np.ones(n_), "d": d, "d-2+1": d-1, "dm": d*m,
                "d^2": d**2, "m": m, "d+m": d+m, "d*(d-2)+2": d*(d-2)+2,
            }
            for name, Z in cands.items():
                if np.max(B @ Z) > tol:
                    cand_fail.setdefault(name, []).append(g6)
            # (c) LP vertex: exists Z, 1 <= Z <= 1e6, B Z <= 0
            res = linprog(np.zeros(n_), A_ub=B, b_ub=np.zeros(n_),
                          bounds=[(1, 1e6)]*n_, method="highs")
            if not res.success:
                lp_v_fail.append(g6)
                # (d) LP edge version: R^T B Z <= 0
                res2 = linprog(np.zeros(n_), A_ub=R.T @ B, b_ub=np.zeros(len(edges)),
                               bounds=[(1, 1e6)]*n_, method="highs")
                if not res2.success:
                    lp_e_fail.append(g6)
    print(f"n={n_lo}..{n_hi}: {count} graphs, eps={eps}")
    for name, fails in sorted(cand_fail.items(), key=lambda kv: len(kv[1])):
        print(f"  candidate {name:12s}: {len(fails)} failures  e.g. {fails[:3]}")
    ok = set(cands) - set(cand_fail)
    for name in ok:
        print(f"  candidate {name:12s}: 0 failures  <== WORKS")
    print(f"  LP vertex infeasible: {len(lp_v_fail)}  e.g. {lp_v_fail[:5]}")
    print(f"  LP edge   infeasible: {len(lp_e_fail)}  e.g. {lp_e_fail[:5]}")

if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    eps = float(sys.argv[3]) if len(sys.argv) > 3 else 1e-6
    check(lo, hi, eps)

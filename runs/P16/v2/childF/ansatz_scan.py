"""Scan structured ansaetze y = diag(v) R^T Z (Z>0 vertex vector) for the exact
edge certificate  A_L^2 y <= arg46 * y  (which implies D1 by generalized
diagonal dominance since A_L^2 is symmetric nonnegative).

For each ansatz (choice of positive edge weights v) run an LP over Z:
   exists Z with 1 <= Z <= 1e6  and  (A_L^2 - diag(arg)) diag(v) R^T Z <= 0.
Feasibility for all graphs => the ansatz is rich enough; then hunt closed form Z.
"""
import sys, subprocess
import numpy as np
from scipy.optimize import linprog
from vertex_cert import graphs, g6_adj

def run(n_lo, n_hi, tol=0.0):
    fails = {}
    count = 0
    for n in range(n_lo, n_hi+1):
        for g6 in graphs(n):
            count += 1
            A = g6_adj(g6); nn = A.shape[0]
            d = A.sum(1); m = (A @ d)/d
            edges = [(i,j) for i in range(nn) for j in range(i+1,nn) if A[i,j]]
            E = len(edges)
            R = np.zeros((nn,E)); arg = np.zeros(E)
            for k,(i,j) in enumerate(edges):
                R[i,k]=R[j,k]=1
                arg[k] = 2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
            AL = R.T@R - 2*np.eye(E)
            C = AL@AL - np.diag(arg)      # need C y <= 0, y = diag(v) R^T Z
            ansaetze = {
                "v=1":        np.ones(E),
                "v=1/arg":    1.0/arg,
                "v=1/(arg-4+.5)": 1.0/(arg-4+0.5),
                "v=1/(arg-4+2)":  1.0/(arg-4+2.0),
                "v=1/sqrt(arg)":  arg**-0.5,
                "v=1/(s)":    np.array([1.0/(d[i]+d[j]) for i,j in edges]),
                "v=1/(didj)": np.array([1.0/(d[i]*d[j]) for i,j in edges]),
            }
            for name, v in ansaetze.items():
                B = C @ np.diag(v) @ R.T
                res = linprog(np.zeros(nn), A_ub=B, b_ub=np.full(E, tol),
                              bounds=[(1,1e6)]*nn, method="highs")
                if not res.success:
                    fails.setdefault(name, []).append(g6)
    print(f"n={n_lo}..{n_hi}: {count} graphs (connected, delta>=2)")
    for name in sorted(set(list(fails)) ):
        print(f"  {name:16s}: {len(fails[name])} infeasible  e.g. {fails[name][:5]}")
    for name in ["v=1","v=1/arg","v=1/(arg-4+.5)","v=1/(arg-4+2)","v=1/sqrt(arg)","v=1/(s)","v=1/(didj)"]:
        if name not in fails:
            print(f"  {name:16s}: FEASIBLE FOR ALL")

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]),
        float(sys.argv[3]) if len(sys.argv)>3 else 0.0)

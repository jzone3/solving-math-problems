"""Deep scan of the shifted ansatz  y_e = (Z_i + Z_j)/(arg46(e) - 4 + c).

Checks per graph (connected, delta>=2):
  - LP feasibility of exists Z in [1,1e6]^n with C diag(v) R^T Z <= 0,
    C = A_L^2 - diag(arg46), v_e = 1/(arg_e - 4 + c).
  - closed-form Z candidates.
Reports failures.  Usage: shifted_scan.py n_lo n_hi c
"""
import sys
import numpy as np
from scipy.optimize import linprog
from vertex_cert import graphs, g6_adj

def data(A):
    nn = A.shape[0]
    d = A.sum(1); m = (A @ d)/d
    edges = [(i,j) for i in range(nn) for j in range(i+1,nn) if A[i,j]]
    E = len(edges)
    R = np.zeros((nn,E)); arg = np.zeros(E)
    for k,(i,j) in enumerate(edges):
        R[i,k]=R[j,k]=1
        arg[k] = 2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
    AL = R.T@R - 2*np.eye(E)
    return d,m,edges,R,arg,AL

def run(n_lo, n_hi, c):
    lp_fail = []; cand_fail = {}; count = 0
    for n in range(n_lo, n_hi+1):
        for g6 in graphs(n):
            count += 1
            A = g6_adj(g6)
            d,m,edges,R,arg,AL = data(A)
            nn = len(d); E = len(edges)
            v = 1.0/(arg - 4 + c)
            B = (AL@AL - np.diag(arg)) @ np.diag(v) @ R.T   # need B Z <= 0
            cands = {"ones": np.ones(nn), "d": d, "d^2": d*d,
                     "d(d-2)+2": d*(d-2)+2, "dm": d*m, "d+m": d+m,
                     "(d-2)m+2": (d-2)*m+2, "d^2+d": d*d+d}
            for name, Z in cands.items():
                if np.max(B @ Z) > 1e-9:
                    cand_fail.setdefault(name, []).append(g6)
            res = linprog(np.zeros(nn), A_ub=B, b_ub=np.zeros(E),
                          bounds=[(1,1e6)]*nn, method="highs")
            if not res.success:
                lp_fail.append(g6)
    print(f"n={n_lo}..{n_hi} c={c}: {count} graphs")
    for name, f in sorted(cand_fail.items(), key=lambda kv: len(kv[1])):
        print(f"  Z={name:10s}: {len(f)} fail  e.g. {f[:4]}")
    for name in ["ones","d","d^2","d(d-2)+2","dm","d+m","(d-2)m+2","d^2+d"]:
        if name not in cand_fail: print(f"  Z={name:10s}: WORKS FOR ALL")
    print(f"  LP infeasible: {len(lp_fail)}  {lp_fail[:8]}")

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))

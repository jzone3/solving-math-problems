"""childD: coverage statistics of the rigorous sufficient conditions
 (D2)  every edge: (d_i+d_j)(m_i+m_j) >= 4 d_i d_j          => Bound 46
 (D3a) exists a in [0,1] grid: every edge:
       2(d_i-2)d_i m_i^a/d_j^a + 2(d_j-2)d_j m_j^a/d_i^a <= arg46 - 4
on connected delta>=2 graphs. Usage: coverage.py NMAX
"""
import numpy as np, subprocess, sys

def graphs(n):
    p = subprocess.Popen(f"nauty-geng -qc -d2 {n}", shell=True,
                         stdout=subprocess.PIPE, text=True)
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
            A[i, j] = A[j, i] = bits[idx]
            idx += 1
    return A

AGRID = np.linspace(0, 1, 41)

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    cnt = c2 = c3 = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            N = A.shape[0]
            d = A.sum(1); m = A @ d / d
            E = [(i, j) for i in range(N) for j in range(i+1, N) if A[i, j]]
            di = np.array([d[i] for i, j in E]); dj = np.array([d[j] for i, j in E])
            mi = np.array([m[i] for i, j in E]); mj = np.array([m[j] for i, j in E])
            arg = 2*(di**2+dj**2) - 16*di*dj/(mi+mj) + 4
            cnt += 1
            if ((di+dj)*(mi+mj) >= 4*di*dj - 1e-9).all():
                c2 += 1; c3 += 1; continue
            ok = False
            for a in AGRID:
                lhs = 2*(di-2)*di*mi**a/dj**a + 2*(dj-2)*dj*mj**a/di**a
                if (lhs <= arg - 4 + 1e-9).all():
                    ok = True; break
            if ok: c3 += 1
    print(f"delta>=2 graphs n<= {nmax}: {cnt}; D2 covers {c2}; D3(power) covers {c3}")

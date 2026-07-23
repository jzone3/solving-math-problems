"""P16 childB: numerical testing of candidate lemmas for BHS bounds 44/46.

Correct statements (DHS Table 2):
  Bound 44: mu(G) <= max_{ij in E} [2 + sqrt(2((d_i-1)^2+(d_j-1)^2+m_i m_j - d_i d_j))]
  Bound 46: mu(G) <= max_{ij in E} [2 + sqrt(2(d_i^2+d_j^2) - 16 d_i d_j/(m_i+m_j) + 4)]
Edge terms with negative sqrt argument are treated as -inf.
"""
import numpy as np
import subprocess, sys, math

def graphs(n, extra="", suffix=""):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n} {suffix}", shell=True,
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

def stats(A):
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d  # average degree of neighbors
    L = np.diag(d) - A
    mu = np.linalg.eigvalsh(L)[-1]
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    return d, m, mu, edges

def term44(di, dj, mi, mj):
    arg = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    return 2 + math.sqrt(arg) if arg >= 0 else -math.inf

def term46(di, dj, mi, mj):
    arg = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    return 2 + math.sqrt(arg) if arg >= 0 else -math.inf

def rhs(A, term):
    d, m, mu, edges = stats(A)
    return max(term(d[i], d[j], m[i], m[j]) for i, j in edges), mu

def merris(A):
    d = A.sum(1); m = A @ d / d
    return (d + m).max()

if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    # E1/E2: is max term >= Merris bound max_i (d_i + m_i)?
    worst = {"44": (1e9, None), "46": (1e9, None),
             "44mu": (1e9, None), "46mu": (1e9, None)}
    cnt = 0
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, mu, edges = stats(A)
            mer = (d + m).max()
            r44 = max(term44(d[i], d[j], m[i], m[j]) for i, j in edges)
            r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in edges)
            for key, val in (("44", r44 - mer), ("46", r46 - mer),
                             ("44mu", r44 - mu), ("46mu", r46 - mu)):
                if val < worst[key][0]:
                    worst[key] = (val, g6)
            cnt += 1
    print(f"graphs checked: {cnt}")
    for k, (v, g) in worst.items():
        print(f"min gap {k}: {v:.6g}  at {g}")

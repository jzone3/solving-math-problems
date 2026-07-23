"""childD: test lambda-normalized edge Collatz-Wielandt for Bound 46.

Lemma (edge CW, lambda-form; from childB Lemma B2 with y_e = phi(d_i/L)phi(d_j/L)):
  For concave phi:(0,1)->(0,inf) and L > Delta(G): if every edge ij satisfies
     d_i phi(m_i/L)/phi(d_j/L) + d_j phi(m_j/L)/phi(d_i/L) <= L
  then mu(G) <= rho(Q) <= L.

Take L = RHS46(G). Test candidate universal phi:
  - identity phi(x)=x
  - two-piece linear phi_{c,t}(x) = x for x<=c, c+t(x-c) for x>c  (0<=t<=1 concave incr.)
  - phi(x) = x(1-x)^b
Report failures (graph, edge, deficit).
"""
import numpy as np, subprocess, sys, math
from itertools import product

def graphs(n, extra=""):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n}", shell=True,
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

def term46(di, dj, mi, mj):
    arg = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    return 2 + math.sqrt(arg) if arg >= 0 else -math.inf

def edge_data(A):
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    return d, m, edges

def make_phi(kind, p1=None, p2=None):
    if kind == "id":
        return lambda x: x
    if kind == "2p":  # breakpoint c=p1, slope t=p2
        c, t = p1, p2
        return lambda x: x if x <= c else c + t * (x - c)
    if kind == "xb":  # x(1-x)^b
        b = p1
        return lambda x: x * (1 - x) ** b
    if kind == "pow":
        return lambda x: x ** p1

def check_graph(d, m, edges, phi):
    """returns (ok, worst deficit, worst edge) for lambda = RHS46"""
    L = max(term46(d[i], d[j], m[i], m[j]) for i, j in edges)
    if L <= max(d.max(), m.max()):
        return False, -math.inf, None, L
    worst = math.inf; we = None
    for i, j in edges:
        cw = d[i] * phi(m[i] / L) / phi(d[j] / L) + d[j] * phi(m[j] / L) / phi(d[i] / L)
        s = L - cw
        if s < worst:
            worst = s; we = (i, j)
    return worst >= -1e-9, worst, we, L

if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    cands = [("id", None, None)]
    cands += [("2p", c, t) for c in (0.3,0.4,0.5,0.6,0.7,0.8) for t in (0.0,0.2,1/3,0.5,0.8)]
    cands += [("xb", b, None) for b in (0.1,0.2,0.3,0.5)]
    fails = {k: [0, math.inf, None] for k in range(len(cands))}
    phis = [make_phi(*c) for c in cands]
    cnt = 0
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges = edge_data(A)
            cnt += 1
            for k, phi in enumerate(phis):
                ok, w, we, L = check_graph(d, m, edges, phi)
                if not ok:
                    fails[k][0] += 1
                    if w < fails[k][1]:
                        fails[k][1] = w; fails[k][2] = (g6, we, L)
    print(f"graphs: {cnt}")
    for k, c in enumerate(cands):
        f = fails[k]
        print(f"{c}: fails={f[0]} worst={f[1]:.4g} at {f[2]}")

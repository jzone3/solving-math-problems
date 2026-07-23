"""childD: for each connected graph (optionally delta>=2), compute the set of
exponents a in [0,1] such that max_e CW_a(e) <= RHS46, where
  CW_a(e) = d_i m_i^a / d_j^a + d_j m_j^a / d_i^a   (childB Corollary B3).
Dump per-graph: g6, n, Delta, delta, maxm, minm, a_lo, a_hi (of the ok-set's
convex hull), n_ok, plus whether ok-set is an interval. Also record graphs with
empty ok-set.
Usage: python3 aintervals.py NMAX [d2] > aint.tsv
"""
import numpy as np, subprocess, sys, math

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

AGRID = np.linspace(0, 1, 201)

def process(g6):
    A = g6_adj(g6)
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    L = max(term46(d[i], d[j], m[i], m[j]) for i, j in edges)
    di = np.array([d[i] for i, j in edges]); dj = np.array([d[j] for i, j in edges])
    mi = np.array([m[i] for i, j in edges]); mj = np.array([m[j] for i, j in edges])
    ok = []
    for a in AGRID:
        cw = (di * mi**a / dj**a + dj * mj**a / di**a).max()
        ok.append(cw <= L + 1e-9)
    ok = np.array(ok)
    idx = np.nonzero(ok)[0]
    interval = False; alo = ahi = -1
    if len(idx):
        alo, ahi = AGRID[idx[0]], AGRID[idx[-1]]
        interval = (idx[-1] - idx[0] + 1) == len(idx)
    return (g6, n, int(d.max()), int(d.min()), m.max(), m.min(), alo, ahi,
            len(idx), int(interval), L)

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    extra = "-d2" if len(sys.argv) > 2 and sys.argv[2] == "d2" else ""
    print("g6\tn\tDelta\tdelta\tmaxm\tminm\talo\tahi\tnok\tinterval\tL")
    for n in range(3, nmax + 1):
        for g6 in graphs(n, extra):
            r = process(g6)
            print("\t".join(str(x) for x in r))

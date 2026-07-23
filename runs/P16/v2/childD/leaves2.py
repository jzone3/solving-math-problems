"""childD: refine leaf handling.
 (M)   RHS46(G-v) <= RHS46(G) for v a leaf?
 (L4r) rho(Q_G) <= max(leaf-edge t46 in G, RHS46(G-v))?  (Q-strengthened L4)
 (P1)  K(G) PSD even when delta=1? count failures
Usage: leaves2.py N RES MOD  (single n, geng -d1 filtered to delta==1)
"""
import numpy as np, subprocess, sys, math

def graphs(n, res, mod):
    p = subprocess.Popen(f"nauty-geng -qc {n} {res}/{mod}", shell=True,
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

def t46(di, dj, mi, mj):
    a = 2*(di*di+dj*dj) - 16*di*dj/(mi+mj) + 4
    return 2 + math.sqrt(a) if a >= 0 else -math.inf

def rhs46(A):
    d = A.sum(1); m = A @ d / d
    n = A.shape[0]
    return max(t46(d[i], d[j], m[i], m[j])
               for i in range(n) for j in range(i+1, n) if A[i, j])

def K_mineig(A):
    n = A.shape[0]
    d = A.sum(1); m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    E = len(edges)
    arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in edges])
    R = np.zeros((n, E))
    for e, (i, j) in enumerate(edges):
        R[i, e] = R[j, e] = 1
    AL = R.T @ R - 2*np.eye(E)
    return np.linalg.eigvalsh(np.diag(arg) - AL @ AL)[0]

if __name__ == "__main__":
    n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    wM = (1e9, None); wL = (1e9, None); psdfail = 0; cnt = 0; wP = (1e9, None)
    for g6 in graphs(n, res, mod):
        A = g6_adj(g6)
        d = A.sum(1)
        if d.min() != 1: continue
        cnt += 1
        m = A @ d / d
        N = A.shape[0]
        rho = np.linalg.eigvalsh(np.diag(d) + A)[-1]
        R46 = rhs46(A)
        leafT = max(t46(d[i], d[j], m[i], m[j]) for i in range(N)
                    for j in range(i+1, N) if A[i, j] and (d[i] == 1 or d[j] == 1))
        ke = K_mineig(A)
        if ke < -1e-9:
            psdfail += 1
            if ke < wP[0]: wP = (ke, g6)
        # all leaves v (worst case over choices? require FOR EVERY leaf -> use max slack;
        # for existence of good leaf use min; check both: report EXISTS-leaf version)
        bestM = -1e9; bestL = -1e9
        for v in range(N):
            if d[v] != 1: continue
            keep = [u for u in range(N) if u != v]
            B = A[np.ix_(keep, keep)]
            if len(keep) < 2 or B.sum() == 0 or B.sum(1).min() == 0:
                sub = 2.0  # K2/K1 edge cases: mu<=2<=any leafT
            else:
                sub = rhs46(B)
            bestM = max(bestM, R46 - sub)
            bestL = max(bestL, max(leafT, sub) - rho)
        if bestM < wM[0]: wM = (bestM, g6)
        if bestL < wL[0]: wL = (bestL, g6)
    print(f"n={n} {res}/{mod}: delta=1 graphs: {cnt}")
    print(f"M  (exists leaf: RHS46(G)-RHS46(G-v) >= 0): min {wM[0]:.6g} at {wM[1]}")
    print(f"L4r(exists leaf: max(leafT,RHS46(G-v)) - rho(Q)): min {wL[0]:.6g} at {wL[1]}")
    print(f"K PSD failures (delta=1): {psdfail}, worst {wP[0]:.4g} at {wP[1]}")

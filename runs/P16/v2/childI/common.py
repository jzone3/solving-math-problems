"""childI common: build M(G), B, T, canonical ground state h* (Perron of
diag(T)^{-1} B), and local invariants for regression.

Notation (childF): d = degrees, m_i = avg degree of neighbors, sigma = d+m-4,
arg46(ij) = 2(d_i^2+d_j^2) - 16 d_i d_j/(m_i+m_j) + 4, a_e = arg46 - 4,
w_e = 1/a_e (0 on degenerate edges, where sigma=0 at both ends),
H = R diag(w) R^T, Q = D_deg + A, D = diag(sigma),
M = 2D + 4I - Q - D H D = diag(T) - B,  T = 2 sigma + 4,  B = Q + D H D.
"""
import numpy as np
import subprocess


def g6_to_adj(g6):
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


def build(A):
    n = A.shape[0]
    d = A.sum(1)
    m = (A @ d) / d
    sig = d + m - 4.0
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    R = np.zeros((n, E))
    w = np.zeros(E)
    for k, (i, j) in enumerate(edges):
        R[i, k] = R[j, k] = 1
        a4 = 2 * (d[i] ** 2 + d[j] ** 2) - 16 * d[i] * d[j] / (m[i] + m[j])
        w[k] = 1.0 / a4 if a4 > 1e-9 else 0.0
    H = (R * w) @ R.T
    D = np.diag(sig)
    Q = np.diag(d) + A
    B = Q + D @ H @ D
    T = 2 * sig + 4
    M = np.diag(T) - B
    return dict(n=n, A=A, d=d, m=m, sig=sig, edges=edges, w=w, H=H, Q=Q,
                B=B, T=T, M=M)


def perron_h(B, T):
    """Perron vector h>0 and rho of diag(T)^{-1} B (irreducible for connected
    delta>=2 G since off-diagonals >= 1 on edges).  Mh = (1-rho) T*h."""
    P = B / T[:, None]
    ev, V = np.linalg.eig(P)
    k = np.argmax(ev.real)
    rho = ev[k].real
    h = V[:, k].real
    if h.sum() < 0:
        h = -h
    return rho, h / h.max()


def geng(n, extra=("-c", "-d2"), res=0, mod=1):
    cmd = ["nauty-geng", *extra, str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in p.stdout:
        yield line.strip()

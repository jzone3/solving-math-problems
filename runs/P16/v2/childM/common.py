"""childM common: M(s) builder for arbitrary diagonal s, capped sigma-hat
(F2'': s = sigma_c := d - 4 + min(m, d + c)), reusing childI's exact
definitions (bit-identical for s = d + m - 4).

Notation (childF): d = degrees, m_i = avg degree of neighbors,
arg46(ij) = 2(d_i^2+d_j^2) - 16 d_i d_j/(m_i+m_j) + 4, a_e = arg46 - 4,
w_e = 1/a_e (0 on degenerate a_e = 0 edges, where d = m = 2 at both ends so
sigma_c = 0 too — Corollary F1' extends to every cap c >= 0),
H = R diag(w) R^T, Q = D_deg + A,
M(s) = 2 diag(s) + 4I - Q - diag(s) H diag(s) = diag(T) - B,
T = 2s + 4, B = Q + diag(s) H diag(s).
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


def build_base(A):
    """Graph data + H (independent of the diagonal)."""
    n = A.shape[0]
    d = A.sum(1)
    m = (A @ d) / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    R = np.zeros((n, E))
    w = np.zeros(E)
    for k, (i, j) in enumerate(edges):
        a4 = 2 * (d[i] ** 2 + d[j] ** 2) - 16 * d[i] * d[j] / (m[i] + m[j])
        w[k] = 1.0 / a4 if a4 > 1e-9 else 0.0
        R[i, k] = R[j, k] = 1
    H = (R * w) @ R.T
    Q = np.diag(d) + A
    return dict(n=n, A=A, d=d, m=m, edges=edges, w=w, R=R, H=H, Q=Q)


def sigma_cap(d, m, c):
    return d - 4.0 + np.minimum(m, d + c)


def with_diag(bd, s):
    """Attach M(s), B, T for diagonal s."""
    D = np.diag(s)
    B = bd["Q"] + D @ bd["H"] @ D
    T = 2 * s + 4.0
    M = np.diag(T) - B
    out = dict(bd)
    out.update(s=s, B=B, T=T, M=M)
    return out


def build_cap(A, c):
    bd = build_base(A)
    return with_diag(bd, sigma_cap(bd["d"], bd["m"], c))


def min_eig(Ms):
    return np.linalg.eigvalsh(Ms)[0]


def perron(B, T):
    P = B / T[:, None]
    ev, V = np.linalg.eig(P)
    k = np.argmax(ev.real)
    rho = ev[k].real
    h = V[:, k].real
    if h.sum() < 0:
        h = -h
    return rho, h / h.max()


def geng(n, extra=("-c", "-d2"), res=0, mod=1):
    cmd = ["nauty-geng", "-q", *extra, str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in p.stdout:
        yield line.strip()


# ---- graph constructors (numpy adjacency) ------------------------------

def windmill(k):
    """F_k: k triangles sharing a hub. n = 2k+1, hub = 0."""
    n = 2 * k + 1
    A = np.zeros((n, n))
    for t in range(k):
        u, v = 1 + 2 * t, 2 + 2 * t
        A[0, u] = A[u, 0] = A[0, v] = A[v, 0] = A[u, v] = A[v, u] = 1
    return A


def hub_gadgets(gadgets):
    """One hub connected to every vertex of each gadget; gadgets are lists of
    (size, edgelist) with local indices."""
    n = 1 + sum(g[0] for g in gadgets)
    A = np.zeros((n, n))
    off = 1
    for sz, el in gadgets:
        for a in range(sz):
            A[0, off + a] = A[off + a, 0] = 1
        for a, b in el:
            A[off + a, off + b] = A[off + b, off + a] = 1
        off += sz
    return A


def gadget_cycle(l):
    return (l, [(i, (i + 1) % l) for i in range(l)])


def gadget_path(l):
    return (l, [(i, i + 1) for i in range(l - 1)])


def gadget_clique(l):
    return (l, [(i, j) for i in range(l) for j in range(i + 1, l)])

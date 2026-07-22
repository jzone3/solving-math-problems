"""Core utilities for P09 (Bollobas-Nikiforov) V1 annealed search.

Graph representation: n, and adjacency as list of int bitmasks (adj[i] bit j set iff ij edge).
Score = lambda1^2 + lambda2^2 - 2m(1 - 1/omega).  Conjecture: score <= 0 for all G != K_n.
A counterexample has score > 0.
"""
import numpy as np


def adj_matrix(n, adj):
    A = np.zeros((n, n))
    for i in range(n):
        m = adj[i]
        while m:
            j = (m & -m).bit_length() - 1
            A[i, j] = 1.0
            m &= m - 1
    return A


def top2_eigs(n, adj):
    A = adj_matrix(n, adj)
    w = np.linalg.eigvalsh(A)
    return w[-1], w[-2]


def num_edges(adj):
    return sum(bin(m).count("1") for m in adj) // 2


def max_clique(n, adj):
    """Exact maximum clique via Tomita-style branch and bound with greedy coloring."""
    best = [0]

    order = sorted(range(n), key=lambda v: bin(adj[v]).count("1"))

    def color_sort(P_list):
        # greedy coloring; returns list of (v, color) sorted by color asc
        colors = {}
        color_classes = []
        for v in P_list:
            placed = False
            for ci, cls in enumerate(color_classes):
                if not (adj[v] & cls[0]):
                    cls[0] |= 1 << v
                    cls[1].append(v)
                    colors[v] = ci + 1
                    placed = True
                    break
            if not placed:
                color_classes.append([1 << v, [v]])
                colors[v] = len(color_classes)
        out = [(v, colors[v]) for v in P_list]
        out.sort(key=lambda x: x[1])
        return out

    def expand(P_mask, size):
        if not P_mask:
            if size > best[0]:
                best[0] = size
            return
        P_list = [v for v in order if (P_mask >> v) & 1]
        cs = color_sort(P_list)
        for idx in range(len(cs) - 1, -1, -1):
            v, c = cs[idx]
            if size + c <= best[0]:
                return
            expand(P_mask & adj[v], size + 1)
            P_mask &= ~(1 << v)

    expand((1 << n) - 1, 0)
    return best[0]


def evaluate(n, adj):
    """Return (score, ratio, l1, l2, m, omega)."""
    m = num_edges(adj)
    if m == 0:
        return -1e18, 0.0, 0.0, 0.0, 0, 1
    w = max_clique(n, adj)
    if w >= n:  # complete graph excluded
        return -1e18, 0.0, 0.0, 0.0, m, w
    l1, l2 = top2_eigs(n, adj)
    rhs = 2.0 * m * (1.0 - 1.0 / w)
    lhs = l1 * l1 + l2 * l2
    return lhs - rhs, (lhs / rhs if rhs > 0 else 0.0), l1, l2, m, w


def adj_to_g6(n, adj):
    """Encode as graph6 for logging/reproducibility."""
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6:
        bits.append(0)
    chars = []
    if n <= 62:
        chars.append(chr(n + 63))
    else:
        chars.append(chr(126))
        chars.append(chr(((n >> 12) & 63) + 63))
        chars.append(chr(((n >> 6) & 63) + 63))
        chars.append(chr((n & 63) + 63))
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        chars.append(chr(v + 63))
    return "".join(chars)


def g6_to_adj(s):
    s = s.strip()
    if s[0] == "~":
        n = ((ord(s[1]) - 63) << 12) | ((ord(s[2]) - 63) << 6) | (ord(s[3]) - 63)
        data = s[4:]
    else:
        n = ord(s[0]) - 63
        data = s[1:]
    bits = []
    for ch in data:
        v = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj

"""Common utilities for P09 V2 (structured two-eigenvalue design) search.

Conjecture (Bollobas-Nikiforov, JCTB 97 (2007), Conj. 1):
for every graph G != K_n with m edges and clique number w:
    lambda1^2 + lambda2^2 <= 2m(1 - 1/w).

score(G) = lambda1^2 + lambda2^2 - 2m(1-1/w).  A violation is score > 0.
Equality holds e.g. for K_a u K_a and complete multipartite graphs.
"""
import itertools
import numpy as np


def top2_eigs_dense(A):
    ev = np.linalg.eigvalsh(A)
    return ev[-1], ev[-2]


def score_from(l1, l2, m, w):
    return l1 * l1 + l2 * l2 - 2.0 * m * (1.0 - 1.0 / w)


def graph_score(A, w):
    """A: symmetric 0/1 numpy adjacency; w: exact clique number (caller-known)."""
    m = int(A.sum()) // 2
    l1, l2 = top2_eigs_dense(A.astype(float))
    return score_from(l1, l2, m, w), l1, l2, m


def max_clique_exact(adj_sets, n):
    """Simple branch-and-bound max clique on small graphs (n <= ~60 sparse)."""
    best = [0]

    def expand(R, P):
        if not P:
            best[0] = max(best[0], len(R))
            return
        if len(R) + len(P) <= best[0]:
            return
        Plist = sorted(P, key=lambda v: -len(adj_sets[v] & P))
        for v in Plist:
            if len(R) + len(P) <= best[0]:
                return
            expand(R | {v}, P & adj_sets[v])
            P = P - {v}

    expand(set(), set(range(n)))
    return best[0]


def clique_number_np(A):
    n = A.shape[0]
    adj = [set(np.nonzero(A[i])[0].tolist()) for i in range(n)]
    return max_clique_exact(adj, n)


# ---------- blow-up machinery (exact via equitable-partition quotient) ------

def blowup_quotient_eigs(F_adj, weights, types):
    """Blow-up of pattern graph F: vertex i replaced by K_{n_i} (type 'K')
    or empty graph on n_i vertices (type 'I'); pattern edges -> complete joins.

    Non-quotient eigenvalues are -1 (inside cliques) and 0 (inside independent
    sets), so lambda1, lambda2 of the blow-up are the top two eigenvalues of
    the k x k quotient matrix Q with
       Q[i][j] = n_j * F_adj[i][j]  (i != j),
       Q[i][i] = n_i - 1 if type K else 0,
    provided the quotient's second eigenvalue >= 0 (always true here for
    lambda2-candidates > 0; we also compare against -1/0 floor).
    Returns (l1, l2, m, is_complete).
    """
    k = len(weights)
    n = sum(weights)
    Q = np.zeros((k, k))
    m = 0
    for i in range(k):
        if types[i] == 'K':
            Q[i, i] = weights[i] - 1
            m += weights[i] * (weights[i] - 1) // 2
        for j in range(k):
            if i != j and F_adj[i][j]:
                Q[i, j] = weights[j]
                if i < j:
                    m += weights[i] * weights[j]
    # symmetrize via D^{1/2} similarity for stable eigensolve
    d = np.sqrt(np.array(weights, dtype=float))
    S = Q * (d[:, None] / d[None, :])
    S = (S + S.T) / 2
    ev = np.sort(np.linalg.eigvalsh(S))
    l1 = ev[-1]
    l2 = ev[-2] if k >= 2 else -1.0
    # floor eigenvalues from inside blobs
    floor = -1.0 if any(t == 'K' and wgt >= 2 for t, wgt in zip(types, weights)) else None
    if floor is not None and l2 < floor:
        l2 = floor
    if any(t == 'I' and wgt >= 2 for t, wgt in zip(types, weights)) and l2 < 0.0:
        l2 = 0.0
    is_complete = (m == n * (n - 1) // 2)
    return l1, l2, m, is_complete


def blowup_clique_number(F_adj, weights, types):
    """omega of the blow-up = max over cliques C of F of sum of contributions:
    n_i for type K, 1 for type I."""
    k = len(weights)
    contrib = [weights[i] if types[i] == 'K' else 1 for i in range(k)]
    best = [0]

    def expand(R, P, val):
        if not P:
            best[0] = max(best[0], val)
            return
        ub = val + sum(contrib[v] for v in P)
        if ub <= best[0]:
            return
        Pl = list(P)
        for v in Pl:
            if val + sum(contrib[u] for u in P) <= best[0]:
                return
            expand(R | {v}, P & nbr[v], val + contrib[v])
            P = P - {v}

    nbr = [set(j for j in range(k) if F_adj[i][j]) for i in range(k)]
    expand(set(), set(range(k)), 0)
    return best[0]


def blowup_score(F_adj, weights, types):
    l1, l2, m, is_complete = blowup_quotient_eigs(F_adj, weights, types)
    if is_complete:
        return None
    w = blowup_clique_number(F_adj, weights, types)
    return score_from(l1, l2, m, w), l1, l2, m, w


def all_graphs(k):
    """All non-isomorphic-ish (all labeled, fine for small k) graphs on k vertices,
    as adjacency matrices; dedupe by canonical form via brute perms."""
    pairs = list(itertools.combinations(range(k), 2))
    seen = set()
    out = []
    perms = list(itertools.permutations(range(k)))
    for mask in range(1 << len(pairs)):
        A = [[0] * k for _ in range(k)]
        for b, (i, j) in enumerate(pairs):
            if mask >> b & 1:
                A[i][j] = A[j][i] = 1
        canon = min(
            tuple(A[p[i]][p[j]] for i in range(k) for j in range(k))
            for p in perms
        )
        if canon in seen:
            continue
        seen.add(canon)
        out.append(A)
    return out

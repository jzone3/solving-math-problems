"""Wide-range scans of star/clique interpolating families for f = dev - R > 0.

Uses degree-sequence formula for dev (machine-verified in explore2.py).
"""
import math


def f_from_graph(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    m = len(edges)
    if m == 0:
        return 0.0
    var = (sum(x * x for x in d) + 2 * m) / n - (2 * m / n) ** 2
    R = sum(1.0 / math.sqrt(d[u] * d[v]) for u, v in edges)
    return math.sqrt(max(var, 0.0)) - R


def f_split(q, s, k):
    """complete split: clique q joined to s independent vertices, + k isolated.
    Closed form, O(1)."""
    n = q + s + k
    m = q * (q - 1) // 2 + q * s
    dq = q - 1 + s
    S = q * dq * dq + s * q * q
    var = (S + 2 * m) / n - (2 * m / n) ** 2
    R = (q * (q - 1) / 2) / dq + q * s / math.sqrt(dq * q)
    return math.sqrt(max(var, 0.0)) - R


def f_star_clique(q, s, k):
    """center vertex in a clique K_q and adjacent to s leaves, + k isolated."""
    n = q + s + k
    edges = [(i, j) for i in range(q) for j in range(i + 1, q)]
    edges += [(0, q + i) for i in range(s)]
    return f_from_graph(n, edges)


if __name__ == "__main__":
    best = (-1e9, None)
    for q in range(1, 200):
        for s in range(0, 4000, 1 if q < 20 else 7):
            # optimal padding k ~ n* = 8m^2/(S+2m) - (q+s); scan around it
            m = q * (q - 1) // 2 + q * s
            if m == 0:
                continue
            dq = q - 1 + s
            S = q * dq * dq + s * q * q
            kopt = int(8 * m * m / (S + 2 * m)) - (q + s)
            for k in set([0, max(0, kopt - 1), max(0, kopt), max(0, kopt + 1)]):
                f = f_split(q, s, k)
                if f > best[0]:
                    best = (f, ("split", q, s, k))
    print("complete split wide:", best)

    best = (-1e9, None)
    for q in range(2, 120):
        for s in range(0, 800):
            for k in range(0, 3):
                # padding rarely helps star-like; also try near-optimal padding
                f = f_star_clique(q, s, k)
                if f > best[0]:
                    best = (f, ("star+clique", q, s, k))
    print("star-with-clique-center wide:", best)

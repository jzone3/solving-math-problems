"""Exhaustive check of all <= FLIPS edge-flip perturbations of the equality
graphs G_m = K_m + (m-2)K_1, up to symmetry.

Aut(G_m) = S_m x S_{m-2}, so any set of <= t flips touches <= 2t vertices and is
equivalent to one whose flipped pairs live inside the first 2t clique vertices
union the first 2t isolated vertices. We enumerate all flip subsets of size <= t
on that 4t-vertex window and evaluate f exactly-ish (float, err ~1e-12).

f(G) = sqrt((sum d^2 + 2m)/n - (2m/n)^2) - sum_{uv in E} 1/sqrt(d_u d_v)
"""
import math
import sys
from itertools import combinations


def f_from_adj(adj, n):
    d = [len(a) for a in adj]
    m = sum(d) // 2
    if m == 0:
        return 0.0
    var = (sum(x * x for x in d) + 2 * m) / n - (2 * m / n) ** 2
    R = 0.0
    for u in range(n):
        for v in adj[u]:
            if v > u:
                R += 1.0 / math.sqrt(d[u] * d[v])
    return math.sqrt(max(var, 0.0)) - R


def run(mq, t):
    k = mq - 2
    n = mq + k
    w = min(2 * t, mq)
    wi = min(2 * t, k)
    window = list(range(w)) + list(range(mq, mq + wi))
    pairs = [(u, v) for i, u in enumerate(window) for v in window[i + 1:]]
    base_adj = [set(range(mq)) - {i} if i < mq else set() for i in range(n)]
    best = -1e9
    barg = None
    for size in range(1, t + 1):
        for flips in combinations(pairs, size):
            adj = [set(s) for s in base_adj]
            for u, v in flips:
                if v in adj[u]:
                    adj[u].discard(v)
                    adj[v].discard(u)
                else:
                    adj[u].add(v)
                    adj[v].add(u)
            f = f_from_adj(adj, n)
            if f > best:
                best, barg = f, flips
    return best, barg


if __name__ == "__main__":
    t = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for mq in [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [4, 5, 6, 8, 10, 14, 20, 30, 50, 80, 120, 200]:
        best, barg = run(mq, t)
        print(f"m={mq:4d} (n={2*mq-2:4d}) best perturbed f = {best:+.9f} at flips {barg}",
              flush=True)
        if best > 0:
            print("POSITIVE CANDIDATE!", flush=True)

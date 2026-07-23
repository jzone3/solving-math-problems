"""Stage E: targeted hunt for the *necessary block structure*.

Reduction (see NOTES.md): if a 2-connected graph B has three vertices a,b,c with
  L_ab = L_bc = L_ca = M   (L_xy = longest x-y path length inside B)
and there exist optimal crossings Q_ab, Q_bc, Q_ca (each of length M) with
  c not in Q_ab,  a not in Q_bc,  b not in Q_ca,  and  Q_ab n Q_bc n Q_ca = {},
then attaching three pendant paths (arms) of equal length D > |V(B)| at a,b,c
yields a COUNTEREXAMPLE to Gallai-3: the three paths arm_a+Q_ab+arm_b, etc.,
are longest (length 2D+M) and have empty intersection.

So we exhaustively test every 2-connected block for this property.

Usage: pypy3 blockhunt.py <n> [res/mod]
"""
import subprocess
import sys
import time
from itertools import combinations

from families import graph6_to_edges
from lp_core import edges_to_adj, _comp_mask


def uv_longest(n, adj, u, v, forbidden=0):
    """Longest u-v path length (edges) avoiding `forbidden`, exact DFS."""
    best = [-1]

    def dfs(x, used, ln):
        if x == v:
            if ln > best[0]:
                best[0] = ln
            return
        rem = ~used & ((1 << n) - 1) & ~forbidden
        reach = _comp_mask(adj, 1 << x, rem | (1 << x))
        if not (reach >> v) & 1:
            return
        if ln + bin(reach & rem).count("1") <= best[0]:
            return
        nb = adj[x] & rem
        while nb:
            w = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            dfs(w, used | (1 << w), ln + 1)

    dfs(u, 1 << u, 0)
    return best[0]


def uv_optimal_paths(n, adj, u, v, L, cap=4000, forbidden=0):
    """All u-v paths of length exactly L avoiding `forbidden`, as bitmasks."""
    out = []

    def dfs(x, used, ln):
        if len(out) >= cap:
            return
        if x == v:
            if ln == L:
                out.append(used)
            return
        if ln >= L:
            return
        rem = ~used & ((1 << n) - 1) & ~forbidden
        reach = _comp_mask(adj, 1 << x, rem | (1 << x))
        if not (reach >> v) & 1:
            return
        if ln + bin(reach & rem).count("1") < L:
            return
        nb = adj[x] & rem
        while nb:
            w = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            dfs(w, used | (1 << w), ln + 1)

    dfs(u, 1 << u, 0)
    return out


def check_block(n, adj, g6):
    # all-pairs longest u-v path lengths
    L = {}
    for u, v in combinations(range(n), 2):
        L[(u, v)] = uv_longest(n, adj, u, v)
    for a, b, c in combinations(range(n), 3):
        M = L[(a, b)]
        if L[(b, c)] != M or L[(a, c)] != M:
            continue
        # cheap necessary tests: an optimal crossing avoiding the third vertex
        if uv_longest(n, adj, a, b, forbidden=1 << c) != M:
            continue
        if uv_longest(n, adj, b, c, forbidden=1 << a) != M:
            continue
        if uv_longest(n, adj, c, a, forbidden=1 << b) != M:
            continue
        Qab = uv_optimal_paths(n, adj, a, b, M, cap=1500, forbidden=1 << c)
        Qbc = uv_optimal_paths(n, adj, b, c, M, cap=1500, forbidden=1 << a)
        seen = set()
        for q1 in Qab:
            for q2 in Qbc:
                s = q1 & q2
                if s in seen:
                    continue
                seen.add(s)
                # need optimal c-a crossing disjoint from s (s contains b)
                if uv_longest(n, adj, c, a, forbidden=s) == M:
                    q3s = uv_optimal_paths(n, adj, c, a, M, cap=1, forbidden=s)
                    return (a, b, c, M, q1, q2, q3s[0])
    return None


def main():
    n = int(sys.argv[1])
    extra = [sys.argv[2]] if len(sys.argv) > 2 else []
    proc = subprocess.Popen(["nauty-geng", "-q", "-C", str(n)] + extra,
                            stdout=subprocess.PIPE, text=True)
    t0 = time.time()
    cnt = 0
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        cnt += 1
        nn, edges = graph6_to_edges(g6)
        adj = edges_to_adj(nn, edges)
        hit = check_block(nn, adj, g6)
        if hit:
            msg = "BLOCK HIT!!! g6=%s edges=%s abcM=%s masks=%s" % (
                g6, edges, hit[:4], hit[4:])
            print(msg)
            with open("BLOCKHIT_%d.txt" % n, "a") as f:
                f.write(msg + "\n")
        if cnt % 5000 == 0:
            print("n=%d cnt=%d elapsed=%.0fs" % (n, cnt, time.time() - t0))
            sys.stdout.flush()
    print("DONE n=%d blocks=%d elapsed=%.0fs" % (n, cnt, time.time() - t0))


if __name__ == "__main__":
    main()

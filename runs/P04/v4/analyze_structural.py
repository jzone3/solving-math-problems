"""Regenerate structurally tight n=16 instances (tight at K=7 with max degree
<= 12, i.e. degree bound only gives 6) from the k15split search trajectory,
analyze their structure, and cross-verify the CP-SAT infeasibility claim with an
independent pure-Python branch-and-bound cycle-removal search.
"""
import random, sys, time
import mincyc as M
from search import toggle_even_set, vertex_split, valid, canon, degrees


def independent_mincyc_lb(n, edges, k):
    """Independent check: return True iff a decomposition into <= k cycles exists.
    Pure-Python DFS: repeatedly extract the cycle through the lowest-indexed used
    vertex; canonical first-edge choice prunes symmetric branches."""
    E0 = frozenset(canon(edges))
    import functools
    sys.setrecursionlimit(10000)

    from functools import lru_cache

    def adj_of(E):
        a = {}
        for u, v in E:
            a.setdefault(u, set()).add(v)
            a.setdefault(v, set()).add(u)
        return a

    memo = {}

    def solve(E, k):
        if not E:
            return True
        if k == 0:
            return False
        key = (E, k)
        if key in memo:
            return memo[key]
        a = adj_of(E)
        v0 = min(a)  # lowest vertex must be in some cycle; enumerate cycles thru v0
        res = False
        nbrs = sorted(a[v0])
        # first step: to smallest-index neighbor choices; cycle returns to v0
        def paths(cur, used_edges, visited):
            # yields sets of edges forming a cycle from v0 back to v0
            for w in sorted(a[cur]):
                e = (min(cur, w), max(cur, w))
                if e in used_edges or e not in E:
                    continue
                if w == v0:
                    yield used_edges | {e}
                elif w not in visited:
                    yield from paths(w, used_edges | {e}, visited | {w})

        first = nbrs[0]  # wlog cycle uses edge (v0, first)? no! cycle through v0
        # must use two edges at v0; canonical: the smallest neighbor edge of v0
        # must be in SOME cycle; but not necessarily the same as v0's cycle set.
        # Since all edges at v0 are partitioned among cycles through v0, the edge
        # (v0, first) is in exactly one cycle. Enumerate cycles containing it.
        e0 = (min(v0, first), max(v0, first))
        for cyc in paths(first, frozenset([e0]), {v0, first}):
            if solve(E - cyc, k - 1):
                res = True
                break
        memo[key] = res
        return res

    return solve(E0, k)


def main():
    rng = random.Random(44)  # same seed as k15split run
    n0, E0 = M.complete_graph(15)
    pool = [(n0, E0)]
    r = None
    for _ in range(50):
        r = vertex_split(n0, E0, rng)
        if r and valid(*r):
            pool = [r]
            break
    found = []
    seen = set()
    it = 0
    while len(found) < 3 and it < 4000:
        it += 1
        weights = [len(e) ** 2 for _, e in pool]
        n, E = rng.choices(pool, weights=weights)[0]
        move = rng.random()
        if move < 0.25 and n % 2 == 1:
            r = vertex_split(n, E, rng)
        elif move < 0.5:
            r1 = toggle_even_set(n, E, rng, max_len=8)
            r = toggle_even_set(n, r1, rng, max_len=8) if r1 else None
            r = (n, r) if r else None
        else:
            r = toggle_even_set(n, E, rng, max_len=8)
            r = (n, r) if r else None
        if r is None or not valid(*r):
            continue
        nn, EE = r
        key = (nn, canon(EE))
        if key in seen:
            continue
        seen.add(key)
        K = (nn - 1) // 2
        ok, _ = M.decomposable_within(nn, EE, K, 120)
        if ok is not True:
            continue
        ok2, _ = M.decomposable_within(nn, EE, K - 1, 120)
        if ok2 is False:
            pool.append((nn, EE))
            if len(pool) > 40:
                pool.pop(1)
            deg = degrees(nn, EE)
            if nn == 16 and max(deg) <= 12 and len(EE) <= 45:
                found.append((nn, sorted(canon(EE))))
                print(f"STRUCTURAL TIGHT n={nn} m={len(EE)} deg={sorted(deg)}")
                print(f"  edges={sorted(canon(EE))}", flush=True)
    for nn, EE in found:
        K = (nn - 1) // 2
        deg = degrees(nn, EE)
        d2 = [v for v in range(nn) if deg[v] == 2]
        print(f"\nanalysis n={nn} m={len(EE)} K={K} deg2count={len(d2)} "
              f"degseq={sorted(d for d in deg if d)}")
        t = time.time()
        indep = independent_mincyc_lb(nn, EE, K - 1)
        print(f"independent check <= {K-1}: {indep} ({time.time()-t:.1f}s) "
              f"[CP-SAT said False]")
        t = time.time()
        indep2 = independent_mincyc_lb(nn, EE, K)
        print(f"independent check <= {K}: {indep2} ({time.time()-t:.1f}s) "
              f"[CP-SAT said True]", flush=True)


if __name__ == "__main__":
    main()

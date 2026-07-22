"""Probe 3d: exact-score annealing. Score = exact minimum cycle-decomposition
size (CP-SAT, downward search from heuristic UB). Maximize score; a graph with
score > floor((n-1)/2) is a counterexample. Moves = triangle XOR, state kept
Eulerian with delta >= 6.
"""
import random
import sys
import time
from hajos import hajos_ok, is_eulerian, rlc_decompose
from anneal import toggle

CACHE = {}

def valid(n, edges_set, maxdeg):
    """Eulerian, 6 <= deg <= maxdeg (Lov\u00e1sz path thm: a dominating vertex (deg n-1,
    n odd) forces a decomposition into (n-1)/2 cycles through it, so counterexamples
    have Delta <= n-3; we impose it as a search constraint)."""
    deg = [0] * n
    for u, v in edges_set:
        deg[u] += 1
        deg[v] += 1
    if any(d < 6 or d > maxdeg or d % 2 for d in deg):
        return False
    return is_eulerian(n, tuple(edges_set))

def exact_min(n, edges, tl=45):
    if edges in CACHE:
        return CACHE[edges]
    if len(CACHE) > 500_000:  # cap memory
        CACHE.clear()
    ub = rlc_decompose(n, edges, tries=300)
    k = len(ub)
    while k > 1:
        ok, _ = hajos_ok(n, edges, k=k - 1, time_limit=tl, workers=4)
        if ok is True:
            k -= 1
        else:
            break  # infeasible or unknown -> current k is (upper bound on) min
    CACHE[edges] = k
    return k

def run(n, seconds, seed):
    rng = random.Random(seed)
    bound = (n - 1) // 2
    maxdeg = n - 3 - ((n - 3) % 2)  # largest even degree <= n-3
    # start: circulant S={1,2,3,4}, degree 8
    edges_set = set()
    for d in (1, 2, 3, 4):
        for v in range(n):
            u, w = v, (v + d) % n
            edges_set.add((min(u, w), max(u, w)))
    assert valid(n, edges_set, maxdeg), "bad start"
    cur = exact_min(n, tuple(sorted(edges_set)))
    best = cur
    t0 = time.time()
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        temp = max(0.15, 1.5 * (1 - (time.time() - t0) / seconds))
        tri = rng.sample(range(n), 3)
        toggle(edges_set, tri)
        if not valid(n, edges_set, maxdeg):
            toggle(edges_set, tri)
            continue
        edges = tuple(sorted(edges_set))
        new = exact_min(n, edges)
        if new >= cur or rng.random() < pow(2.718, (new - cur) / temp):
            cur = new
            if new > best:
                best = new
                print(f"[n={n} it={it} t={int(time.time()-t0)}s] min-decomp={new} "
                      f"(bound {bound}) m={len(edges)}", flush=True)
                if new > bound:
                    # candidate counterexample -- reverify with long budget
                    ok, _ = hajos_ok(n, edges, k=bound, time_limit=3600, workers=8)
                    if ok is False:
                        print(f"*** COUNTEREXAMPLE n={n} edges={edges}", flush=True)
                        with open(f"counterexample_exact_n{n}.txt", "w") as f:
                            f.write(repr((n, edges)))
                        return
                    print(f"[n={n}] false alarm (long CP-SAT found decomposition)", flush=True)
                    cur = bound
        else:
            toggle(edges_set, tri)
        if it % 200 == 0:
            print(f"[n={n} it={it} t={int(time.time()-t0)}s] cur={cur} best={best} "
                  f"m={len(edges_set)} cache={len(CACHE)}", flush=True)
    print(f"[n={n}] done: {it} its, best min-decomp {best} vs bound {bound}", flush=True)

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 7)

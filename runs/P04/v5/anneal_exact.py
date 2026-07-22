"""Probe 3d: exact-score annealing. Score = exact minimum cycle-decomposition
size (CP-SAT, downward search from heuristic UB). Maximize score; a graph with
score > floor((n-1)/2) is a counterexample. Moves = triangle XOR, state kept
Eulerian with delta >= 6.
"""
import random
import sys
import time
from hajos import hajos_ok, is_eulerian, rlc_decompose
from anneal import toggle, valid

CACHE = {}

def exact_min(n, edges, tl=45):
    if edges in CACHE:
        return CACHE[edges]
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
    edges_set = set((u, v) for u in range(n) for v in range(u + 1, n))
    if (n - 1) % 2:
        for v in range(0, n, 2):
            edges_set.discard((v, v + 1))
    cur = exact_min(n, tuple(sorted(edges_set)))
    best = cur
    t0 = time.time()
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        temp = max(0.15, 1.5 * (1 - (time.time() - t0) / seconds))
        tri = rng.sample(range(n), 3)
        toggle(edges_set, tri)
        if not valid(n, edges_set):
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

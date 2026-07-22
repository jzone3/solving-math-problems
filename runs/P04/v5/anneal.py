"""Probe 3b: annealing over Eulerian graphs with delta >= 6, hunting graphs whose
minimum cycle decomposition exceeds floor((n-1)/2).

Move: XOR the three vertex-pairs of a random vertex triple (preserves all degree
parities). State kept Eulerian (connected, even degrees) with min degree >= 6
(minimum-counterexample profile, Fan-Xu / HNS Thm 2(i) modulo the single allowed
exceptional vertex, which we skip for search efficiency).

Score (hardness, maximized): failures of the RLC greedy heuristic to reach the
Hajos bound. Graphs the heuristic cannot settle get escalated to exact CP-SAT.
An infeasible CP-SAT at k = floor((n-1)/2) is a counterexample -> logged loudly.
"""
import random
import sys
import time
from itertools import combinations
from hajos import hajos_ok, is_eulerian, rlc_decompose

def score(n, edges, rng, tries=60):
    """Hardness score: (min cycles found by heuristic, fraction of tries above bound)."""
    bound = (n - 1) // 2
    best = len(edges)
    fails = 0
    for _ in range(tries):
        c = rlc_decompose(n, edges, tries=1, rng=rng)
        if c is None:
            fails += 1
            continue
        best = min(best, len(c))
        if len(c) > bound:
            fails += 1
    return (best - bound) * 1000 + fails

def toggle(edges_set, tri):
    a, b, c = tri
    for e in ((min(a,b),max(a,b)), (min(a,c),max(a,c)), (min(b,c),max(b,c))):
        if e in edges_set:
            edges_set.remove(e)
        else:
            edges_set.add(e)

def valid(n, edges_set):
    deg = [0] * n
    for u, v in edges_set:
        deg[u] += 1
        deg[v] += 1
    if any(d < 6 or d % 2 for d in deg):
        return False
    return is_eulerian(n, tuple(edges_set))

def run(n, seconds, seed):
    rng = random.Random(seed)
    bound = (n - 1) // 2
    # start: random even circulant-ish dense graph: K_n minus perfect matching-ish, or K_n for odd n
    edges_set = set((u, v) for u in range(n) for v in range(u + 1, n))
    if (n - 1) % 2:  # even n: K_n has odd degrees; remove a perfect matching
        for v in range(0, n, 2):
            edges_set.discard((v, v + 1))
    assert valid(n, edges_set), "bad start"
    cur = score(n, tuple(sorted(edges_set)), rng)
    best_seen = cur
    t0 = time.time()
    it = 0
    temp = 3.0
    escalated = set()
    while time.time() - t0 < seconds:
        it += 1
        temp = max(0.2, 3.0 * (1 - (time.time() - t0) / seconds))
        tri = rng.sample(range(n), 3)
        toggle(edges_set, tri)
        if not valid(n, edges_set):
            toggle(edges_set, tri)
            continue
        edges = tuple(sorted(edges_set))
        new = score(n, edges, rng)
        if new >= cur or rng.random() < pow(2.718, (new - cur) / temp):
            cur = new
            if new > best_seen:
                best_seen = new
                print(f"[n={n} it={it} t={int(time.time()-t0)}s] new best hardness {new} "
                      f"m={len(edges)}", flush=True)
            if new >= 1000 and edges not in escalated:  # heuristic never reached bound
                escalated.add(edges)
                print(f"[n={n}] ESCALATE to CP-SAT: m={len(edges)} edges={edges}", flush=True)
                ok, cyc = hajos_ok(n, edges, time_limit=1800)
                if ok is False:
                    print(f"*** COUNTEREXAMPLE n={n} edges={edges}", flush=True)
                    with open(f"counterexample_n{n}.txt", "w") as f:
                        f.write(repr((n, edges)))
                    return
                print(f"[n={n}] CP-SAT verdict: {ok} (True=satisfies Hajos)", flush=True)
        else:
            toggle(edges_set, tri)
    print(f"[n={n}] done: {it} iterations, best hardness {best_seen}, "
          f"escalations {len(escalated)}", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1])
    seconds = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(n, seconds, seed)

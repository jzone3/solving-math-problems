"""Probe 3g: mass random-walk sampling of Eulerian graphs with degrees in {6,8}
(the mixed-degree layer above the exhausted 6-regular one; full space ~10^10,
not exhaustible). Random triangle-XOR walk, greedy filter, CP-SAT escalation.
Usage: sampler.py <n> <seconds> <seed>
"""
import random
import sys
import time
from hajos import check_decomposition, hajos_ok, is_eulerian, rlc_decompose
from anneal import toggle

def valid(n, edges_set):
    deg = [0] * n
    for u, v in edges_set:
        deg[u] += 1
        deg[v] += 1
    if any(d not in (6, 8) for d in deg):
        return False
    return is_eulerian(n, tuple(edges_set))

def run(n, seconds, seed):
    rng = random.Random(seed)
    bound = (n - 1) // 2
    edges_set = set()
    for d in (1, 2, 3, 4):
        for v in range(n):
            edges_set.add((min(v, (v + d) % n), max(v, (v + d) % n)))
    assert valid(n, edges_set)
    t0 = time.time()
    tested = hard = 0
    seen = set()
    while time.time() - t0 < seconds:
        tri = rng.sample(range(n), 3)
        toggle(edges_set, tri)
        if not valid(n, edges_set):
            toggle(edges_set, tri)
            continue
        edges = tuple(sorted(edges_set))
        if edges in seen:
            continue
        seen.add(edges)
        tested += 1
        h = rlc_decompose(n, edges, tries=120, rng=rng)
        if h is not None and len(h) <= bound:
            check_decomposition(n, edges, h)
            if tested % 20000 == 0:
                print(f"[n={n}] tested={tested} hard={hard} t={int(time.time()-t0)}s",
                      flush=True)
            continue
        hard += 1
        ok, _ = hajos_ok(n, edges, time_limit=1200, workers=4)
        print(f"HARD n={n} m={len(edges)} cpSAT={ok}", flush=True)
        if ok is False:
            print(f"*** COUNTEREXAMPLE n={n} edges={edges}", flush=True)
            with open(f"counterexample_sampler_n{n}.txt", "w") as f:
                f.write(repr((n, edges)))
            return
    print(f"[n={n}] DONE tested={tested} hard={hard} t={int(time.time()-t0)}s", flush=True)

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

"""Direct random sampling + exact check: every sampled graph gets the exact CP-SAT
decision decompose <= k. Slower per graph but zero heuristic filtering — exact coverage.

Usage: python3 sample_exact.py N SECONDS [SEED]
"""
import json
import random
import sys
import time

import networkx as nx

from exact import decompose_leq_k
from search import random_even_graph


def main(n, seconds, seed):
    rng = random.Random(seed)
    k = (n - 1) // 2
    t0 = time.time()
    tested = 0
    stats = {}
    out = open(f"sample_exact_n{n}_seed{seed}.jsonl", "a")
    while time.time() - t0 < seconds:
        p = rng.uniform(0.55, 0.95)
        G = random_even_graph(n, p, rng)
        edges = [tuple(sorted(e)) for e in G.edges()]
        st, cyc = decompose_leq_k(n, edges, k, time_limit=300, workers=2)
        tested += 1
        stats[st] = stats.get(st, 0) + 1
        if st != "FEASIBLE":
            rec = {"n": n, "m": len(edges), "k": k, "exact": st,
                   "edges": [list(e) for e in edges]}
            if st == "INFEASIBLE":
                rec["COUNTEREXAMPLE"] = True
                print("!!! COUNTEREXAMPLE:", json.dumps(rec), flush=True)
            out.write(json.dumps(rec) + "\n")
            out.flush()
        if tested % 25 == 0:
            print(f"[n={n} t={time.time()-t0:.0f}s] tested={tested} stats={stats}",
                  flush=True)
    print(f"DONE n={n} seed={seed}: tested={tested} stats={stats}", flush=True)
    out.close()


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1)

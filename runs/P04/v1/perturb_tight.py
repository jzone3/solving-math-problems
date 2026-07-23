"""Structured probe around the tight family K_{2k+1} (which needs exactly k = (n-1)/2
cycles). Remove a random even subgraph (edge-disjoint union of random short cycles) from
K_n, keeping delta >= 6 and connectivity, and exact-check decompose <= k with CP-SAT.
Tightness suggests counterexamples, if any, live near extremal instances.

Usage: python3 perturb_tight.py N SECONDS [SEED]
"""
import json
import random
import sys
import time

import networkx as nx

from exact import decompose_leq_k


def random_even_removal(n, rng, max_edges=18):
    G = nx.complete_graph(n)
    budget = rng.randint(0, max_edges)
    removed = 0
    for _ in range(30):
        if removed >= budget:
            break
        L = rng.choice([3, 3, 4, 5])
        vs = rng.sample(range(n), L)
        cyc = [(vs[i], vs[(i + 1) % L]) for i in range(L)]
        if all(G.has_edge(u, v) for u, v in cyc):
            H = G.copy()
            H.remove_edges_from(cyc)
            if min(d for _, d in H.degree()) >= 6 and nx.is_connected(H):
                G = H
                removed += L
    return G


def main(n, seconds, seed):
    rng = random.Random(seed)
    k = (n - 1) // 2
    t0 = time.time()
    tested = 0
    stats = {}
    out = open(f"perturb_tight_n{n}_seed{seed}.jsonl", "a")
    while time.time() - t0 < seconds:
        G = random_even_removal(n, rng)
        edges = [tuple(sorted(e)) for e in G.edges()]
        st, _ = decompose_leq_k(n, edges, k, time_limit=600, workers=2)
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
        if tested % 50 == 0:
            print(f"[n={n} t={time.time()-t0:.0f}s] tested={tested} stats={stats}",
                  flush=True)
    print(f"DONE n={n} seed={seed}: tested={tested} stats={stats}", flush=True)
    out.close()


if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1)

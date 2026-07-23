"""Exhaustive sweep of connected 6-regular graphs (graph6 on stdin, e.g. from nauty-geng).

For each graph: try heuristic decompositions (Euler-split + greedy long-cycle peel with
early exit) up to MAXR restarts; if none achieves <= k = floor((n-1)/2) cycles, escalate
to the exact CP-SAT oracle. Logs survivors and any counterexample.

Usage: nauty-geng -c -d6 -D6 N res/mod | python3 regular_sweep.py N TAG
"""
import json
import random
import sys
import time

import networkx as nx

from exact import decompose_leq_k
from search import euler_split, greedy_peel

MAXR = 300


def g6_to_graph(line):
    return nx.from_graph6_bytes(line.strip().encode())


def main():
    n = int(sys.argv[1])
    tag = sys.argv[2]
    k = (n - 1) // 2
    rng = random.Random(12345)
    t0 = time.time()
    total = 0
    escalated = 0
    out = open(f"regular_sweep_n{n}_{tag}.jsonl", "a")
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        total += 1
        G = g6_to_graph(line)
        ok = False
        for r in range(MAXR):
            c = greedy_peel(G, rng) if r % 2 == 0 else euler_split(G, rng)
            if c <= k:
                ok = True
                break
        if not ok:
            escalated += 1
            edges = [tuple(sorted(e)) for e in G.edges()]
            st, cyc = decompose_leq_k(n, edges, k, time_limit=1200, workers=2)
            rec = {"n": n, "k": k, "g6": line, "exact": st}
            if st == "INFEASIBLE":
                rec["COUNTEREXAMPLE"] = True
                print("!!! COUNTEREXAMPLE:", json.dumps(rec), flush=True)
            out.write(json.dumps(rec) + "\n")
            out.flush()
        if total % 20000 == 0:
            print(f"[{tag}] total={total} escalated={escalated} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"DONE [{tag}] total={total} escalated={escalated} t={time.time()-t0:.0f}s",
          flush=True)
    out.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simulated annealing over Z_k lift voltages of a 4-regular 4-chromatic base
(Brinkmann/Chvatal). Objective: keep girth>=6 (zero-voltage short closed walks
forbidden) and maximize difficulty of 3-coloring measured by best (minimum)
conflict count reached by Tabucol within a fixed budget. A state where Tabucol
cannot reach 0 conflicts is verified exactly with SAT; UNSAT => WITNESS."""
import random, sys, networkx as nx
from pysat.solvers import Glucose4
from lift_search import BASES, lift, three_colorable
from lift_search2 import closed_walks

def tabucol(adj, n, iters, rng):
    """Return best conflict count found (3 colors)."""
    col = [rng.randrange(3) for _ in range(n)]
    conf = 0
    confl_of = [0]*n
    for v in range(n):
        c = sum(1 for u in adj[v] if col[u] == col[v])
        confl_of[v] = c; conf += c
    conf //= 2
    best = conf
    tabu = {}
    it = 0
    while it < iters and best > 0:
        it += 1
        # pick random conflicted vertex
        cand = [v for v in range(n) if confl_of[v] > 0]
        if not cand: break
        v = rng.choice(cand)
        # best move
        counts = [0,0,0]
        for u in adj[v]: counts[col[u]] += 1
        bestc = None; bestdelta = None
        for c in range(3):
            if c == col[v]: continue
            if tabu.get((v,c), 0) > it and counts[c] >= counts[col[v]]: continue
            d = counts[c] - counts[col[v]]
            if bestdelta is None or d < bestdelta:
                bestdelta = d; bestc = c
        if bestc is None: continue
        old = col[v]
        tabu[(v, old)] = it + 10 + rng.randrange(10)
        # update
        for u in adj[v]:
            if col[u] == old: confl_of[u] -= 1; confl_of[v] -= 1; conf -= 1
            if col[u] == bestc: confl_of[u] += 1; confl_of[v] += 1; conf += 1
        col[v] = bestc
        if conf < best: best = conf
    return best, it

def hardness(adj, N, rng, budget=3000, runs=3):
    """Average iterations Tabucol needs to 3-color (capped); higher = harder."""
    tot = 0
    for _ in range(runs):
        best, it = tabucol(adj, N, budget, rng)
        tot += budget if best > 0 else it
    return tot / runs

def build_adj(G, volt_list, edges, k):
    n = G.number_of_nodes()
    N = n*k
    adj = [[] for _ in range(N)]
    for i, (u, v) in enumerate(edges):
        t = volt_list[i]
        for j in range(k):
            a = u + n*j; b = v + n*((j+t) % k)
            adj[a].append(b); adj[b].append(a)
    return adj, N

def zero_walks(volt_list, walks, k):
    return sum(1 for w in walks if sum(s*volt_list[i] for i, s in w) % k == 0)

def main():
    seed = int(sys.argv[1]); base = sys.argv[2]; k = int(sys.argv[3])
    rng = random.Random(seed)
    G = BASES[base]
    edges, walks = closed_walks(G)
    m = len(edges)
    # init: random girth-6-valid voltage
    while True:
        volt = [rng.randrange(k) for _ in range(m)]
        if zero_walks(volt, walks, k) == 0: break
    adj, N = build_adj(G, volt, edges, k)
    budget = 3000
    cur = hardness(adj, N, rng, budget)
    print(f"start base={base} k={k} n={N} hardness={cur}", flush=True)
    T = 1.0
    it = 0
    import math
    while True:
        it += 1
        i = rng.randrange(m); old = volt[i]
        new = rng.randrange(k)
        if new == old: continue
        volt[i] = new
        if zero_walks(volt, walks, k) > 0:
            volt[i] = old; continue
        adj, N = build_adj(G, volt, edges, k)
        val = hardness(adj, N, rng, budget)
        if val >= cur or rng.random() < math.exp((val - cur)/(max(T,1e-3)*budget*0.02)):
            cur = val
            if val >= budget:
                # exact check
                Gs = nx.Graph()
                for a in range(N):
                    for b in adj[a]:
                        if a < b: Gs.add_edge(a, b)
                if not three_colorable(Gs):
                    print(f"WITNESS base={base} k={k} volt={volt}", flush=True)
                    nx.write_adjlist(Gs, f"/home/ubuntu/p20/sms/WITNESS_anneal_{base}_{k}_{seed}.adjlist")
                    return
        else:
            volt[i] = old
        T *= 0.99995
        if it % 500 == 0:
            print(f"it={it} cur={cur} T={T:.3f}", flush=True)

if __name__ == "__main__":
    main()

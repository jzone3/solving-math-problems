#!/usr/bin/env python3
"""Anneal in 5-regular LCF(r,s) space (where 4-chromatic girth-6 graphs are known
to exist, e.g. EG66) using tabucol-hardness objective; exact SAT check on capped
states. Each 4-chromatic hit is saved as a CEGAR target for the Delta<=4 reduction."""
import random, sys, math, networkx as nx
from pysat.solvers import Glucose4
from anneal_lift import tabucol, hardness
from lcf5_search import girth_at_least_6, three_colorable, sample

def adj_lists(adjsets):
    return adjsets  # already lists

def main():
    seed = int(sys.argv[1]); r = int(sys.argv[2]); s = int(sys.argv[3])
    rng = random.Random(seed)
    n = r*s
    budget = 3000
    # init with a girth-6 sample
    while True:
        res = sample(rng, r, s)
        if res is None: continue
        adj, chords = res
        if girth_at_least_6(adj, n): break
    def build(chs):
        a = [set() for _ in range(n)]
        for v in range(n):
            a[v].add((v+1) % n); a[(v+1) % n].add(v)
        for (i, t) in chs:
            for j in range(0, n, r):
                x = (i+j) % n; y = (i+j+t) % n
                if x == y or y in a[x]: return None
                a[x].add(y); a[y].add(x)
        for v in range(n):
            if len(a[v]) != 5: return None
        return [sorted(z) for z in a]
    cur = hardness(adj, n, rng, budget)
    print(f"start r={r} s={s} n={n} hardness={cur}", flush=True)
    T = 1.0
    it = 0
    while True:
        it += 1
        # move: change offset of one chord by multiple of r (preserves class pairing)
        ci = rng.randrange(len(chords))
        i, t = chords[ci]
        nt = t + r*rng.randrange(1, s)
        nt %= n
        if nt % n in (0, 1, n-1): continue
        new = list(chords); new[ci] = (i, nt)
        a2 = build(new)
        if a2 is None: continue
        if not girth_at_least_6(a2, n): continue
        val = hardness(a2, n, rng, budget)
        if val >= cur or rng.random() < math.exp((val-cur)/(max(T, 1e-3)*budget*0.02)):
            chords = new; cur = val
            if val >= budget:
                if not three_colorable(a2, n):
                    print(f"HIT 4-chromatic 5-regular girth6 n={n} chords={chords}", flush=True)
                    G = nx.Graph()
                    for v in range(n):
                        for u in a2[v]:
                            if u > v: G.add_edge(v, u)
                    nx.write_adjlist(G, f"/home/ubuntu/p20/sms/HIT5_{n}_{seed}.adjlist")
                    return
        T *= 0.99995
        if it % 500 == 0:
            print(f"it={it} cur={cur} T={T:.3f}", flush=True)

if __name__ == "__main__":
    main()

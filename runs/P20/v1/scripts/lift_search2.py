#!/usr/bin/env python3
"""Fast cyclic-lift search: precompute non-backtracking closed walks of length
3..5 in the base; a Z_k lift has girth>=6 iff every such walk has nonzero net
voltage mod k. Only then build lift and SAT-check 3-colorability."""
import random, sys, networkx as nx
from pysat.solvers import Glucose4
from lift_search import BASES, lift, three_colorable

def closed_walks(G, maxlen=5):
    """Non-backtracking closed walks up to maxlen, as signed edge sequences.
    Return list of walks; each walk is list of (edge_index, sign)."""
    edges = list(G.edges())
    eid = {}
    for i, (u, v) in enumerate(edges):
        eid[(u, v)] = (i, 1); eid[(v, u)] = (i, -1)
    walks = []
    nodes = list(G.nodes())
    def dfs(start, cur, prev, path, depth):
        for w in G.neighbors(cur):
            if w == prev: continue
            step = eid[(cur, w)]
            if w == start and depth + 1 >= 3:
                walks.append(path + [step])
                continue
            if depth + 1 < maxlen and (w != start):
                dfs(start, w, cur, path + [step], depth + 1)
    for s in nodes:
        dfs(s, s, None, [], 0)
    # dedupe: canonical form
    seen = set(); out = []
    for w in walks:
        key = frozenset(((i, s) for i, s in w)), len(w)
        k2 = min(tuple(w[i:] + w[:i]) for i in range(len(w)))
        k3 = tuple(sorted(w))
        kk = (len(w), k3)
        if kk in seen: continue
        seen.add(kk); out.append(w)
    return edges, out

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rng = random.Random(seed)
    prep = {}
    for name, G in BASES.items():
        prep[name] = (G,) + tuple(closed_walks(G))
    names = list(BASES)
    tried = g6 = 0
    while True:
        name = rng.choice(names)
        G, edges, walks = prep[name]
        k = rng.choice([5,6,7,8,9,10,11,12,13,14,15,16])
        volt = [rng.randrange(k) for _ in edges]
        ok = True
        for w in walks:
            if sum(s*volt[i] for i, s in w) % k == 0:
                ok = False; break
        tried += 1
        if not ok: continue
        vd = {e: volt[i] for i, e in enumerate(edges)}
        H = lift(G, vd, k)
        if not nx.is_connected(H): continue
        g6 += 1
        assert nx.girth(H) >= 6
        if not three_colorable(H):
            print(f"WITNESS base={name} k={k} volt={volt}", flush=True)
            nx.write_adjlist(H, f"/home/ubuntu/p20/sms/WITNESS_lift2_{seed}_{name}_{k}.adjlist")
        if g6 % 1000 == 0:
            print(f"seed={seed} tried={tried} g6={g6}", flush=True)

if __name__ == "__main__":
    main()

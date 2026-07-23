#!/usr/bin/env python3
"""Randomized LCF(r,s)-style search for a 4-regular girth>=6 non-3-colorable graph.

Graph on n=r*s vertices. Row i (0<=i<r) has offset entries; entry t in row i
adds edges (i+r*j, i+r*j+t mod n) for j=0..s-1.
We fix entry 1 in every row (Hamiltonian cycle) and add one extra offset t_i
per row such that every class is the target of exactly one chord
(i -> (i+t_i) mod r is a bijection), giving a 4-regular graph.
Filter girth>=6 exactly, then SAT-check 3-colorability (Glucose4).
Witnesses printed and saved.
"""
import random, sys, itertools
from pysat.solvers import Glucose4

def build(n, r, ts):
    adj = [set() for _ in range(n)]
    ok = True
    # hamiltonian cycle
    for v in range(n):
        adj[v].add((v+1) % n); adj[(v+1) % n].add(v)
    for i, t in enumerate(ts):
        for j in range(0, n, r):
            a = (i + j) % n; b = (i + j + t) % n
            if a == b or b in adj[a]:
                return None
            adj[a].add(b); adj[b].add(a)
    for v in range(n):
        if len(adj[v]) != 4:
            return None
    return [sorted(x) for x in adj]

def girth_at_least_6(adj, n):
    # BFS from each vertex up to depth 2; any cycle of length<=5 shows up as
    # an edge between two vertices at distance <=2 from root (careful check via BFS shortest cycle)
    for root in range(n):
        dist = {root: 0}
        parent = {root: -1}
        frontier = [root]
        d = 0
        while frontier and d < 2:
            nxt = []
            for u in frontier:
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = d+1; parent[w] = u; nxt.append(w)
            frontier = nxt; d += 1
        # any edge between two visited vertices u,w with dist[u]+dist[w]+1 <=5 and not tree edge
        for u in dist:
            for w in adj[u]:
                if w in dist and parent.get(w) != u and parent.get(u) != w and u < w:
                    if dist[u] + dist[w] + 1 <= 5:
                        return False
    return True

def three_colorable(adj, n):
    s = Glucose4()
    var = lambda v, c: 3*v + c + 1
    for v in range(n):
        s.add_clause([var(v,0), var(v,1), var(v,2)])
    for v in range(n):
        for u in adj[v]:
            if u > v:
                for c in range(3):
                    s.add_clause([-var(v,c), -var(u,c)])
    # symmetry: vertex 0 color 0, vertex 1 (neighbor) color 1
    s.add_clause([var(0,0)]); s.add_clause([var(1,1)])
    res = s.solve()
    s.delete()
    return res

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rng = random.Random(seed)
    combos = []
    for r in range(2, 13):
        for s in range(6, 40):
            n = r*s
            if 30 <= n <= 130:
                combos.append((r, s))
    tried = girth6 = 0
    while True:
        r, s = rng.choice(combos)
        n = r*s
        # random target bijection on classes and offsets realizing it
        perm = list(range(r)); rng.shuffle(perm)
        ts = []
        okp = True
        for i in range(r):
            delta = (perm[i] - i) % r
            # offset t = delta + r*m, choose m random, avoid |t| in {0,1,n-1}
            cand = [delta + r*m for m in range(0, s)]
            cand = [t for t in cand if t % n not in (0, 1, n-1)]
            if not cand: okp = False; break
            ts.append(rng.choice(cand))
        if not okp: continue
        adj = build(n, r, ts)
        if adj is None: continue
        tried += 1
        if not girth_at_least_6(adj, n): continue
        girth6 += 1
        if not three_colorable(adj, n):
            print(f"WITNESS n={n} r={r} s={s} ts={ts}", flush=True)
            with open(f"/home/ubuntu/p20/sms/WITNESS_lcf_{seed}.txt", "a") as f:
                f.write(f"n={n} r={r} s={s} ts={ts}\nadj={adj}\n")
        if girth6 % 2000 == 0:
            print(f"seed={seed} tried={tried} girth6={girth6}", flush=True)

if __name__ == "__main__":
    main()

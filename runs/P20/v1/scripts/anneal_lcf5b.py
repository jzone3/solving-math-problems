#!/usr/bin/env python3
"""Two-phase annealing in 5-regular LCF(6,s) space.
Phase 1: minimize number of short cycles (girth<6 violations) to reach girth>=6.
Phase 2: maximize tabucol hardness; exact SAT check at cap; save distinct hits.
Seeds: EG66 chords (s=11) or random. Usage: anneal_lcf5b.py seed s [kick]"""
import random, sys, math, networkx as nx
from pysat.solvers import Glucose4
from anneal_lift import tabucol, hardness
from lcf5_search import three_colorable

R = 6
EG66_CHORDS = [(0,6),(1,9),(1,14),(1,23),(2,26),(2,33),(3,18),(4,10),(5,18)]

def build(chs, n):
    a = [set() for _ in range(n)]
    for v in range(n):
        a[v].add((v+1) % n); a[(v+1) % n].add(v)
    for (i, t) in chs:
        for j in range(0, n, R):
            x = (i+j) % n; y = (i+j+t) % n
            if x == y or y in a[x]: return None
            a[x].add(y); a[y].add(x)
    for v in range(n):
        if len(a[v]) != 5: return None
    return [sorted(z) for z in a]

def short_cycles(adj, n):
    """count vertices on cycles of length<6 (proxy)."""
    bad = 0
    for root in range(n):
        dist = {root: 0}; parent = {root: -1}; frontier = [root]; d = 0
        while frontier and d < 2:
            nxt = []
            for u in frontier:
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = d+1; parent[w] = u; nxt.append(w)
            frontier = nxt; d += 1
        for u in dist:
            for w in adj[u]:
                if w in dist and parent.get(w) != u and parent.get(u) != w and u < w:
                    if dist[u] + dist[w] + 1 <= 5:
                        bad += 1
    return bad

def rand_chords(rng, n):
    """random 9 chords forming 3 slots/class: use class-pairing of EG66 topology."""
    out = []
    for (i, t0) in EG66_CHORDS:
        delta = t0 % R
        t = delta + R*rng.randrange(1, n//R)
        out.append((i, t % n))
    return out

def main():
    seed = int(sys.argv[1]); s = int(sys.argv[2]); kick = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    rng = random.Random(seed)
    n = R*s
    budget = 50*n
    seen = set()
    def wl(a2):
        G = nx.Graph()
        for v in range(n):
            for u in a2[v]:
                if u > v: G.add_edge(v, u)
        return nx.weisfeiler_lehman_graph_hash(G, iterations=4), G
    # known: EG66
    eg = build(EG66_CHORDS, 66)
    if eg:
        seen.add(nx.weisfeiler_lehman_graph_hash(
            nx.Graph([(v,u) for v in range(66) for u in eg[v] if u>v]), iterations=4))
    if s == 11:
        chords = list(EG66_CHORDS)
        for _ in range(kick):
            ci = rng.randrange(9); i, t = chords[ci]
            chords[ci] = (i, (t + R*rng.randrange(1, s)) % n)
    else:
        chords = rand_chords(rng, n)
    # phase 1: minimize short cycles
    def sc_of(chs):
        a = build(chs, n)
        return (10**9 if a is None else short_cycles(a, n)), a
    cur_sc, adj = sc_of(chords)
    it = 0
    while cur_sc > 0:
        it += 1
        ci = rng.randrange(9); i, t = chords[ci]
        new = list(chords); new[ci] = (i, (t + R*rng.randrange(1, s)) % n)
        v, a2 = sc_of(new)
        if v <= cur_sc or rng.random() < 0.02:
            chords, cur_sc, adj = new, v, a2
        if it % 2000 == 0:
            print(f"phase1 it={it} short={cur_sc}", flush=True)
        if it > 200000:
            print("phase1 stuck", flush=True); return
    print(f"phase1 done it={it} n={n}", flush=True)
    cur = hardness(adj, n, rng, budget)
    print(f"phase2 start hardness={cur}", flush=True)
    T = 1.0; it = 0; hits = 0
    while True:
        it += 1
        ci = rng.randrange(9); i, t = chords[ci]
        new = list(chords); new[ci] = (i, (t + R*rng.randrange(1, s)) % n)
        a2 = build(new, n)
        if a2 is None or short_cycles(a2, n) > 0: continue
        val = hardness(a2, n, rng, budget)
        if val >= cur or rng.random() < math.exp((val-cur)/(max(T, 1e-3)*budget*0.02)):
            chords, cur, adj = new, val, a2
            if val >= budget:
                h, G = wl(a2)
                fresh = h not in seen
                if fresh:
                    seen.add(h)
                    if not three_colorable(a2, n):
                        hits += 1
                        print(f"HIT n={n} chords={chords}", flush=True)
                        nx.write_adjlist(G, f"/home/ubuntu/p20/sms/HIT5_{n}_{seed}_{hits}.adjlist")
                # kick regardless (escape basin / avoid plateau on seen or colorable states)
                for _ in range(10):
                    ci = rng.randrange(9); i, t = chords[ci]
                    chords[ci] = (i, (t + R*rng.randrange(1, s)) % n)
                a3 = build(chords, n)
                tries = 0
                while a3 is None or short_cycles(a3, n) > 0:
                    ci = rng.randrange(9); i, t = chords[ci]
                    chords[ci] = (i, (t + R*rng.randrange(1, s)) % n)
                    a3 = build(chords, n)
                    tries += 1
                    if tries > 100000:
                        print("rekick stuck", flush=True); return
                adj = a3; cur = hardness(adj, n, rng, budget); T = 1.0
        T *= 0.99995
        if it % 500 == 0:
            print(f"phase2 it={it} cur={cur} T={T:.3f} hits={hits}", flush=True)

if __name__ == "__main__":
    main()

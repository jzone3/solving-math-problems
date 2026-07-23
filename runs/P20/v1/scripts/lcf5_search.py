#!/usr/bin/env python3
"""Random search for 5-regular girth-6 non-3-colorable LCF(r,s) graphs (EG-style).

Each class i in 0..r-1 gets offsets: 1,-1 (cycle) plus chords. Chord structure:
choose a 3-regular multigraph on classes with Z offsets; here we sample by
choosing 3 chord slots per class consistently: repeatedly pick pair of classes
(i, i') (possibly equal) with remaining slots and an offset t with t ≡ i'-i (mod r).
Offsets t=+-1,0 excluded; self-pair with t = n/2 allowed (perfect-matching orbit).
Then exact girth>=6 filter and SAT 3-colorability. Hits (non-3-col) are saved
as CEGAR targets are unnecessary: 5-regular hit -> run matching cegar on it.
"""
import random, sys
from pysat.solvers import Glucose4

def girth_at_least_6(adj, n):
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
    s.add_clause([var(0,0)])
    res = s.solve(); s.delete(); return res

def sample(rng, r, s):
    n = r * s
    slots = {i: 3 for i in range(r)}
    chords = []  # (class i, offset t): orbit edges (i+rj, i+rj+t)
    guard = 0
    while any(slots.values()):
        guard += 1
        if guard > 200: return None
        avail = [i for i in range(r) if slots[i] > 0]
        i = rng.choice(avail)
        j = rng.choice(avail)
        t = rng.randrange(2, n-1)
        if t % n in (0, 1, n-1): continue
        if (t - (j - i)) % r != 0: 
            t = t - (t - (j - i)) % r
            if t < 2 or t % n in (0,1,n-1): continue
        if i == j and (2*t) % n == 0:
            # perfect matching orbit uses only 1 slot... actually each vertex of
            # class i gets one edge; uses 1 slot of class i
            if slots[i] < 1: continue
            slots[i] -= 1; chords.append((i, t)); continue
        if i == j:
            if slots[i] < 2: continue
            slots[i] -= 2; chords.append((i, t)); continue
        if slots[i] < 1 or slots[j] < 1: continue
        slots[i] -= 1; slots[j] -= 1; chords.append((i, t))
    adj = [set() for _ in range(n)]
    for v in range(n):
        adj[v].add((v+1) % n); adj[(v+1) % n].add(v)
    for (i, t) in chords:
        for j in range(0, n, r):
            a = (i + j) % n; b = (i + j + t) % n
            if a == b or b in adj[a]: return None
            adj[a].add(b); adj[b].add(a)
    for v in range(n):
        if len(adj[v]) != 5: return None
    return [sorted(x) for x in adj], chords

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rng = random.Random(seed)
    combos = [(r, s) for r in (2,3,4,6) for s in range(8, 30) if 40 <= r*s <= 140]
    tried = g6 = hits = 0
    while True:
        r, s = rng.choice(combos)
        n = r*s
        res = sample(rng, r, s)
        if res is None: continue
        adj, chords = res
        tried += 1
        if not girth_at_least_6(adj, n): continue
        g6 += 1
        if not three_colorable(adj, n):
            hits += 1
            print(f"HIT n={n} r={r} s={s} chords={chords}", flush=True)
            with open(f"/home/ubuntu/p20/sms/HIT5_{seed}.txt", "a") as f:
                f.write(f"n={n} r={r} s={s} chords={chords}\nadj={adj}\n")
        if g6 % 5000 == 0:
            print(f"seed={seed} tried={tried} girth6={g6} hits={hits}", flush=True)

if __name__ == "__main__":
    main()

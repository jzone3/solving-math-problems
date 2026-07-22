#!/usr/bin/env python3
"""Cross-check the C HC counter against a brute-force permutation counter
on small random 4-regular graphs (n=8..12) plus K5."""
import itertools, random, subprocess, sys

def brute_hc(n, edges):
    adj = [[False]*n for _ in range(n)]
    for a,b in edges: adj[a][b]=adj[b][a]=True
    cnt = 0
    for perm in itertools.permutations(range(1,n)):
        if perm[0] > perm[-1]:  # each undirected cycle once
            continue
        ok = adj[0][perm[0]] and adj[perm[-1]][0]
        if ok:
            for i in range(len(perm)-1):
                if not adj[perm[i]][perm[i+1]]: ok=False; break
        if ok: cnt += 1
    return cnt

def c_count(n, edges):
    inp = f"{n}\n" + "\n".join(f"{a} {b}" for a,b in edges)
    out = subprocess.run(["./search","count"], input=inp, capture_output=True, text=True)
    return int(out.stdout.strip())

def rand_4reg(n, rng):
    while True:
        edges = set((i,(i+1)%n) for i in range(n))
        edges = set((min(a,b),max(a,b)) for a,b in edges)
        p = list(range(n)); rng.shuffle(p)
        e2 = set((min(p[i],p[(i+1)%n]), max(p[i],p[(i+1)%n])) for i in range(n))
        if e2 & edges: continue
        return sorted(edges|e2)

rng = random.Random(12345)
k5 = [(a,b) for a in range(5) for b in range(a+1,5)]
b, c = brute_hc(5,k5), c_count(5,k5)
print("K5:", b, c); assert b==c==12

for n in (8,10,11,12):
    for t in range(5):
        e = rand_4reg(n,rng)
        b, c = brute_hc(n,e), c_count(n,e)
        status = "OK" if b==c else "MISMATCH"
        print(f"n={n} trial={t}: brute={b} c={c} {status}")
        assert b==c
print("ALL PASS")

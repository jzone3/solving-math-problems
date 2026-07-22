"""V4 escalation: much larger exact grids.

  A. Kneser up to n=100, Johnson up to n=60, Hamming q^d <= 1e9 (+complements).
  B. Complete multipartite: all partitions n <= 50.
  C. Parameterized union-join grids: (a*K_p u E_q) v K_r / v E_s with big ranges;
     (a*K_p u b*K_q) v K_r; Kneser v K_r etc.  Spectra have O(1) distinct values,
     so worst_fast is O(1) per instance -> millions of instances exact.
"""
import sys, time, itertools
from fractions import Fraction
sys.path.insert(0, '.')
from spectra import (Spec, empty_graph, complete_graph, join, complement, kneser,
                     johnson, hamming, complete_multipartite, disjoint_union, worst_fast)

t0 = time.time()
gmin = [None]
cnt = [0]

def rec(name, spec):
    d, t = worst_fast(spec)
    cnt[0] += 1
    if d < 0:
        print(f"!!! COUNTEREXAMPLE {name} n={spec.n} t={t} deficit={d}", flush=True)
    if gmin[0] is None or d < gmin[0][0]:
        gmin[0] = (d, name, spec.n, spec.m, t)
    return d

def clique_union(a, p):
    """a disjoint copies of K_p"""
    if p == 1:
        return empty_graph(a)
    return Spec(a * p, a * (p * (p - 1) // 2),
                [(Fraction(p), a * (p - 1)), (Fraction(0), a)])

# A
for nn in range(5, 101):
    for k in range(2, nn // 2 + 1):
        sp = kneser(nn, k); rec(f"K({nn},{k})", sp); rec(f"cK({nn},{k})", complement(sp))
for nn in range(4, 61):
    for k in range(2, nn // 2 + 1):
        sp = johnson(nn, k); rec(f"J({nn},{k})", sp); rec(f"cJ({nn},{k})", complement(sp))
for d in range(2, 31):
    for q in range(2, 21):
        if q ** d > 10 ** 9: continue
        sp = hamming(d, q); rec(f"H({d},{q})", sp); rec(f"cH({d},{q})", complement(sp))
print(f"A done {cnt[0]} specs {time.time()-t0:.0f}s min={gmin[0]}", flush=True)

# B
def partitions(n, maxp=None):
    if maxp is None: maxp = n
    if n == 0:
        yield []; return
    for p in range(min(n, maxp), 0, -1):
        for rest in partitions(n - p, p):
            yield [p] + rest

for n in range(41, 51):
    for parts in partitions(n):
        if len(parts) < 2: continue
        rec(f"K{parts}", complete_multipartite(parts))
print(f"B done {cnt[0]} specs {time.time()-t0:.0f}s min={gmin[0]}", flush=True)

# C. big parameterized grids
for p in range(1, 26):
    for a in range(1, 26):
        for q in range(0, 16):
            g = clique_union(a, p)
            if q: g = disjoint_union(g, empty_graph(q))
            for r in range(1, 51):
                rec(f"({a}K{p}uE{q})vK{r}", join(g, complete_graph(r)))
                rec(f"c[({a}K{p}uE{q})vK{r}]", complement(join(g, complete_graph(r))))
print(f"C1 done {cnt[0]} specs {time.time()-t0:.0f}s min={gmin[0]}", flush=True)

for p in range(1, 16):
    for a in range(1, 11):
        for pq in range(1, 16):
            for b in range(1, 11):
                g = disjoint_union(clique_union(a, p), clique_union(b, pq))
                for r in range(1, 31):
                    rec(f"({a}K{p}u{b}K{pq})vK{r}", join(g, complete_graph(r)))
print(f"C2 done {cnt[0]} specs {time.time()-t0:.0f}s min={gmin[0]}", flush=True)

# Kneser / Johnson joined with cliques and empties (dense middle-t stress)
fams = []
for nn in range(5, 26):
    for k in range(2, nn // 2 + 1):
        fams.append((f"K({nn},{k})", kneser(nn, k)))
        fams.append((f"J({nn},{k})", johnson(nn, k)))
for nm, sp in fams:
    for r in range(1, 61):
        rec(f"{nm}vK{r}", join(sp, complete_graph(r)))
        rec(f"{nm}vE{r}", join(sp, empty_graph(r)))
        rec(f"c{nm}vK{r}", join(complement(sp), complete_graph(r)))
        rec(f"c{nm}vE{r}", join(complement(sp), empty_graph(r)))
print(f"C3 done {cnt[0]} specs {time.time()-t0:.0f}s min={gmin[0]}", flush=True)

print(f"TOTAL {cnt[0]} specs, GLOBAL MIN deficit = {gmin[0]}")

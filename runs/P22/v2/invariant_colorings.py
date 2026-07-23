#!/usr/bin/env python3
"""Restricted arrowing tests: colorings of E(G127) invariant under a chosen
subgroup H <= Aut(G127).

Aut(G127) contains Z127 (translations) semidirect Z42 (Stab(0) = mults by
cubic residues, cyclic). Any subgroup with nontrivial translation part
contains all of Z127 (127 prime) => coloring is circulant (excluded
exhaustively by circulant_colorings.py). Any other nontrivial subgroup is,
by Schur–Zassenhaus conjugacy (gcd(127,42)=1), conjugate to a subgroup of the
cyclic Stab(0); and conjugate subgroups give isomorphic restricted problems.
Hence: if for each prime p | 42 (p = 2, 3, 7) no coloring invariant under the
order-p subgroup of Stab(0) avoids mono triangles, then every witness of
G127 -/-> (3,3)^e has trivial stabilizer in Aut(G127).

For subgroup H = <x -> g*x> we collapse edge variables to H-orbits and emit
the collapsed CNF (SAT <=> an H-invariant good coloring exists).
Usage: invariant_colorings.py <order>   (order | 42)
"""
import sys, os

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
Cset = set(C)

# generator of the cyclic group of cubic residues (order 42)
def mult_order(a):
    x, k = a, 1
    while x != 1:
        x = x * a % p; k += 1
    return k
gen42 = next(a for a in C if mult_order(a) == 42)

order = int(sys.argv[1])
assert 42 % order == 0 and order > 1
g = pow(gen42, 42 // order, p)
assert mult_order(g) == order

adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)
edges = [(u, v) for u in range(p) for v in adj[u] if u < v]

def canon(e):
    u, v = e
    return (u, v) if u < v else (v, u)

# H-orbits of edges
orbit = {}
norb = 0
for e in edges:
    if e in orbit:
        continue
    norb += 1
    x = e
    while True:
        orbit[x] = norb
        x = canon((x[0] * g % p, x[1] * g % p))
        if x == e:
            break

cls = []
seen = set()
for (u, v) in edges:
    for w in adj[u] & adj[v]:
        if w > v:
            a, b, c = orbit[(u, v)], orbit[canon((u, w))], orbit[canon((v, w))]
            key = tuple(sorted((a, b, c)))
            if key in seen:
                continue
            seen.add(key)
            if a == b == c:
                # orbit-monochromatic triangle: both clauses unsatisfiable
                print(f"order {order}: triangle within a single edge-orbit -> "
                      f"no H-invariant good coloring exists (trivially UNSAT)")
                cls = [(a,), (-a,)]
                break
            cls.append(tuple({a, b, c}))
            cls.append(tuple(-x for x in {a, b, c}))
    else:
        continue
    break

out = f"inv_{order}.cnf"
with open(out, "w") as f:
    f.write(f"p cnf {norb} {len(cls)}\n")
    for cl in cls:
        f.write(" ".join(map(str, cl)) + " 0\n")
print(f"order {order}: generator g={g}, {norb} edge-orbits, {len(cls)} clauses -> {out}")

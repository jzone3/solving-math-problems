"""exp10: sanity scan for Lemma X.

Lemma X (proved in PROOF_J.md): if a connected graph G contains an edge f
with (s, z1, zs) = (3, 4, 21) and rho0(f) <= 14, then G = T1 (the n=9
spider `HkE?K?@`: center degree 4, four legs of length 2).

Scan: all connected graphs n <= 9 and all trees n <= 17; report every
occurrence of the tuple, with its rho0 and the graph.
"""
import itertools
from common import geng, gentreeg, g6_adj, edge_env

found = []
gens = itertools.chain(
    itertools.chain.from_iterable(geng(n) for n in range(3, 10)),
    itertools.chain.from_iterable(gentreeg(n) for n in range(3, 18)),
)
tot = 0
for g6 in gens:
    A = g6_adj(g6)
    d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
    tot += 1
    for a in range(len(E)):
        if (s[a], z1[a], zs[a]) == (3, 4, 21) and rho0[a] <= 14:
            found.append((g6, a, str(rho0[a])))
print("graphs scanned:", tot)
print("occurrences of (3,4,21) with rho0<=14:", len(found))
for f in found:
    print(" ", f)

#!/usr/bin/env python3
"""Generate anneal_in.txt for anneal.c (C7 orbit data), plus decode helper."""
import sys
from search_sat import perm_order7, close_group, edge_orbits, cycle_orbit_reps, N

group = close_group(perm_order7())
orbits, seen = edge_orbits(group)
tri = cycle_orbit_reps(group, seen, 3)
c4 = cycle_orbit_reps(group, seen, 4)
vreps = [0, 7, 14, 21, 28, 35, 42, 49]
with open('anneal_in.txt', 'w') as f:
    f.write(f"{len(tri)} {len(c4)}\n")
    for t in tri:
        f.write(" ".join(map(str, t)) + "\n")
    for q in c4:
        f.write(" ".join(map(str, q)) + "\n")
    for v in vreps:
        w = [0]*len(orbits)
        for u in range(N):
            if u == v:
                continue
            w[seen[(min(u, v), max(u, v))]] += 1
        f.write(" ".join(map(str, w)) + "\n")
print("wrote anneal_in.txt:", len(tri), "tri,", len(c4), "c4")

if len(sys.argv) > 2 and sys.argv[1] == 'decode':
    # decode anneal_out-style file (orbit color per line) to edge-list witness
    out = sys.argv[3]
    with open(sys.argv[2]) as f, open(out, 'w') as g:
        for line in f:
            o, c = map(int, line.split())
            if c < 0:
                continue
            for (u, v) in orbits[o]:
                g.write(f"{c} {u} {v}\n")
    print("decoded to", out)

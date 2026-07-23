#!/usr/bin/env python3
"""Decode a SAT model (kissat 'v' lines) into an edge-list witness.

Usage: decode_model.py <kissat_output> <map_file> <out_witness>
map_file lines: <var> <orbit> <color>  (from DIMACS=... search_sat.py run)
Witness lines: <color> <u> <v>, verifiable with verify.py.
"""
import sys
from search_sat import perm_order7, close_group, edge_orbits

group = close_group(perm_order7())
orbits, _ = edge_orbits(group)

pos = set()
for line in open(sys.argv[1]):
    if line.startswith('v'):
        for tok in line.split()[1:]:
            l = int(tok)
            if l > 0:
                pos.add(l)
mapping = {}
for line in open(sys.argv[2]):
    var, o, c = map(int, line.split())
    mapping[var] = (o, c)
with open(sys.argv[3], 'w') as f:
    for var, (o, c) in sorted(mapping.items()):
        if var in pos:
            for (u, v) in orbits[o]:
                f.write(f"{c} {min(u,v)} {max(u,v)}\n")
print("wrote", sys.argv[3])

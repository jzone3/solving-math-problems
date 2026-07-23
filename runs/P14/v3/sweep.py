#!/usr/bin/env python3
"""Sweep all prescribed groups x instances, big groups first, escalating time limits."""
import sys
from km_solve import INSTANCES, GROUPS, close_group, solve

TL = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
only = [int(x) for x in sys.argv[2:]] or [1, 2, 3, 4]

jobs = []
for inst in only:
    V = INSTANCES[inst]['V']
    for gname, gens in GROUPS[V].items():
        jobs.append((len(close_group(V, gens)), inst, gname))
jobs.sort(key=lambda t: (-t[0], t[1]))

results = {}
for gsz, inst, gname in jobs:
    try:
        r = solve(inst, gname, TL)
    except Exception as e:
        r = f"ERR:{e}"
        print(f"inst{inst} group={gname} ERROR {e}", flush=True)
    results[(inst, gname)] = r
    if r == 'SAT':
        print(f"*** SAT inst{inst} {gname} ***", flush=True)

print("\n=== SUMMARY ===")
for (inst, g), r in sorted(results.items()):
    print(inst, g, r)

#!/usr/bin/env python3
"""Sweep 2: new prime-cycle-type groups + long-budget reruns of sweep-1 UNKNOWNs."""
import sys
from km_solve import solve

TL = float(sys.argv[1]) if len(sys.argv) > 1 else 3600.0
JOBS = [
    # (inst, group) — priority order
    (4, 'C7'),          # UNKNOWN at 600s, biggest reduction
    (2, 'C3'), (2, 'C3b'), (2, 'C4'),
    (4, 'C3a'), (4, 'C3b'),
    # new groups, V=14 instances
    (1, 'C11a'), (1, 'C5a'), (1, 'C5b'), (1, 'C3c'), (1, 'C3d'),
    (4, 'C11a'), (4, 'C5a'), (4, 'C5b'), (4, 'C3c'), (4, 'C3d'),
    # new groups, V=12 instances
    (2, 'C7a'), (2, 'C5b'), (2, 'C3c'),
    (3, 'C7a'), (3, 'C5b'), (3, 'C3c'),
]
for inst, g in JOBS:
    try:
        r = solve(inst, g, TL)
        if r == 'SAT':
            print(f"*** SAT inst{inst} {g} ***", flush=True)
    except Exception as e:
        print(f"inst{inst} {g} ERR {e}", flush=True)

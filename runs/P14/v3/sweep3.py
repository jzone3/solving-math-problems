#!/usr/bin/env python3
"""Sweep 3: long-budget runs on the remaining C2 prescribed groups (and inst2 C3)."""
import sys
from km_solve import solve

TL = float(sys.argv[1]) if len(sys.argv) > 1 else 7200.0
which = int(sys.argv[2])  # lane 0 or 1

LANES = [
    # lane 0: instance 1 (V=14) C2 ladder + inst3
    [(1, 'C2'), (1, 'C2a'), (1, 'C2b'), (1, 'C2c'), (1, 'C2d'),
     (3, 'C2'), (3, 'C2a'), (3, 'C2b'), (3, 'C2c')],
    # lane 1: instance 2 (V=12) C2 ladder + C3 retry
    [(2, 'C2'), (2, 'C2a'), (2, 'C2b'), (2, 'C2c'), (2, 'C3'), (2, 'C2d')],
]
for inst, g in LANES[which]:
    try:
        r = solve(inst, g, TL)
        if r == 'SAT':
            print(f"*** SAT inst{inst} {g} ***", flush=True)
    except Exception as e:
        print(f"inst{inst} {g} ERR {e}", flush=True)

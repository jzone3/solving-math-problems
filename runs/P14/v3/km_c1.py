#!/usr/bin/env python3
"""Independent confirmation of nonexistence via the (differently-encoded) KM model
with trivial group: km_c1.py INSTANCE TIMELIMIT."""
import sys
from km_solve import GROUPS, INSTANCES, solve

GROUPS[12]['C1'] = []
GROUPS[14]['C1'] = []
inst = int(sys.argv[1]); tl = float(sys.argv[2])
print(solve(inst, 'C1', tl))

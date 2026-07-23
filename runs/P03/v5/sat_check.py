"""SAT-check candidate orientations from enum_pypy.py.
Usage: python3 sat_check.py n < candN.jsonl"""
import sys
import json
import time
from harness import tau, has_k_disjoint_dijoins

n = int(sys.argv[1])
checked = nonpacking = 0
t0 = time.time()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    arcs = [tuple(a) for a in rec["arcs"]]
    checked += 1
    if checked % 5000 == 1:
        assert tau(n, arcs) == 3, f"tau!=3: {rec}"
    if not has_k_disjoint_dijoins(n, arcs, 3):
        nonpacking += 1
        print("NONPACKING:", json.dumps(rec), flush=True)
    if checked % 2000 == 0:
        print(f"checked={checked} nonpacking={nonpacking} "
              f"t={time.time()-t0:.0f}s", flush=True)
print(f"DONE checked={checked} nonpacking={nonpacking} "
      f"wall={time.time()-t0:.0f}s", flush=True)

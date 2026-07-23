"""Check: for every connected graph with min degree >= 2 on n vertices, some
a in {0, 0.05, ..., 1} gives edge-CW power bound <= RHS46.
Usage: pow46_n10.py <n> <res> <mod>"""
import sys
import subprocess
import numpy as np
from exhaustive_small import g6_to_adj
from search_common import degrees_and_m, rhs_graph, rhs46_edge

AS = [k * 0.05 for k in range(21)]
n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cnt = fails = 0
worst = 1e18
p = subprocess.Popen(["nauty-geng", "-c", "-d2", "-q", str(n), f"{res}/{mod}"],
                     stdout=subprocess.PIPE, text=True)
for line in p.stdout:
    A = g6_to_adj(line.strip())
    d, m = degrees_and_m(A)
    r46 = rhs_graph(A, rhs46_edge)
    iu, ju = np.nonzero(np.triu(A))
    ok = False
    margin = -1e18
    for a in AS:
        da, ma = d ** a, m ** a
        vals = d[iu] * ma[iu] / da[ju] + d[ju] * ma[ju] / da[iu]
        cw = float(vals.max())
        if r46 - cw > margin:
            margin = r46 - cw
        if cw <= r46 + 1e-9:
            ok = True
            break
    if not ok:
        fails += 1
        print("FAIL", line.strip(), margin, flush=True)
    if margin < worst:
        worst = margin
    cnt += 1
p.wait()
print(f"DONE n={n} {res}/{mod} count={cnt} fails={fails} worst_margin={worst:.3e}")

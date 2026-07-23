#!/usr/bin/env python3
"""ILP: minimize |C| s.t. every word of {0,1,2}^6 covered (radius 1). HiGHS."""
import sys
import highspy
import numpy as np

N = 729
def ball(w):
    d = []
    t = w
    for _ in range(6):
        d.append(t % 3); t //= 3
    res = [w]
    p3 = 1
    for i in range(6):
        for v in (1, 2):
            res.append(w + (((d[i] + v) % 3) - d[i]) * p3)
        p3 *= 3
    return res

h = highspy.Highs()
inf = highspy.kHighsInf
h.addVars(N, np.zeros(N), np.ones(N))
h.changeColsIntegrality(N, np.arange(N, dtype=np.int32), np.full(N, highspy.HighsVarType.kInteger))
h.changeColsCost(N, np.arange(N, dtype=np.int32), np.ones(N))
for w in range(N):
    b = ball(w)
    h.addRow(1.0, inf, len(b), np.array(sorted(b), dtype=np.int32), np.ones(len(b)))
ub = float(sys.argv[1]) if len(sys.argv) > 1 else None
if ub is not None:
    h.addRow(-inf, ub, N, np.arange(N, dtype=np.int32), np.ones(N))
tl = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
h.setOptionValue("time_limit", tl)
h.setOptionValue("threads", 1)
h.run()
print("status", h.getModelStatus())
info = h.getInfo()
print("obj", info.objective_function_value, "bound", info.mip_dual_bound, "gap", info.mip_gap)
sol = h.getSolution()
vals = np.array(sol.col_value)
idx = np.where(vals > 0.5)[0]
print("size", len(idx))
if ub is not None and len(idx) and len(idx) <= ub:
    for w in idx:
        t = int(w); print("".join(str((t // 3**p) % 3) for p in range(6)))

"""childJ exp12: which trees fail fixed c? print failing trees per c.
Usage: exp12_treesfixed.py nmin nmax c1 c2 ...
"""
import subprocess
import sys

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9

nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
cs = [float(x) for x in sys.argv[3:]]
for n in range(nmin, nmax + 1):
    cnt = {c: 0 for c in cs}
    tot = 0
    for line in subprocess.Popen(
            f"nauty-gentreeg -q {n} | nauty-copyg -g", shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True).stdout:
        g6 = line.strip()
        if not g6:
            continue
        tot += 1
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        AL = line_graph_adj(E)
        s = np.array([d[i] + d[j] for i, j in E])
        zs = AL @ (AL @ s)
        z1 = AL @ (AL @ np.ones(len(E)))
        for c in cs:
            if c <= -s.min():
                bad = True
            else:
                bad = not (zs + c * z1 <= R * (s + c) + TOL).all()
            if bad:
                cnt[c] += 1
                if cnt[c] <= 5:
                    dsort = sorted((int(x) for x in d), reverse=True)[:6]
                    print(f"n={n} c={c} FAIL {g6} degs{dsort} R={R:.2f}")
    print(f"n={n}: trees={tot} " + " ".join(f"c={c}:fails={cnt[c]}" for c in cs))

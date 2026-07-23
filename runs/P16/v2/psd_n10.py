"""Check childD Conjecture D1 (K = diag(arg46) - A_L^2 >= 0) for all connected
delta>=2 graphs on n vertices.  Usage: psd_n10.py <n> <res> <mod>"""
import sys
import subprocess
import numpy as np
from exhaustive_small import g6_to_adj
from search_common import degrees_and_m

n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cnt = fails = 0
worst = 1e18
p = subprocess.Popen(["nauty-geng", "-c", "-d2", "-q", str(n), f"{res}/{mod}"],
                     stdout=subprocess.PIPE, text=True)
for line in p.stdout:
    A = g6_to_adj(line.strip())
    d, m = degrees_and_m(A)
    iu, ju = np.nonzero(np.triu(A))
    E = len(iu)
    R = np.zeros((len(d), E))
    for e in range(E):
        R[iu[e], e] = 1.0
        R[ju[e], e] = 1.0
    AL = R.T @ R - 2.0 * np.eye(E)
    arg = 2.0 * (d[iu] ** 2 + d[ju] ** 2) - 16.0 * d[iu] * d[ju] / (m[iu] + m[ju]) + 4.0
    K = np.diag(arg) - AL @ AL
    ev = float(np.linalg.eigvalsh(K)[0])
    if ev < worst:
        worst = ev
        if ev < -1e-7:
            fails += 1
            print("PSD-FAIL", line.strip(), ev, flush=True)
    cnt += 1
p.wait()
print(f"DONE n={n} {res}/{mod} count={cnt} fails={fails} min_eig={worst:.3e}")

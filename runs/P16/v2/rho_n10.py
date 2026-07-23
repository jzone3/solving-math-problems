"""Check the STRONGER statements rho(Q) <= RHS44 and RHS46 for all connected graphs
on n vertices (nauty-geng res/mod partition).  Usage: rho_n10.py <n> <res> <mod>."""
import sys
import subprocess
import numpy as np
from exhaustive_small import g6_to_adj
from search_common import rhs_graph, rhs44_edge, rhs46_edge

n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cnt = 0
w44 = w46 = 1e18
p = subprocess.Popen(["nauty-geng", "-c", "-q", str(n), f"{res}/{mod}"],
                     stdout=subprocess.PIPE, text=True)
for line in p.stdout:
    A = g6_to_adj(line.strip())
    d = A.sum(axis=1)
    rho = float(np.linalg.eigvalsh(np.diag(d) + A)[-1])
    g44 = rhs_graph(A, rhs44_edge) - rho
    g46 = rhs_graph(A, rhs46_edge) - rho
    if g44 < w44:
        w44 = g44
        if g44 < -1e-9:
            print("VIOLATION44", line.strip(), g44, flush=True)
    if g46 < w46:
        w46 = g46
        if g46 < -1e-9:
            print("VIOLATION46", line.strip(), g46, flush=True)
    cnt += 1
p.wait()
print(f"DONE n={n} {res}/{mod} count={cnt} min44={w44:.3e} min46={w46:.3e}")

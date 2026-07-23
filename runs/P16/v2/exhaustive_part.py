import subprocess, sys
import numpy as np
from search_common import mu, rhs_graph, rhs44_edge, rhs46_edge
from exhaustive_small import g6_to_adj

n, res, mod = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
worst = {44: 1e9, 46: 1e9}
p = subprocess.Popen(["nauty-geng", "-c", "-q", str(n), f"{res}/{mod}"], stdout=subprocess.PIPE, text=True)
cnt = 0
for line in p.stdout:
    A = g6_to_adj(line.strip())
    lam = mu(A)
    for b, fn in ((44, rhs44_edge), (46, rhs46_edge)):
        gap = rhs_graph(A, fn) - lam
        if gap < worst[b]:
            worst[b] = gap
        if gap < -1e-9:
            print(f"VIOLATION bound {b}: g6={line.strip()}", flush=True)
    cnt += 1
p.wait()
print(f"part {res}/{mod} done cnt={cnt} worst44={worst[44]:.3e} worst46={worst[46]:.3e}")

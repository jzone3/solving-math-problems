"""Verify the n=40 counterexample tree and test (B)-analogues with rho_r =
max arg44 over the line-graph r-ball, for r = 2..diam."""
import sys
import numpy as np
from fractions import Fraction
sys.path.insert(0, ".")
from common import edge_env

edges = []
nxt = [0]
def new():
    v = nxt[0]; nxt[0] += 1; return v
def add(u, v):
    edges.append((u, v))

i = new(); j = new(); add(i, j)
# i-side: 3 branches deg 4, children (2,2,3) each, leaf-padded
for _ in range(3):
    k = new(); add(i, k)
    for c in (2, 2, 3):
        u = new(); add(k, u)
        for _ in range(c - 1):
            add(u, new())
# j-side: pendant + deg-4 branch with children (4,4,4)
add(j, new())
l2 = new(); add(j, l2)
for c in (4, 4, 4):
    u = new(); add(l2, u)
    for _ in range(c - 1):
        add(u, new())

n = nxt[0]
print("n =", n)
A = np.zeros((n, n), dtype=np.int64)
for u, v in edges:
    A[u, v] = A[v, u] = 1
d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
a = E.index((0, 1))
w = zs[a] - s[a] * z1[a]
print(f"e: s={s[a]} z1={z1[a]} zs={zs[a]} w={w} arg44={a44[a]} rho0={rho0[a]}")
print(f"heavy: {z1[a] > rho0[a]}  D={rho0[a]*(s[a]-3)+3*z1[a]-zs[a]}")

# rho_r for all radii via line graph BFS
ne = len(E)
ALb = (AL > 0)
from collections import deque
dist = [-1] * ne
dist[a] = 0
q = deque([a])
while q:
    u = q.popleft()
    for v in np.nonzero(ALb[u])[0]:
        if dist[v] < 0:
            dist[v] = dist[u] + 1
            q.append(v)
maxd = max(dist)
for r in range(2, maxd + 1):
    rr = max(a44[b] for b in range(ne) if dist[b] <= r)
    heavy = z1[a] > rr
    Dr = rr * (s[a] - 3) + 3 * z1[a] - zs[a]
    print(f"r={r}: rho_r={rr} heavy={heavy} D_r={Dr} "
          f"{'(B_r) VIOLATED' if heavy and Dr <= 0 else ''}")
lam = np.linalg.eigvalsh(AL.astype(float)).max()
R = max(a44)
print(f"lambda^2={lam*lam:.4f} R={float(R)} Bound44 ok: {lam*lam<=float(R)+1e-9}")

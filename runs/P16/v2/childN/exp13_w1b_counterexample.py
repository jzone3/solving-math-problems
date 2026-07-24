"""Construct explicit tree realizing abstract config (x,y)=(4,3), dk=(5,5,5),
dl=(1,3), with m_k values at the C1-integrality caps; test W1B (and (W=))."""
import sys
import numpy as np
sys.path.insert(0, ".")
from common import edge_env

edges = []
def add(u, v):
    edges.append((u, v))

# vertices: 0=i, 1=j
nxt = 2
i, j = 0, 1
add(i, j)
ks = []
for _ in range(3):          # k's: degree 5
    k = nxt; nxt += 1
    add(i, k); ks.append(k)
# j children: l1 (pendant), l2 (degree 3)
l1 = nxt; nxt += 1; add(j, l1)
l2 = nxt; nxt += 1; add(j, l2)
# each k: children degrees (2,1,1,1); the degree-2 child gets one leaf
for k in ks:
    c2 = nxt; nxt += 1; add(k, c2)
    leaf = nxt; nxt += 1; add(c2, leaf)
    for _ in range(3):
        c = nxt; nxt += 1; add(k, c)
# l2 children with degrees 6 and 7 (deg-sum 3+6+7=16 => m_l2=16/3)
for deg in (6, 7):
    c = nxt; nxt += 1; add(l2, c)
    for _ in range(deg - 1):
        u = nxt; nxt += 1; add(c, u)

n = nxt
A = np.zeros((n, n), dtype=np.int64)
for u, v in edges:
    A[u, v] = A[v, u] = 1
d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
a = E.index((0, 1))
w = zs[a] - s[a] * z1[a]
print(f"n={n} edge e=(i,j): s={s[a]} z1={z1[a]} zs={zs[a]} w={w} "
      f"arg44_e={a44[a]} rho1={rho1[a]} rho0={rho0[a]}")
print("W1B premise z1>=rho1:", z1[a] >= rho1[a], "| w<=0:", w <= 0)
print("mi,mj:", m[0], m[1], "deg i,j:", d[0], d[1])
for k in ks:
    b = E.index((min(0, k), max(0, k)))
    print(f"  edge ik: d_k={d[k]} m_k={m[k]} arg44={a44[b]} z1={z1[b]}")

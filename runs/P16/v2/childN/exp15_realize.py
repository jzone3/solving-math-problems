"""Realize the abstract W2*/B-violating config (x,y)=(5,3), dk=(5,5,5,5),
dl=(1,3) as an explicit tree; test (B), clause (b) of Conjecture J, ord2-sum
feasibility (Conjecture H), and Bound 44 itself."""
import sys
import numpy as np
from fractions import Fraction
sys.path.insert(0, ".")
from common import edge_env

edges = []
nxt = 0
def new():
    global nxt
    v = nxt
    nxt += 1
    return v
def add(u, v):
    edges.append((u, v))

i = new(); j = new()
add(i, j)
# i-side: 4 neighbors of degree 5
for _ in range(4):
    k = new(); add(i, k)
    for _ in range(4):           # 4 children of degree 2
        u = new(); add(k, u)
        leaf = new(); add(u, leaf)
# j-side: pendant l1; l2 of degree 3 with two degree-6 children
l1 = new(); add(j, l1)
l2 = new(); add(j, l2)
for _ in range(2):
    c = new(); add(l2, c)
    for _ in range(5):
        add(c, new())

n = nxt
A = np.zeros((n, n), dtype=np.int64)
for u, v in edges:
    A[u, v] = A[v, u] = 1
d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
print("n =", n)
a = E.index((0, 1))
w = zs[a] - s[a] * z1[a]
D = rho0[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
print(f"e=(i,j): s={s[a]} z1={z1[a]} zs={zs[a]} w={w} arg44={a44[a]} "
      f"rho0={rho0[a]} heavy={z1[a] > rho0[a]}  D={D}  (B) holds: {D > 0}")

# full (B)/(W=) scan on this tree
violB = violW = 0
for b in range(len(E)):
    if z1[b] > rho0[b]:
        Db = rho0[b] * (s[b] - 3) + 3 * z1[b] - zs[b]
        if Db <= 0:
            violB += 1
            print("  (B) VIOLATED at", E[b], "D =", Db, "s,z1,zs,rho0 =",
                  s[b], z1[b], zs[b], rho0[b])
    elif z1[b] == rho0[b] and zs[b] - s[b] * z1[b] > 0:
        violW += 1
        print("  (W=) VIOLATED at", E[b])
print("violB:", violB, "violW:", violW)

# clause (b) of Conjecture J: for all pairs (e,f), rho in [max(rho0), z1_e]:
# rho*s_e - zs_e + s_f (z1_e - rho) >= 0, strict if rho < z1_e.
# affine in rho => check endpoints rho_lo = max(rho0 e,f), rho_hi = z1_e.
ne = len(E)
violb = 0
smin = min(s)
for eidx in range(ne):
    for fidx in range(ne):
        lo = max(rho0[eidx], rho0[fidx])
        hi = z1[eidx]
        if lo > hi:
            continue
        for rho, strict in ((lo, lo < hi), (hi, False)):
            val = rho * s[eidx] - zs[eidx] + s[fidx] * (z1[eidx] - rho)
            if val < 0 or (strict and val == 0):
                violb += 1
                if violb < 5:
                    print("  clause(b) VIOLATED:", E[eidx], E[fidx], "rho=", rho,
                          "val=", val)
print("clause(b) violations:", violb)

# Conjecture H: ord2-sum interval feasibility at R = max arg44
R = max(a44)
lo_c = Fraction(-smin)
hi_ok = True
LO, HI = None, None
for b in range(ne):
    sig = z1[b] - R
    kap = zs[b] - R * s[b]
    if sig > 0:
        v = Fraction(-kap) / sig
        if HI is None or v < HI:
            HI = v
    elif sig < 0:
        v = Fraction(-kap) / sig
        if LO is None or v > LO:
            LO = v
    else:
        if kap > 0:
            hi_ok = False
print(f"R={R} interval: LO={LO} HI={HI} sigma0_ok={hi_ok} "
      f"feasible={hi_ok and (HI is None or ((LO is None or LO <= HI) and HI > lo_c))}")

# Bound 44 truth: lambda_max(A_L)^2 <= R ?
lam = np.linalg.eigvalsh(AL.astype(float)).max()
print(f"lambda^2 = {lam**2:.6f} vs R = {float(R):.6f}  Bound44 (lam^2<=R): {lam*lam <= float(R) + 1e-9}")

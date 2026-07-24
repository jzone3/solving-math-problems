"""childN: single self-contained EXACT verification of the counterexamples.

T40 (n=40 tree): disproves inequality (B), clause (b) of Conjecture J,
Conjecture J, and CONJECTURE H (childH PROOF44 §5).  Bound 44 itself holds.
T52 (n=52 tree): disproves (B)/clause (b) with rho0 < z1 strictly inside the
2-ball window; H remains feasible there (global R=54 exceeds z1).

All arithmetic exact (Fractions/ints) except the final eigenvalue check.
No shared library code: everything recomputed from scratch.
"""
from fractions import Fraction
from collections import deque
import numpy as np


def build_T40():
    edges = []
    nxt = [0]
    def new():
        v = nxt[0]; nxt[0] += 1; return v
    def add(u, v):
        edges.append((u, v))
    i = new(); j = new(); add(i, j)
    for _ in range(3):                    # i-side: 3 branches of degree 4
        k = new(); add(i, k)
        for c in (2, 2, 3):               # children degrees
            u = new(); add(k, u)
            for _ in range(c - 1):
                add(u, new())             # leaf padding
    add(j, new())                         # pendant on j
    l2 = new(); add(j, l2)                # j-branch of degree 4
    for c in (4, 4, 4):
        u = new(); add(l2, u)
        for _ in range(c - 1):
            add(u, new())
    return edges, nxt[0]


def build_T52():
    edges = []
    nxt = [0]
    def new():
        v = nxt[0]; nxt[0] += 1; return v
    def add(u, v):
        edges.append((u, v))
    i = new(); j = new(); add(i, j)
    for _ in range(4):                    # i-side: 4 branches of degree 5
        k = new(); add(i, k)
        for _ in range(4):                # 4 children of degree 2
            u = new(); add(k, u)
            add(u, new())
    add(j, new())                         # pendant on j
    l2 = new(); add(j, l2)                # j-branch of degree 3
    for _ in range(2):                    # 2 children of degree 6
        c = new(); add(l2, c)
        for _ in range(5):
            add(c, new())
    return edges, nxt[0]


def analyze(edges, n, name):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    deg = {v: len(adj[v]) for v in adj}
    m = {v: Fraction(sum(deg[u] for u in adj[v]), deg[v]) for v in adj}
    E = sorted(tuple(sorted(e)) for e in edges)
    nbrs = {e: [f for f in E if e != f and set(e) & set(f)] for e in E}
    z1 = {e: sum(len(nbrs[f]) for f in nbrs[e]) for e in E}
    zs = {e: sum(sum(deg[a] + deg[b] for (a, b) in nbrs[f]) for f in nbrs[e])
          for e in E}
    s = {e: deg[e[0]] + deg[e[1]] for e in E}
    a44 = {e: 2 * ((deg[e[0]] - 1) ** 2 + (deg[e[1]] - 1) ** 2
                   + m[e[0]] * m[e[1]] - deg[e[0]] * deg[e[1]]) for e in E}
    # rho0 = max arg44 over line-graph 2-ball
    def rho_r(e, r):
        dist = {e: 0}
        q = deque([e])
        while q:
            u = q.popleft()
            if dist[u] == r:
                continue
            for v in nbrs[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return max(a44[f] for f in dist)
    e0 = (0, 1)
    r0 = rho_r(e0, 2)
    R = max(a44.values())
    print(f"== {name}: n={n}, |E|={len(E)} ==")
    print(f"e=(i,j): s={s[e0]} z1={z1[e0]} zs={zs[e0]} w={zs[e0]-s[e0]*z1[e0]}")
    print(f"arg44_e={a44[e0]}  rho0(e)={r0}  rho3(e)={rho_r(e0,3)}  R={R}")
    heavy = z1[e0] > r0
    D = r0 * (s[e0] - 3) + 3 * z1[e0] - zs[e0]
    print(f"heavy at rho0: {heavy};  D_e = {D}  ->  (B) "
          f"{'VIOLATED' if heavy and D <= 0 else 'holds'}")
    # clause (b) of Conjecture J: for all f and admissible rho in
    # [max(rho0(e),rho0(f)), z1_e]: rho*s_e - zs_e + s_f(z1_e-rho) >= 0,
    # strict for rho < z1_e.  Affine in rho: check both endpoints.
    r0f = {f: rho_r(f, 2) for f in E}
    nviol = 0
    worst = None
    for f in E:
        lo = max(r0, r0f[f])
        hi = z1[e0]
        if lo > hi:
            continue
        for rho, strict in ((lo, lo < hi), (hi, False)):
            val = rho * s[e0] - zs[e0] + s[f] * (z1[e0] - rho)
            if val < 0 or (strict and val == 0):
                nviol += 1
                if worst is None or val < worst[0]:
                    worst = (val, f, rho)
    print(f"clause(b) violations over f (e fixed): {nviol}; worst: {worst}")
    # Conjecture H interval (Corollary H3): c > -min s, (z1-R)c <= Rs - zs
    LO = HI = None
    ok0 = True
    for e in E:
        sig, kap = z1[e] - R, zs[e] - R * s[e]
        if sig > 0:
            v = Fraction(-kap) / sig
            HI = v if HI is None or v < HI else HI
        elif sig < 0:
            v = Fraction(-kap) / sig
            LO = v if LO is None or v > LO else LO
        elif kap > 0:
            ok0 = False
    smin = min(s.values())
    feas = ok0 and (HI is None or ((LO is None or LO <= HI) and HI > -smin))
    print(f"H interval: c in [{LO}, {HI}], need c > -{smin}; "
          f"H {'FEASIBLE' if feas else 'INFEASIBLE (Conjecture H FALSE)'}")
    # Bound 44 truth (numeric eigenvalue)
    idx = {e: t for t, e in enumerate(E)}
    AL = np.zeros((len(E), len(E)))
    for e in E:
        for f in nbrs[e]:
            AL[idx[e], idx[f]] = 1
    lam = np.linalg.eigvalsh(AL).max()
    print(f"lambda(A_L)^2 = {lam*lam:.6f} vs R = {float(R):.6f}: Bound44 "
          f"{'holds' if lam*lam <= float(R) + 1e-9 else 'VIOLATED'}")
    print()


if __name__ == "__main__":
    analyze(*build_T40(), "T40")
    analyze(*build_T52(), "T52")

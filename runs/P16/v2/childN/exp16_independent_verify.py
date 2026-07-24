"""Independent from-scratch verification of the n=52 counterexample tree:
pure-python adjacency lists, exact Fraction arithmetic, no shared code.
Recomputes d, m, arg44 per edge, line-graph 2-walks by explicit walk
enumeration, B2 by BFS in the line graph, rho0, and D_e."""
from fractions import Fraction

adj = {}
def add(u, v):
    adj.setdefault(u, set()).add(v)
    adj.setdefault(v, set()).add(u)

nxt = [0]
def new():
    v = nxt[0]
    nxt[0] += 1
    adj.setdefault(v, set())
    return v

i = new(); j = new(); add(i, j)
for _ in range(4):
    k = new(); add(i, k)
    for _ in range(4):
        u = new(); add(k, u)
        add(u, new())
l1 = new(); add(j, l1)
l2 = new(); add(j, l2)
for _ in range(2):
    c = new(); add(l2, c)
    for _ in range(5):
        add(c, new())

n = nxt[0]
assert n == 52
deg = {v: len(adj[v]) for v in adj}
m = {v: Fraction(sum(deg[u] for u in adj[v]), deg[v]) for v in adj}
edges = sorted({tuple(sorted((u, v))) for u in adj for v in adj[u]})
eid = {e: t for t, e in enumerate(edges)}

def incident(e, f):
    return e != f and len(set(e) & set(f)) > 0

# line graph adjacency lists
nbrs = {e: [f for f in edges if incident(e, f)] for e in edges}

def z1(e):   # number of 2-walks in L(G) from e = sum_f~e deg_L(f) ... careful:
    # (A_L^2 1)_e = sum over walks e->f->g = sum_{f~e} deg_L(f)
    return sum(len(nbrs[f]) for f in nbrs[e])

def zs(e):
    return sum(sum(deg[a] + deg[b] for (a, b) in nbrs[f]) for f in nbrs[e])

def arg44(e):
    a, b = e
    return 2 * ((deg[a] - 1) ** 2 + (deg[b] - 1) ** 2 + m[a] * m[b] - deg[a] * deg[b])

def B2(e):
    out = {e}
    for f in nbrs[e]:
        out.add(f)
        out.update(nbrs[f])
    return out

e0 = (0, 1)
r0 = max(arg44(g) for g in B2(e0))
se = deg[0] + deg[1]
Z1, ZS = z1(e0), zs(e0)
D = r0 * (se - 3) + 3 * Z1 - ZS
print(f"independent: s={se} z1={Z1} zs={ZS} arg44_e={arg44(e0)} rho0={r0}")
print(f"heavy (z1>rho0): {Z1 > r0}")
print(f"D_e = {D}  => (B) {'HOLDS' if D > 0 else 'VIOLATED'}")
print(f"w_e = zs - s*z1 = {ZS - se * Z1}")
# clause (b) with f = e at rho = z1_e (needs >= 0):
print("clause(b) value at rho=z1_e (any f):", Z1 * se - ZS)
# sanity: global R and Bound 44 by power iteration on A_L
R = max(arg44(g) for g in edges)
import random
vec = {e: 1.0 for e in edges}
for _ in range(2000):
    nv = {e: sum(vec[f] for f in nbrs[e]) for e in edges}
    norm = max(abs(t) for t in nv.values())
    vec = {e: t / norm for e, t in nv.items()}
lam = norm
print(f"global R = {R}, lambda ~= {lam:.6f}, lambda^2 ~= {lam*lam:.6f} <= R: {lam*lam <= R}")

"""Construct H_3, the intersection graph of the Hermitian unital U_3 in PG(2,9)
with its secant lines, exactly as defined in Mulrenin-van Overberghe arXiv:2506.14942 §2.

GF(9) = GF(3)[x]/(x^2+1). Elements encoded as (a,b) ~ a + b*x, a,b in {0,1,2}.
Unital: U = { <X,Y,Z> : X^4 + Y^4 + Z^4 = 0 }  (q=3, q+1=4).
Vertices of H_3 = secant lines (meet U in exactly 4 points).
Edge {l1,l2} iff the (unique) intersection point of l1,l2 lies in U.
"""
from itertools import product, combinations

# ---------- GF(9) arithmetic ----------
ELTS = [(a, b) for a in range(3) for b in range(3)]
ZERO, ONE = (0, 0), (1, 0)

def add(u, v):
    return ((u[0] + v[0]) % 3, (u[1] + v[1]) % 3)

def neg(u):
    return ((-u[0]) % 3, (-u[1]) % 3)

def mul(u, v):
    # (a+bx)(c+dx) = ac + (ad+bc)x + bd x^2, x^2 = -1
    a, b = u; c, d = v
    return ((a * c - b * d) % 3, (a * d + b * c) % 3)

def pow4(u):
    u2 = mul(u, u)
    return mul(u2, u2)

INV = {}
for u in ELTS:
    if u == ZERO: continue
    for v in ELTS:
        if mul(u, v) == ONE:
            INV[u] = v

# ---------- PG(2,9) points (normalized projective triples) ----------
def normalize(p):
    for coord in p:
        if coord != ZERO:
            inv = INV[coord]
            return tuple(mul(inv, c) for c in p)
    return None

points = set()
for X, Y, Z in product(ELTS, repeat=3):
    if (X, Y, Z) == (ZERO, ZERO, ZERO): continue
    points.add(normalize((X, Y, Z)))
points = sorted(points)
assert len(points) == 91, len(points)

# ---------- Unital ----------
def in_unital(p):
    s = ZERO
    for c in p:
        s = add(s, pow4(c))
    return s == ZERO

unital = [p for p in points if in_unital(p)]
assert len(unital) == 28, len(unital)

# ---------- Lines of PG(2,9): line = normalized dual triple [a,b,c]; point on line iff aX+bY+cZ=0
def dot(l, p):
    s = ZERO
    for lc, pc in zip(l, p):
        s = add(s, mul(lc, pc))
    return s

lines = points  # duality: same normalized triples
line_pts = {l: frozenset(p for p in points if dot(l, p) == ZERO) for l in lines}
for l in lines:
    assert len(line_pts[l]) == 10

# secants: meet U in exactly q+1 = 4 points
unital_set = set(unital)
secants = [l for l in lines if len(line_pts[l] & unital_set) == 4]
tangents = [l for l in lines if len(line_pts[l] & unital_set) == 1]
assert len(secants) == 63, len(secants)
assert len(tangents) == 28, len(tangents)

# ---------- H_3 ----------
sec_upts = {l: line_pts[l] & unital_set for l in secants}

def build_h3():
    n = 63
    idx = {l: i for i, l in enumerate(secants)}
    adj = [[False] * n for _ in range(n)]
    edges = []
    meet_pt = {}
    for l1, l2 in combinations(secants, 2):
        common = line_pts[l1] & line_pts[l2]
        assert len(common) == 1
        p = next(iter(common))
        if p in unital_set:
            i, j = idx[l1], idx[l2]
            adj[i][j] = adj[j][i] = True
            edges.append((i, j))
            meet_pt[(i, j)] = p
    return idx, adj, edges, meet_pt

idx, adj, edges, meet_pt = build_h3()

def neighbors(i):
    return [j for j in range(63) if adj[i][j]]

def all_triangles():
    tri = []
    for i, j in edges:
        for k in range(j + 1, 63):
            if adj[i][k] and adj[j][k]:
                tri.append((i, j, k))
    return tri

def nondegenerate_triangles():
    """Triangles whose three pairwise intersection points in U are all distinct."""
    out = []
    for (i, j, k) in all_triangles():
        p1 = meet_pt[(i, j)]
        p2 = meet_pt[(i, k)]
        p3 = meet_pt[(j, k)]
        if len({p1, p2, p3}) == 3:
            out.append((i, j, k))
    return out

def maximal_cliques_C():
    """C_3: for each unital point, the clique of secants through it."""
    cl = {}
    for p in unital:
        cl[p] = sorted(idx[l] for l in secants if p in sec_upts[l])
    return cl

if __name__ == "__main__":
    n = 63
    degs = [sum(adj[i]) for i in range(n)]
    print("n =", n, "regular:", set(degs))
    print("edges:", len(edges))
    tri = all_triangles()
    ndt = nondegenerate_triangles()
    print("triangles:", len(tri), "non-degenerate:", len(ndt))
    cl = maximal_cliques_C()
    sizes = {len(v) for v in cl.values()}
    print("cliques C_3:", len(cl), "sizes:", sizes)
    # strong regularity checks
    import random
    lam = set(); mu = set()
    for i in range(n):
        for j in range(i + 1, n):
            common = sum(1 for k in range(n) if adj[i][k] and adj[j][k])
            (lam if adj[i][j] else mu).add(common)
    print("lambda(common nbrs, adjacent):", lam, " mu(non-adjacent):", mu)

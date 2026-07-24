#!/usr/bin/env python3
"""Construct H_3, the intersection graph of the secants of the Hermitian unital
in PG(2,9), and the non-degenerate triangle system T_3, following
Mulrenin-Van Overberghe, "Some remarks on Folkman graphs for triangles"
(arXiv:2506.14942), Section 2.

Definitions (paper §2):
  - Work in PG(2, q^2) with q=3, i.e. over GF(9).
  - Hermitian unital  U = { <X,Y,Z> : X^(q+1)+Y^(q+1)+Z^(q+1) = 0 },  |U| = q^3+1 = 28.
  - A line is a SECANT if it meets U in exactly q+1 = 4 points; there are
    |L| = q^4-q^3+q^2 = 63 secants.
  - H_q = intersection graph of secants: vertices = secants, v_l1 ~ v_l2 iff
    l1 ∩ l2 ∈ U (the two secants cross at a unital point).
  - Maximal cliques C_q: for each unital point p, the q^2 secants through p form
    a clique of order q^2 = 9; there are q^3+1 = 28 of them; every edge lies in
    exactly one.
  - A triangle (3 pairwise-adjacent secants) is DEGENERATE if all three pass
    through a single common unital point (i.e. it lies inside one clique of C_q),
    and NON-DEGENERATE otherwise (its three crossing points are distinct).
    T_q := the set of non-degenerate triangles.

Outputs (this script): h3.edges (edge list, 0-indexed secant ids),
h3.cnf (arrowing CNF for H_3 -> (K_3)_{T_3}), and prints exact property checks
against Propositions 2.1/2.2/2.3 of the paper.  A separate script generates the
DRAT-checked UNSAT proof.
"""
import itertools
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# GF(9) = GF(3)[i]/(i^2 = -1 = 2).  Element a+b*i encoded as integer a+3*b,
# a,b in {0,1,2}.
# ---------------------------------------------------------------------------
def _parts(e):
    return e % 3, e // 3


def _mk(a, b):
    return (a % 3) + 3 * (b % 3)


def gadd(x, y):
    ax, bx = _parts(x)
    ay, by = _parts(y)
    return _mk(ax + ay, bx + by)


def gmul(x, y):
    ax, bx = _parts(x)
    ay, by = _parts(y)
    # (ax+bx i)(ay+by i) = (ax ay - bx by) + (ax by + bx ay) i,  i^2 = -1
    return _mk(ax * ay - bx * by, ax * by + bx * ay)


GF = list(range(9))
ZERO, ONE = 0, 1


def gpow(x, n):
    r = ONE
    for _ in range(n):
        r = gmul(r, x)
    return r


def norm_pow(x):
    """X^(q+1) = X^4 for q=3."""
    return gpow(x, 4)


# self-test of the field
assert gmul(3, 3) == 2, "i^2 must equal 2 (=-1) in GF(9)"  # 3 encodes i
for a in GF:
    if a != ZERO:
        # every nonzero element is invertible
        assert any(gmul(a, b) == ONE for b in GF), a
# GF(9)* is cyclic of order 8
nonzero = [g for g in GF if g != ZERO]
assert len(nonzero) == 8


# ---------------------------------------------------------------------------
# PG(2,9): points and lines are nonzero triples up to scalar, normalized so the
# first nonzero coordinate is 1.  Duality: a line [a:b:c] is the point set
# { <X,Y,Z> : aX+bY+cZ = 0 }.
# ---------------------------------------------------------------------------
def normalize(v):
    for c in v:
        if c != ZERO:
            inv = next(b for b in GF if gmul(c, b) == ONE)
            return tuple(gmul(inv, t) for t in v)
    raise ValueError("zero vector")


def all_projective_points():
    seen = {}
    pts = []
    for X in GF:
        for Y in GF:
            for Z in GF:
                if (X, Y, Z) == (ZERO, ZERO, ZERO):
                    continue
                key = normalize((X, Y, Z))
                if key not in seen:
                    seen[key] = len(pts)
                    pts.append(key)
    return pts


def dot(u, v):
    return gadd(gadd(gmul(u[0], v[0]), gmul(u[1], v[1])), gmul(u[2], v[2]))


def build():
    points = all_projective_points()
    assert len(points) == 91, len(points)          # q^4+q^2+1 = 91
    pindex = {p: i for i, p in enumerate(points)}

    # Hermitian unital
    unital = [p for p in points if
              gadd(gadd(norm_pow(p[0]), norm_pow(p[1]), ), norm_pow(p[2])) == ZERO]
    assert len(unital) == 28, len(unital)          # q^3+1
    unital_set = set(unital)

    # Lines = same set of homogeneous coordinate triples (self-dual labelling).
    lines = points  # a line's coefficient vector is a projective point
    # For each line, the unital points on it.
    secants = []            # list of (line_coeff, frozenset of unital pts on it)
    for L in lines:
        on = frozenset(p for p in unital if dot(L, p) == ZERO)
        if len(on) == 4:    # q+1
            secants.append((L, on))
    assert len(secants) == 63, len(secants)        # q^4-q^3+q^2

    n = len(secants)
    scoef = [s[0] for s in secants]
    son = [s[1] for s in secants]

    # unique intersection point of two distinct lines in PG(2,q^2) is the cross
    # product of their coefficient vectors.
    def gsub(x, y):
        ax, bx = _parts(x)
        ay, by = _parts(y)
        return _mk(ax - ay, bx - by)

    def cross3(a, b):
        cx = gsub(gmul(a[1], b[2]), gmul(a[2], b[1]))
        cy = gsub(gmul(a[2], b[0]), gmul(a[0], b[2]))
        cz = gsub(gmul(a[0], b[1]), gmul(a[1], b[0]))
        return normalize((cx, cy, cz))

    # adjacency: secants i,j adjacent iff their crossing point is a unital point.
    # (equivalently iff son[i] & son[j] is nonempty -- they share a unital pt.)
    adj = [set() for _ in range(n)]
    cross_pt = {}
    for i, j in itertools.combinations(range(n), 2):
        shared = son[i] & son[j]
        if shared:
            assert len(shared) == 1                # two secants share <=1 unital pt
            adj[i].add(j)
            adj[j].add(i)
            cross_pt[(i, j)] = next(iter(shared))
            # sanity: the algebraic crossing point equals the shared unital point
            assert cross3(scoef[i], scoef[j]) == next(iter(shared))

    deg = [len(a) for a in adj]
    assert all(d == 32 for d in deg), (min(deg), max(deg))   # d=(q+1)(q^2-1)=32

    edges = sorted((i, j) for i in range(n) for j in adj[i] if i < j)
    assert len(edges) == n * 32 // 2 == 1008, len(edges)

    return dict(n=n, adj=adj, edges=edges, son=son, unital=unital,
                cross_pt=cross_pt)


def triangles_and_system(G):
    n, adj, cross_pt, son = G["n"], G["adj"], G["cross_pt"], G["son"]

    def cp(i, j):
        return cross_pt[(i, j)] if i < j else cross_pt[(j, i)]

    tris = []
    nondeg = []
    for i, j, k in itertools.combinations(range(n), 3):
        if j in adj[i] and k in adj[i] and k in adj[j]:
            tris.append((i, j, k))
            p_ij, p_ik, p_jk = cp(i, j), cp(i, k), cp(j, k)
            # degenerate iff all three secants pass a common unital point
            # <=> the three crossing points coincide
            if p_ij == p_ik == p_jk:
                pass  # degenerate
            else:
                # non-degenerate: three distinct crossing points
                assert len({p_ij, p_ik, p_jk}) == 3
                nondeg.append((i, j, k))
    return tris, nondeg


def check_k4(G, nondeg):
    """Proposition 2.3: no four triangles of T_3 span a K_4, i.e. no K_4 has all
    four of its faces non-degenerate."""
    n, adj = G["n"], G["adj"]
    ndset = set(nondeg)
    bad = 0
    for a, b, c, d in itertools.combinations(range(n), 4):
        if (b in adj[a] and c in adj[a] and d in adj[a]
                and c in adj[b] and d in adj[b] and d in adj[c]):
            faces = [(a, b, c), (a, b, d), (a, c, d), (b, c, d)]
            if all(f in ndset for f in faces):
                bad += 1
    return bad


def write_cnf(G, nondeg, path):
    edges = G["edges"]
    eidx = {e: i + 1 for i, e in enumerate(edges)}

    def evar(u, v):
        return eidx[(u, v) if u < v else (v, u)]

    clauses = []
    for (i, j, k) in nondeg:
        a, b, c = evar(i, j), evar(i, k), evar(j, k)
        clauses.append((a, b, c))
        clauses.append((-a, -b, -c))
    with open(path, "w") as f:
        f.write(f"p cnf {len(edges)} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return len(edges), len(clauses)


def main():
    out = Path(__file__).resolve().parent
    G = build()
    tris, nondeg = triangles_and_system(G)

    print(f"H_3: n={G['n']} vertices, {len(G['edges'])} edges, 32-regular  [OK]")
    print(f"unital |U|=28, secants=63  [OK]")

    # expected |T_3| from paper eq (3): (1/6)(q^4-q^3+q^2)(q^3-q)(q+1)q, q=3
    q = 3
    expT = (q**4 - q**3 + q**2) * (q**3 - q) * (q + 1) * q // 6
    print(f"triangles total={len(tris)}, non-degenerate |T_3|={len(nondeg)} "
          f"(paper formula {expT})")
    assert len(nondeg) == expT == 3024, (len(nondeg), expT)

    bad = check_k4(G, nondeg)
    print(f"Prop 2.3 check: #K4 with all 4 faces non-degenerate = {bad} "
          f"(must be 0)  [{'OK' if bad == 0 else 'FAIL'}]")
    assert bad == 0

    # H_3 does contain K4's overall (it is not K4-free) -- report how many, to be
    # honest that this is NOT yet a Folkman graph.
    nv, nc = write_cnf(G, nondeg, out / "h3.cnf")
    with open(out / "h3.edges", "w") as f:
        for (u, v) in G["edges"]:
            f.write(f"{u} {v}\n")
    print(f"wrote h3.cnf ({nv} vars, {nc} clauses), h3.edges")
    print("SAT  <=> a 2-coloring with no monochromatic non-degenerate triangle")
    print("UNSAT <=> H_3 -> (K_3)_{T_3}  (the Mulrenin-Van Overberghe q=3 result)")
    print("PASS")


if __name__ == "__main__":
    main()

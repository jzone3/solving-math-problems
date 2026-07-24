#!/usr/bin/env python3
"""Independent verifier for the q=3 Hermitian-unital secant graph H_3.

This intentionally uses GF(3)[t]/(t^2+2t+2), rather than the field model in
build_h3.py.  The isomorphism to the canonical integer labels is used only to
make the independently reconstructed secant ordering comparable to h3.edges.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path

Q = 3
F = range(9)
ZERO, ONE = 0, 1


def parts(x):
    return x % 3, x // 3


def add(x, y):
    a, b = parts(x)
    c, d = parts(y)
    return ((a + c) % 3) + 3 * ((b + d) % 3)


def neg(x):
    a, b = parts(x)
    return ((-a) % 3) + 3 * ((-b) % 3)


def mul(x, y):
    """t^2 + 2t + 2 = 0, hence t^2=t+1 over GF(3)."""
    a, b = parts(x)
    c, d = parts(y)
    return ((a * c + b * d) % 3) + 3 * ((a * d + b * c + b * d) % 3)


def power(x, n):
    result = ONE
    for _ in range(n):
        result = mul(result, x)
    return result


def inverse(x):
    assert x != ZERO
    return next(y for y in F if mul(x, y) == ONE)


# t maps to 2+i in the other model (integer label 5), so this is a field
# isomorphism used solely for canonical coordinate ordering.  These tiny
# operations are deliberately separate from the arithmetic above.
def canonical_add(x, y):
    return ((x % 3 + y % 3) % 3) + 3 * ((x // 3 + y // 3) % 3)


def canonical_mul(x, y):
    a, b = x % 3, x // 3
    c, d = y % 3, y // 3
    return ((a * c - b * d) % 3) + 3 * ((a * d + b * c) % 3)


NEW_TO_CANONICAL = {
    x: canonical_add(x % 3, canonical_mul(x // 3, 5)) for x in F
}


def normalize(v):
    for x in v:
        if x != ZERO:
            z = inverse(x)
            return tuple(mul(z, y) for y in v)
    raise ValueError("zero projective vector")


def canonical_tuple(v):
    return tuple(NEW_TO_CANONICAL[x] for x in v)


def projective_points():
    points = set()
    for x in F:
        for y in F:
            for z in F:
                if (x, y, z) != (ZERO, ZERO, ZERO):
                    points.add(normalize((x, y, z)))
    return sorted(points, key=canonical_tuple)


def dot(a, b):
    return add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))


def cross(a, b):
    return normalize(
        (
            add(mul(a[1], b[2]), neg(mul(a[2], b[1]))),
            add(mul(a[2], b[0]), neg(mul(a[0], b[2]))),
            add(mul(a[0], b[1]), neg(mul(a[1], b[0]))),
        )
    )


def build():
    points = projective_points()
    assert len(points) == 91
    unital = [
        p
        for p in points
        if add(add(power(p[0], 4), power(p[1], 4)), power(p[2], 4)) == ZERO
    ]
    assert len(unital) == 28
    uset = set(unital)

    # Sort coefficient vectors by the canonical labels to reproduce the
    # constructor's independent secant numbering.
    lines = sorted(points, key=canonical_tuple)
    secants = []
    for line in lines:
        on = frozenset(p for p in unital if dot(line, p) == ZERO)
        if len(on) == 4:
            secants.append((line, on))
    assert len(secants) == 63

    coeff = [line for line, _ in secants]
    on = [pts for _, pts in secants]
    adj = [set() for _ in secants]
    crossing = {}
    for i, j in combinations(range(63), 2):
        shared = on[i] & on[j]
        if shared:
            assert len(shared) == 1
            p = next(iter(shared))
            assert cross(coeff[i], coeff[j]) == p
            adj[i].add(j)
            adj[j].add(i)
            crossing[(i, j)] = p
    edges = sorted((i, j) for i in range(63) for j in adj[i] if i < j)
    return {
        "points": points,
        "unital": unital,
        "secants": secants,
        "on": on,
        "adj": adj,
        "edges": edges,
        "crossing": crossing,
        "uset": uset,
    }


def triangles(G):
    adj = G["adj"]
    crossing = G["crossing"]

    def cp(i, j):
        return crossing[(i, j) if i < j else (j, i)]

    all_t = []
    nondeg = []
    for i, j, k in combinations(range(63), 3):
        if j in adj[i] and k in adj[i] and k in adj[j]:
            t = (i, j, k)
            all_t.append(t)
            pts = (cp(i, j), cp(i, k), cp(j, k))
            if len(set(pts)) > 1:
                assert len(set(pts)) == 3
                nondeg.append(t)
    return all_t, nondeg


def check_k4_prop(G, nondeg):
    nd = set(nondeg)
    adj = G["adj"]
    bad = 0
    for a, b, c, d in combinations(range(63), 4):
        if all(
            [
                b in adj[a],
                c in adj[a],
                d in adj[a],
                c in adj[b],
                d in adj[b],
                d in adj[c],
            ]
        ):
            faces = [(a, b, c), (a, b, d), (a, c, d), (b, c, d)]
            if all(face in nd for face in faces):
                bad += 1
    return bad


def read_cnf(path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    assert header[:2] == ["p", "cnf"]
    nv, nc = int(header[2]), int(header[3])
    clauses = [tuple(map(int, line.split()[:-1])) for line in lines[1:] if line]
    assert len(clauses) == nc
    return nv, nc, clauses


def main():
    root = Path(__file__).resolve().parent
    G = build()
    adj = G["adj"]
    edges = G["edges"]
    all_t, nondeg = triangles(G)

    assert len(edges) == 1008
    assert all(len(a) == 32 for a in adj)
    for i, j in combinations(range(63), 2):
        common = len(adj[i] & adj[j])
        assert common == 16, (i, j, common)

    cliques = []
    for p in G["unital"]:
        clique = tuple(i for i, pts in enumerate(G["on"]) if p in pts)
        assert len(clique) == 9
        assert all(v in adj[u] for u, v in combinations(clique, 2))
        cliques.append(frozenset(clique))
    assert len(set(cliques)) == 28

    edge_clique_count = Counter()
    for clique in cliques:
        for edge in combinations(sorted(clique), 2):
            edge_clique_count[edge] += 1
    assert set(edge_clique_count.values()) == {1}
    assert set(edge_clique_count) == set(edges)

    assert len(all_t) == 5376
    assert len(nondeg) == 3024
    assert check_k4_prop(G, nondeg) == 0

    edge_var = {edge: i + 1 for i, edge in enumerate(edges)}

    listed_edges = [
        tuple(map(int, line.split()))
        for line in (root / "h3.edges").read_text().splitlines()
        if line
    ]
    assert listed_edges == edges
    assert {v for e in listed_edges for v in e} <= set(range(63))

    expected = []
    for i, j, k in nondeg:
        a, b, c = edge_var[(i, j)], edge_var[(i, k)], edge_var[(j, k)]
        expected.extend(((a, b, c), (-a, -b, -c)))
    nv, nc, actual = read_cnf(root / "h3.cnf")
    assert (nv, nc) == (1008, 6048)
    assert Counter(actual) == Counter(expected)

    print("H3 independent reconstruction: PASS")
    print("PASS: 63 vertices, 1008 edges, 32-regular")
    print("PASS: strongly regular srg(63,32,16,16)")
    print("PASS: 28 maximal cliques of order 9; every edge in exactly one")
    print("PASS: 5376 triangles, 3024 non-degenerate triangles")
    print("PASS: Prop 2.3 (zero K4 with four non-degenerate faces)")
    print("PASS: h3.edges numbering and h3.cnf clause multiset exactly match")
    print("PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent verifier for P02 (Brandt's regular supergraph conjecture,
as stated on West's open problem page dwest.web.illinois.edu/openp/regsup.html:

  "If G is a maximal triangle-free graph and has minimum degree at least
   n(G)/3, then G has a regular supergraph obtainable by vertex
   multiplications."

CLAIM (this run): the statement is FALSE at the boundary delta = n/3.
Witness: the 9-vertex graph below (and further graphs at n=12, 15, ...).

Vertex multiplication with multiplicities x_v >= 1 (integers) turns G into a
regular graph of degree d iff  sum_{u in N(v)} x_u = d  for every v.
So the conjecture for G says: EXISTS integers x_v >= 1 and d with A x = d*1.

Infeasibility proof checked here (Farkas certificate): rationals y_v with
    (i)  sum_v y_v = 0
    (ii) (A y)_u >= 0 for all u
    (iii) sum_u (A y)_u > 0.
If x >= 1 and A x = d*1 then, using symmetry of A,
    0 = d * sum_v y_v = sum_v y_v (A x)_v = sum_u (A y)_u x_u
      >= sum_u (A y)_u > 0,   contradiction.
(The middle inequality uses x_u >= 1 and (A y)_u >= 0.)
This rules out EVERY degree d simultaneously, with pure exact arithmetic.

The script also re-checks from scratch that each witness graph is
triangle-free, maximal triangle-free, and has min degree >= n/3.
Only stdlib used. Prints PASS iff everything verifies.
"""

from fractions import Fraction as F
from itertools import combinations

WITNESSES = [
    # (name, n, edge list, farkas certificate y)
    (
        "n9-minimal (g6: H?q`qjo)",
        9,
        [(0, 4), (0, 5), (0, 8), (1, 4), (1, 7), (1, 8), (2, 5), (2, 6),
         (2, 8), (3, 6), (3, 7), (3, 8), (4, 6), (5, 7)],
        [F(1), F(-1, 2), F(-1, 2), F(1), F(-1, 2), F(-1, 2), F(-1, 2),
         F(-1, 2), F(1)],
    ),
    (
        "n12 twin-free (g6: K?AFE_]JVoN_)",
        12,
        [(0, 5), (0, 6), (0, 7), (0, 10), (1, 6), (1, 7), (1, 10), (1, 11),
         (2, 6), (2, 9), (2, 10), (2, 11), (3, 7), (3, 8), (3, 10), (3, 11),
         (4, 8), (4, 9), (4, 10), (4, 11), (5, 8), (5, 9), (5, 11), (6, 8),
         (7, 9)],
        [F(1), F(1), F(-1), F(-1), F(1), F(1), F(-1), F(-1), F(-1), F(-1),
         F(1), F(1)],
    ),
    (
        "n15 4-chromatic (g6: N??E@_NMeIfo{GrO^_?)",
        15,
        [(0, 6), (0, 10), (0, 12), (0, 13), (0, 14), (1, 6), (1, 10), (1, 12),
         (1, 13), (1, 14), (2, 7), (2, 9), (2, 11), (2, 12), (2, 14), (3, 7),
         (3, 9), (3, 11), (3, 12), (3, 14), (4, 8), (4, 9), (4, 11), (4, 13),
         (4, 14), (5, 8), (5, 10), (5, 11), (5, 13), (5, 14), (6, 8), (6, 9),
         (6, 11), (7, 8), (7, 10), (7, 13), (8, 12), (9, 10)],
        [F(-3, 2), F(1), F(-3, 2), F(1), F(1), F(0), F(-1, 2), F(-1, 2), F(1),
         F(1), F(0), F(-3, 2), F(0), F(-1, 2), F(1)],
    ),
    (
        "n18 uniform 2-blowup of n9 witness (infinite family n=9t)",
        18,
        [(0, 8), (0, 9), (0, 10), (0, 11), (0, 16), (0, 17), (1, 8), (1, 9),
         (1, 10), (1, 11), (1, 16), (1, 17), (2, 8), (2, 9), (2, 14), (2, 15),
         (2, 16), (2, 17), (3, 8), (3, 9), (3, 14), (3, 15), (3, 16), (3, 17),
         (4, 10), (4, 11), (4, 12), (4, 13), (4, 16), (4, 17), (5, 10),
         (5, 11), (5, 12), (5, 13), (5, 16), (5, 17), (6, 12), (6, 13),
         (6, 14), (6, 15), (6, 16), (6, 17), (7, 12), (7, 13), (7, 14),
         (7, 15), (7, 16), (7, 17), (8, 12), (8, 13), (9, 12), (9, 13),
         (10, 14), (10, 15), (11, 14), (11, 15)],
        [F(1), F(1), F(-2), F(1), F(-2), F(1), F(1), F(1), F(-2), F(1), F(-2),
         F(1), F(-2), F(1), F(-2), F(1), F(1), F(1)],
    ),
]


def check(name, n, edges, y):
    N = [set() for _ in range(n)]
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b
        N[a].add(b)
        N[b].add(a)
    # triangle-free
    for a, b in edges:
        assert not (N[a] & N[b]), f"{name}: triangle through edge {a},{b}"
    # maximal: every non-edge has a common neighbour
    for u, v in combinations(range(n), 2):
        if v not in N[u]:
            assert N[u] & N[v], f"{name}: non-edge {u},{v} addable"
    # minimum degree >= n/3  (exact rational comparison)
    for v in range(n):
        assert F(len(N[v])) >= F(n, 3), f"{name}: deg({v}) < n/3"
    # Farkas certificate
    assert len(y) == n
    assert sum(y) == 0, f"{name}: sum y != 0"
    Ay = [sum(y[u] for u in N[v]) for v in range(n)]
    assert all(a >= 0 for a in Ay), f"{name}: A y has negative entry"
    assert sum(Ay) > 0, f"{name}: 1'A y not positive"
    print(f"  OK: {name}  (n={n}, delta={min(len(s) for s in N)}, "
          f"no regular multiplication supergraph)")


def main():
    for w in WITNESSES:
        check(*w)
    print("PASS")


if __name__ == "__main__":
    main()

"""SAT decider for P04 (Hajos cycle decomposition), variant V3.

Question decided: given a simple Eulerian graph G and an integer k, does G
admit a decomposition of its edge set into at most k edge-disjoint cycles?

Encoding (edge-coloring + per-class connectivity):
  - x[e][c]  : edge e gets color c (exactly one color per edge).
  - Each color class must be 2-regular on its support: for every vertex v and
    color c, the number of c-colored edges at v is 0 or 2
    (at-most-2 cardinality + "not exactly one" implication clauses).
    => each class is a disjoint union of cycles.
  - Connectivity of each class (=> class is a single cycle) via a BFS-level
    reachability ladder: r[c][v] <-> v touches color c; the minimum-index
    vertex of the class is the root (level 0); a[c][v][d] means "v reachable
    from the root within d steps inside class c"; justification clauses
    prevent spurious reachability; constraint r[c][v] -> a[c][v][n-1].
  - Symmetry breaking between interchangeable color classes:
    x[e][c] -> OR_{e'<e} x[e'][c-1]  (first edge of color c comes after the
    first edge of color c-1), plus edge i restricted to colors <= i.

G decomposes into <= k cycles  <=>  formula SAT.
A counterexample to Hajos = Eulerian G with UNSAT at k = floor((n-1)/2).
"""

from itertools import combinations
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153


def build_cnf(n, edges, k):
    """n vertices 0..n-1, edges list of sorted tuples, k colors."""
    pool = IDPool()
    cnf = CNF()
    m = len(edges)
    eidx = {e: i for i, e in enumerate(edges)}
    inc = [[] for _ in range(n)]
    for e in edges:
        inc[e[0]].append(e)
        inc[e[1]].append(e)

    def X(e, c):
        return pool.id(("x", eidx[e], c))

    def R(c, v):
        return pool.id(("r", c, v))

    def A(c, v, d):
        return pool.id(("a", c, v, d))

    # each edge exactly one color
    for e in edges:
        lits = [X(e, c) for c in range(k)]
        cnf.append(lits)
        for c1, c2 in combinations(range(k), 2):
            cnf.append([-X(e, c1), -X(e, c2)])

    # degree in each class is 0 or 2
    for v in range(n):
        for c in range(k):
            lits = [X(e, c) for e in inc[v]]
            # at most 2
            cnf.extend(CardEnc.atmost(lits, bound=2, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
            # not exactly one: x(e,c) -> OR of other incident edges in c
            for e in inc[v]:
                cnf.append([-X(e, c)] + [X(f, c) for f in inc[v] if f != e])

    # r[c][v] <-> v incident to a c-colored edge
    for v in range(n):
        for c in range(k):
            lits = [X(e, c) for e in inc[v]]
            cnf.append([-R(c, v)] + lits)
            for l in lits:
                cnf.append([R(c, v), -l])

    # connectivity ladder
    D = n - 1
    for c in range(k):
        for v in range(n):
            # a[c][v][0] <-> (r[c][v] and no smaller r[c][u])
            a0 = A(c, v, 0)
            cnf.append([-a0, R(c, v)])
            for u in range(v):
                cnf.append([-a0, -R(c, u)])
            cnf.append([a0, -R(c, v)] + [R(c, u) for u in range(v)])
        for d in range(1, D + 1):
            for v in range(n):
                # a[c][v][d] -> a[c][v][d-1] OR exists nbr u: x(uv,c) & a[c][u][d-1]
                clause = [-A(c, v, d), A(c, v, d - 1)]
                for e in inc[v]:
                    u = e[0] if e[1] == v else e[1]
                    y = pool.id(("y", c, eidx[e], v, d))
                    cnf.append([-y, X(e, c)])
                    cnf.append([-y, A(c, u, d - 1)])
                    clause.append(y)
                cnf.append(clause)
        for v in range(n):
            cnf.append([-R(c, v), A(c, v, D)])

    # symmetry breaking between colors
    for i, e in enumerate(edges):
        for c in range(i + 1, k):
            cnf.append([-X(e, c)])
        for c in range(1, k):
            if c <= i:
                cnf.append([-X(e, c)] + [X(edges[j], c - 1) for j in range(i)])
    return cnf, pool, eidx


def decompose_le_k(n, edges, k, return_model=False):
    """Return (sat, coloring or None). sat=True => decomposition into <=k cycles."""
    edges = [tuple(sorted(e)) for e in edges]
    cnf, pool, eidx = build_cnf(n, edges, k)
    with Cadical153(bootstrap_with=cnf.clauses) as s:
        if not s.solve():
            return False, None
        if not return_model:
            return True, None
        model = set(l for l in s.get_model() if l > 0)
        coloring = {}
        for e in edges:
            for c in range(k):
                if pool.id(("x", eidx[e], c)) in model:
                    coloring[e] = c
        return True, coloring


def min_cycles_sat(n, edges, kmax):
    """Smallest k <= kmax with a <=k-cycle decomposition, else None."""
    for k in range(1, kmax + 1):
        sat, _ = decompose_le_k(n, edges, k)
        if sat:
            return k
    return None

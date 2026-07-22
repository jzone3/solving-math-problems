#!/usr/bin/env python3
"""Independent verifier for counterexamples to Brandt's regular-supergraph
conjecture as stated on West's open problem page
(https://dwest.web.illinois.edu/openp/regsup.html):

    If G is maximal triangle-free with minimum degree >= n(G)/3, then G has a
    regular supergraph obtainable by vertex multiplications.

A vertex multiplication replaces each vertex v by an independent set of
x_v >= 1 twin copies inheriting v's neighborhood.  The blowup is d-regular
iff  sum_{u in N(v)} x_u = d  for every v, i.e.  A x = d*1  with A the
adjacency matrix.  Since A is integral, a rational solution x > 0 of
A x = lambda*1 scales to an integral one, so G is a counterexample iff
there is NO real x > 0 with A x = lambda*1 (lambda is automatically > 0).

Farkas-style certificate of nonexistence: an integer vector y with
    (1) A y >= 0 componentwise,
    (2) sum_v y_v = 0,
    (3) sum_v (A y)_v > 0   (equivalently deg . y > 0, so A y != 0).
Proof: if x > 0 and A x = lambda*1 then
    0 = lambda * (1^T y) = (A x)^T y = x^T (A y) > 0,
the last inequality because x > 0, A y >= 0 and A y != 0.  Contradiction.

For each witness below the script checks, using only exact integer
arithmetic and the Python standard library:
    - the graph decodes from graph6 and is triangle-free,
    - it is maximal triangle-free (every non-adjacent pair has a common
      neighbor),
    - min degree * 3 >= n,
    - the certificate y satisfies (1),(2),(3),
    - belt-and-braces: exhaustive DFS confirms no integral x with
      1 <= x_v <= 8 and A x = d*1 for any d (redundant with the Farkas
      proof, but independent of it).
Prints PASS iff every witness verifies.
"""
import sys
from itertools import combinations

# (graph6, Farkas certificate y) -- minimum order n=12, delta=4=n/3.
WITNESSES = [
    ("K??FCo]XVw^_", [0, 1, 0, 1, 0, 0, -1, -1, -1, -1, 1, 1]),
    ("K?AFE_]JVoN_", [1, 0, 0, 0, 0, 1, -1, -1, -1, -1, 1, 1]),  # twin-free
    ("K?AFCo]XVoN_", [1, 0, 0, 0, 0, 1, -1, -1, -1, -1, 1, 1]),
    ("K?BDF?{UfoBw", [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 1, 1]),
    ("K?BD?{{Ufo^?", [1, -1, -1, 1, 1, -1, -1, 1, -1, -1, 1, 1]),
    # n=15, delta=5=n/3, chromatic number 4 (not 3-colorable):
    ("N??E@_NMeIfo{GrO^_?", [-1, 0, -1, 0, 1, 1, -1, -1, 2, 1, 1, -2, 0, -2, 2]),
]


def parse_graph6(s):
    data = [ord(c) - 63 for c in s.strip()]
    n = data[0]
    bits = []
    for b in data[1:]:
        bits.extend(((b >> k) & 1) for k in range(5, -1, -1))
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, adj


def check_witness(g6, y):
    n, adj = parse_graph6(g6)
    assert len(y) == n, "certificate length mismatch"
    # triangle-free
    for u, v in combinations(range(n), 2):
        if v in adj[u]:
            assert not (adj[u] & adj[v]), f"triangle at {u},{v}"
    # maximal: every non-adjacent pair has a common neighbor
    for u, v in combinations(range(n), 2):
        if v not in adj[u]:
            assert adj[u] & adj[v], f"non-adjacent {u},{v} lack common neighbor"
    # minimum degree >= n/3
    assert all(3 * len(adj[v]) >= n for v in range(n)), "min degree < n/3"
    # Farkas certificate
    Ay = [sum(y[u] for u in adj[v]) for v in range(n)]
    assert sum(y) == 0, "sum y != 0"
    assert all(t >= 0 for t in Ay), "A y has a negative entry"
    assert sum(Ay) > 0, "A y is zero"
    # independent exhaustive double check: no x in {1..B}^n with A x constant
    assert not exists_small_solution(n, adj, 8), "found small regular blowup?!"
    return n


def exists_small_solution(n, adj, B):
    degs = [len(adj[v]) for v in range(n)]
    dmax = B * max(degs)
    for d in range(min(degs), dmax + 1):
        x = [0] * n
        psum = [0] * n          # sum of assigned neighbors of w
        rem = degs[:]           # number of unassigned neighbors of w

        def assign(v, val):
        # returns list of (vertex, value) actually assigned (for undo), or None on conflict
            trail = [(v, val)]
            x[v] = val
            for w in adj[v]:
                psum[w] += val
                rem[w] -= 1
            queue = [v]
            while queue:
                _ = queue.pop()
                # unit propagation: any w with all-but-one neighbor assigned forces the last
                for w in range(n):
                    if psum[w] + rem[w] > d or psum[w] + rem[w] * B < d:
                        return trail, False
                progressed = True
                while progressed:
                    progressed = False
                    for w in range(n):
                        if rem[w] == 1:
                            u = next(u for u in adj[w] if x[u] == 0)
                            forced = d - psum[w]
                            if not (1 <= forced <= B):
                                return trail, False
                            trail.append((u, forced))
                            x[u] = forced
                            for t in adj[u]:
                                psum[t] += forced
                                rem[t] -= 1
                            if any(psum[t] + rem[t] > d or psum[t] + rem[t] * B < d
                                   for t in adj[u]):
                                return trail, False
                            progressed = True
            return trail, True

        def undo(trail):
            for v, val in reversed(trail):
                x[v] = 0
                for w in adj[v]:
                    psum[w] -= val
                    rem[w] += 1

        def dfs():
            v = next((u for u in range(n) if x[u] == 0), None)
            if v is None:
                return all(psum[w] == d for w in range(n))
            # prefer a vertex adjacent to a nearly-complete constraint
            for val in range(1, B + 1):
                trail, ok = assign(v, val)
                if ok and dfs():
                    return True
                undo(trail)
            return False

        if dfs():
            return True
    return False


def main():
    for g6, y in WITNESSES:
        n = check_witness(g6, y)
        print(f"verified counterexample {g6} (n={n})")
    print("PASS")


if __name__ == "__main__":
    main()

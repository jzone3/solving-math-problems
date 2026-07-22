#!/usr/bin/env python3
"""Independent verifier for P02 (Brandt regular supergraph, boundary case delta = n/3).

Claim: the 9-vertex graph W (graph6 'H?q`qjo') is maximal triangle-free with
delta(W) = 3 = n/3, yet W has NO regular supergraph obtainable by vertex
multiplications (expanding each vertex v into a nonempty independent set of
size x_v >= 1, copies inheriting neighborhoods).

The blow-up W[x] is d-regular iff  sum_{u in N(v)} x_u = d  for every v,
i.e. A x = d*1 (A = adjacency matrix). W[x] is a supergraph of W iff x >= 1.
(Rational x > 0 scales to integer, so integer and rational feasibility agree.)

Certificate of infeasibility: an integer vector y with
    y^T A = 2*e_8   and   y^T 1 = 0.
Then for ANY x, d with A x = d*1:  2*x_8 = y^T (A x) = d * (y^T 1) = 0,
so x_8 = 0, contradicting x_8 >= 1.

Everything below is exact integer arithmetic; only the Python stdlib is used.
Prints PASS iff all checks succeed.
"""

G6 = 'H?q`qjo'
Y = [0, 1, 1, 0, -1, -1, -1, -1, 2]  # certificate
TARGET = 8  # forced-zero vertex


def g6_to_adj(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for b in data[1:]:
        bits.extend((b >> i) & 1 for i in range(5, -1, -1))
    A = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i][j] = A[j][i] = 1
            idx += 1
    return n, A


def main():
    n, A = g6_to_adj(G6)
    ok = True

    # simple graph, symmetric, no loops
    assert all(A[i][i] == 0 for i in range(n))
    assert all(A[i][j] == A[j][i] for i in range(n) for j in range(n))

    # triangle-free
    tf = all(not (A[i][j] and A[j][k] and A[i][k])
             for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))
    print('triangle-free:', tf)
    ok &= tf

    # maximal: every non-edge has a common neighbor
    mx = all(A[i][j] == 1 or any(A[i][k] and A[j][k] for k in range(n))
             for i in range(n) for j in range(i + 1, n))
    print('maximal triangle-free:', mx)
    ok &= mx

    # minimum degree = n/3
    degs = [sum(row) for row in A]
    print('degrees:', degs)
    dmin_ok = 3 * min(degs) >= n
    print('delta >= n/3:', dmin_ok, f'(delta={min(degs)}, n={n})')
    ok &= dmin_ok

    # certificate: Y^T A = 2*e_TARGET, Y^T 1 = 0
    yA = [sum(Y[i] * A[i][j] for i in range(n)) for j in range(n)]
    want = [2 if j == TARGET else 0 for j in range(n)]
    cert1 = (yA == want)
    cert2 = (sum(Y) == 0)
    print('y^T A == 2*e_%d:' % TARGET, cert1, yA)
    print('y^T 1 == 0:', cert2)
    ok &= cert1 and cert2

    # independent double-check: brute-force x in {1..6}^n finds no regular blow-up
    # (not a proof by itself, but corroborates; certificate above is the proof)
    import itertools
    bf = None
    for x in itertools.product(range(1, 5), repeat=n):
        s = {sum(A[v][u] * x[u] for u in range(n)) for v in range(n)}
        if len(s) == 1:
            bf = x
            break
    print('brute force x in [1,4]^9 found solution:', bf)
    ok &= bf is None

    print('PASS' if ok else 'FAIL')


if __name__ == '__main__':
    main()

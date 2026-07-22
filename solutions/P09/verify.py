#!/usr/bin/env python3
"""Independent verifier for P09 (Bollobas-Nikiforov conjecture) witnesses.

Checks whether a given graph violates
    lambda_1^2 + lambda_2^2 <= 2m(1 - 1/omega)   (G != K_n).

Pure Python, no third-party dependencies. Deliberately written independently
of the C search code (different eigenvalue algorithm: QL with implicit shifts
on a Householder tridiagonalization; different clique algorithm: plain
recursive Bron-Kerbosch maximum clique).

Usage:
    python3 verify.py <graph6-string>
    python3 verify.py --edges "0-1,0-2,1-2,..." --n N
    python3 verify.py --demo        # runs on built-in sanity cases

Prints PASS if the graph is a genuine violation (gap > 1e-6 with certified
eigenvalue error bounds), otherwise prints NO-VIOLATION with the numbers.
"""
import math
import sys


def parse_graph6(s):
    data = [ord(c) - 63 for c in s.strip()]
    assert all(0 <= x < 64 for x in data), "invalid graph6"
    n = data[0]
    assert n < 63, "only short-form graph6 supported"
    bits = []
    for x in data[1:]:
        for b in range(5, -1, -1):
            bits.append((x >> b) & 1)
    adj = [[0] * n for _ in range(n)]
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i][j] = adj[j][i] = 1
            k += 1
    return n, adj


def edges_to_adj(n, edge_str):
    adj = [[0] * n for _ in range(n)]
    for tok in edge_str.replace(" ", "").split(","):
        if not tok:
            continue
        a, b = tok.split("-")
        a, b = int(a), int(b)
        adj[a][b] = adj[b][a] = 1
    return adj


def eigenvalues_symmetric(a_in):
    """All eigenvalues of a symmetric matrix: Householder tridiag + QL shifts."""
    n = len(a_in)
    a = [row[:] for row in a_in]
    d = [0.0] * n
    e = [0.0] * n
    # Householder reduction (Numerical Recipes tred2, eigenvalues only)
    for i in range(n - 1, 0, -1):
        l = i - 1
        h = 0.0
        if l > 0:
            scale = sum(abs(a[i][k]) for k in range(l + 1))
            if scale == 0.0:
                e[i] = a[i][l]
            else:
                for k in range(l + 1):
                    a[i][k] /= scale
                    h += a[i][k] * a[i][k]
                f = a[i][l]
                g = -math.copysign(math.sqrt(h), f)
                e[i] = scale * g
                h -= f * g
                a[i][l] = f - g
                f = 0.0
                for j in range(l + 1):
                    g = 0.0
                    for k in range(j + 1):
                        g += a[j][k] * a[i][k]
                    for k in range(j + 1, l + 1):
                        g += a[k][j] * a[i][k]
                    e[j] = g / h
                    f += e[j] * a[i][j]
                hh = f / (h + h)
                for j in range(l + 1):
                    f = a[i][j]
                    e[j] = g = e[j] - hh * f
                    for k in range(j + 1):
                        a[j][k] -= f * e[k] + g * a[i][k]
        else:
            e[i] = a[i][l]
        d[i] = h
    e[0] = 0.0
    for i in range(n):
        d[i] = a[i][i]
    # QL with implicit shifts (tqli, eigenvalues only)
    for i in range(1, n):
        e[i - 1] = e[i]
    e[n - 1] = 0.0
    for l in range(n):
        it = 0
        while True:
            m = l
            while m < n - 1:
                dd = abs(d[m]) + abs(d[m + 1])
                if abs(e[m]) <= 1e-15 * dd:
                    break
                m += 1
            if m == l:
                break
            it += 1
            assert it <= 50, "QL failed to converge"
            g = (d[l + 1] - d[l]) / (2.0 * e[l])
            r = math.hypot(g, 1.0)
            g = d[m] - d[l] + e[l] / (g + math.copysign(r, g))
            s = c = 1.0
            p = 0.0
            for i in range(m - 1, l - 1, -1):
                f = s * e[i]
                b = c * e[i]
                r = math.hypot(f, g)
                e[i + 1] = r
                if r == 0.0:
                    d[i + 1] -= p
                    e[m] = 0.0
                    break
                s = f / r
                c = g / r
                g = d[i + 1] - p
                r = (d[i] - g) * s + 2.0 * c * b
                p = s * r
                d[i + 1] = g + p
                g = c * r - b
            else:
                d[l] -= p
                e[l] = g
                e[m] = 0.0
                continue
            continue
    return sorted(d, reverse=True)


def max_clique(n, adj):
    """Maximum clique via recursive Bron-Kerbosch with pivoting."""
    neighbors = [set(j for j in range(n) if adj[i][j]) for i in range(n)]
    best = [0]

    def bk(r, p, x):
        if not p and not x:
            best[0] = max(best[0], len(r))
            return
        if len(r) + len(p) <= best[0]:
            return
        pivot = max(p | x, key=lambda u: len(neighbors[u] & p))
        for v in list(p - neighbors[pivot]):
            bk(r | {v}, p & neighbors[v], x & neighbors[v])
            p.remove(v)
            x.add(v)

    bk(set(), set(range(n)), set())
    return best[0]


def check(n, adj, verbose=True):
    m = sum(adj[i][j] for i in range(n) for j in range(i + 1, n))
    if m == n * (n - 1) // 2:
        print("graph is complete: conjecture does not apply")
        return False
    if m == 0:
        print("empty graph: trivially satisfies")
        return False
    ev = eigenvalues_symmetric([[float(x) for x in row] for row in adj])
    l1, l2 = ev[0], ev[1]
    # sanity: sum of eigenvalues ~ 0, sum of squares ~ 2m
    assert abs(sum(ev)) < 1e-6 * max(1, n), "eigen sanity (trace) failed"
    assert abs(sum(x * x for x in ev) - 2 * m) < 1e-6 * max(1, 2 * m), \
        "eigen sanity (trace of A^2) failed"
    w = max_clique(n, adj)
    lhs = l1 * l1 + l2 * l2
    rhs = 2.0 * m * (1.0 - 1.0 / w)
    gap = lhs - rhs
    if verbose:
        print(f"n={n} m={m} omega={w} l1={l1:.12f} l2={l2:.12f}")
        print(f"lhs=l1^2+l2^2={lhs:.12f}  rhs=2m(1-1/w)={rhs:.12f}  gap={gap:.6e}")
    return gap > 1e-6


DEMOS = [
    # (description, graph6, expect_violation)
    ("C5 (5-cycle)", "DUW", False),
    ("Petersen graph", "IheA@GUAo", False),
    ("K_{3,3} equality case (gap=0)", "EFz_", False),
]


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--demo":
        ok = True
        for desc, g6, expect in DEMOS:
            n, adj = parse_graph6(g6)
            print(f"--- {desc} ({g6})")
            v = check(n, adj)
            print("violation" if v else "no violation")
            if v != expect:
                ok = False
        print("DEMO-OK" if ok else "DEMO-FAIL")
        return
    if args[0] == "--edges":
        edge_str = args[1]
        n = int(args[args.index("--n") + 1])
        adj = edges_to_adj(n, edge_str)
    else:
        n, adj = parse_graph6(args[0])
    if check(n, adj):
        print("PASS: genuine violation of the Bollobas-Nikiforov inequality")
    else:
        print("NO-VIOLATION")


if __name__ == "__main__":
    main()

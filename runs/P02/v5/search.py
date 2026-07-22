#!/usr/bin/env python3
"""P02 V5: check Brandt's regular-supergraph conjecture on maximal
triangle-free graphs with delta >= n/3, focusing on the equality case
delta = n/3 (the only genuinely open residual class; see NOTES.md).

Pipeline: nauty-geng -t -d<k> <n>  ->  filter maximal triangle-free
(diameter <= 2)  ->  exact rational feasibility of
    { x_v >= 1,  sum_{u in N(v)} x_u = c  for all v }
via Phase-1 simplex over Fractions.  Feasibility of the rational system
with x_v >= 1 is equivalent to existence of an integer witness (scale by
the lcm of denominators; x_v >= 1 is preserved and c scales to integer d).

Output: for each graph, either an exact integer witness (x, d) written to
witnesses.jsonl, or "INFEASIBLE" plus a Farkas certificate -> counterexample!
"""
import sys, json, subprocess
from fractions import Fraction

def g6_to_adj(line):
    data = [ord(ch) - 63 for ch in line.strip()]
    n = data[0]
    bits = []
    for b in data[1:]:
        bits.extend([(b >> s) & 1 for s in range(5, -1, -1)])
    adj = [[0] * n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i][j] = adj[j][i] = 1
            idx += 1
    return n, adj

def is_maximal_tf(n, adj):
    # triangle-free guaranteed by geng -t; maximal iff diameter <= 2
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j]:
                continue
            if not any(adj[i][k] and adj[j][k] for k in range(n)):
                return False
    return True

def phase1_simplex(A_rows, b):
    """Solve min sum(artificials) s.t. A y = b, y >= 0 (b >= 0), exact Fractions.
    Returns (feasible, y_solution or dual_certificate)."""
    m = len(A_rows); nv = len(A_rows[0])
    # tableau: columns = nv original + m artificial + rhs
    T = [[Fraction(x) for x in row] + [Fraction(1) if i == j else Fraction(0) for j in range(m)] + [Fraction(b[i])] for i, row in enumerate(A_rows)]
    basis = [nv + i for i in range(m)]
    # objective row: minimize sum artificials => reduced costs
    obj = [Fraction(0)] * (nv + m + 1)
    for i in range(m):
        for j in range(nv + m + 1):
            obj[j] -= T[i][j]
    for i in range(m):
        obj[nv + i] += 1  # artificial vars have cost 1
    while True:
        piv_col = -1
        for j in range(nv + m):
            if obj[j] < 0:
                piv_col = j; break
        if piv_col == -1:
            break
        piv_row, best = -1, None
        for i in range(m):
            if T[i][piv_col] > 0:
                ratio = T[i][-1] / T[i][piv_col]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[piv_row]):
                    best = ratio; piv_row = i  # Bland's rule: avoid cycling
        if piv_row == -1:
            break  # unbounded (cannot happen in phase 1)
        pv = T[piv_row][piv_col]
        T[piv_row] = [v / pv for v in T[piv_row]]
        for i in range(m):
            if i != piv_row and T[i][piv_col] != 0:
                f = T[i][piv_col]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[piv_row])]
        if obj[piv_col] != 0:
            f = obj[piv_col]
            obj = [a - f * bb for a, bb in zip(obj, T[piv_row])]
        basis[piv_row] = piv_col
    opt = -obj[-1]
    if opt == 0:
        y = [Fraction(0)] * (nv + m)
        for i, bcol in enumerate(basis):
            y[bcol] = T[i][-1]
        return True, y[:nv]
    # infeasible: Farkas certificate from obj row over artificial columns
    cert = [obj[nv + i] + 1 for i in range(m)]  # dual multipliers
    return False, cert

def check_graph(n, adj):
    deg = [sum(row) for row in adj]
    # variables: y_v = x_v - 1 >= 0 (n vars), c' where c = c' (>=0)
    # equations: c - sum_{u in N(v)} x_u = 0  ->  c' - sum A[v] y = deg[v]
    A_rows, b = [], []
    for v in range(n):
        row = [Fraction(-adj[v][u]) for u in range(n)] + [Fraction(1)]
        A_rows.append(row); b.append(Fraction(deg[v]))
    # phase-1 needs b>=0 and works with y>=0, c'>=0
    feas, sol = phase1_simplex(A_rows, b)
    if not feas:
        return None
    y, cp = sol[:n], sol[n]
    x = [yi + 1 for yi in y]
    # scale to integers
    from math import lcm
    L = lcm(*[f.denominator for f in x + [cp]])
    xi = [int(f * L) for f in x]
    d = int(cp * L)
    # verify
    for v in range(n):
        assert sum(xi[u] for u in range(n) if adj[v][u]) == d
        assert xi[v] >= L >= 1
    return xi, d

def main():
    n = int(sys.argv[1]); mindeg = int(sys.argv[2])
    out = open(f"witnesses_n{n}_d{mindeg}.jsonl", "w")
    p = subprocess.Popen(["nauty-geng", "-q", "-t", f"-d{mindeg}", str(n)],
                         stdout=subprocess.PIPE, text=True)
    total = mtf = 0; bad = []
    for line in p.stdout:
        total += 1
        nn, adj = g6_to_adj(line)
        if not is_maximal_tf(nn, adj):
            continue
        mtf += 1
        res = check_graph(nn, adj)
        if res is None:
            bad.append(line.strip())
            print("INFEASIBLE:", line.strip(), flush=True)
        else:
            xi, d = res
            out.write(json.dumps({"g6": line.strip(), "x": xi, "d": d}) + "\n")
    out.close()
    print(f"n={n} mindeg={mindeg}: geng_output={total} maximal_tf={mtf} infeasible={len(bad)}", flush=True)

if __name__ == "__main__":
    main()

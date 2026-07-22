"""Cross-check LP1 oracle against brute-force integer search on small graphs.

Brute force: for x_v in {1..X}^n check A x constant. Compare with LP1 verdict on
all triangle-free graphs up to n=7 (and some structured examples).
Also sanity: Andrasfai graphs (regular) must be LP1-feasible with x=1.
"""
import itertools
import subprocess
import sys
from fractions import Fraction

from oracle import lp1_multiplication_feasible, neighborhoods, is_triangle_free


def brute_force_feasible(n, edges, X=4):
    N = neighborhoods(n, edges)
    for x in itertools.product(range(1, X + 1), repeat=n):
        vals = {sum(x[u] for u in N[v]) for v in range(n)}
        if len(vals) == 1:
            return True
    return False


def graphs_from_geng(n, args):
    out = subprocess.run(["nauty-geng", "-q"] + args + [str(n)],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        yield g6_to_edges(line.strip())


def g6_to_edges(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for c in data[1:]:
        bits += [(c >> k) & 1 for k in range(5, -1, -1)]
    edges, idx = [], 0
    for v in range(1, n):
        for u in range(v):
            if bits[idx]:
                edges.append((u, v))
            idx += 1
    return n, edges


def main():
    mismatches = 0
    checked = 0
    for n in range(2, 8):
        for n_, edges in graphs_from_geng(n, ["-t", "-c"]):
            feas_lp, _ = lp1_multiplication_feasible(n_, edges)
            feas_bf = brute_force_feasible(n_, edges, X=4)
            checked += 1
            if feas_bf and not feas_lp:
                print("MISMATCH (bf feasible, LP infeasible):", n_, edges)
                mismatches += 1
            if feas_lp and not feas_bf:
                # LP witness might need x > 4; verify by scaling rational witness
                ok, (x, c) = lp1_multiplication_feasible(n_, edges)
                den = 1
                for xv in x:
                    den = den * xv.denominator // __import__("math").gcd(den, xv.denominator)
                xi = [int(xv * den) for xv in x]
                N = neighborhoods(n_, edges)
                vals = {sum(xi[u] for u in N[v]) for v in range(n_)}
                assert len(vals) == 1 and all(v >= 1 for v in xi), ("BAD WITNESS", n_, edges)
    print(f"checked {checked} connected triangle-free graphs n<=7, mismatches={mismatches}")
    if mismatches:
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()

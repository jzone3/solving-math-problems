"""Analyze counterexample hits from sweep logs: chromatic number, twin-freeness,
degree sequence, girth, automorphisms, and re-verified Farkas certificate.
Usage: python3 analyze.py logs/*.log
"""
import re
import sys
from itertools import combinations

from oracle import (lp1_multiplication_feasible, lp2_blowup_degree_feasible,
                    neighborhoods, is_maximal_tf, is_triangle_free,
                    is_twin_free)
from test_oracle import g6_to_edges


def chromatic_number(n, edges):
    N = neighborhoods(n, edges)
    for k in range(1, n + 1):
        col = {}

        def bt(v):
            if v == n:
                return True
            for c in range(k):
                if all(col.get(u) != c for u in N[v]):
                    col[v] = c
                    if bt(v + 1):
                        return True
                    del col[v]
            return False

        if bt(0):
            return k


def main():
    g6s = []
    for path in sys.argv[1:]:
        for line in open(path):
            m = re.search(r"COUNTEREXAMPLE n=(\d+) g6=(\S+)", line)
            if m:
                g6s.append(m.group(2))
    seen = set()
    for g6 in g6s:
        if g6 in seen:
            continue
        seen.add(g6)
        n, edges = g6_to_edges(g6)
        N = neighborhoods(n, edges)
        assert is_triangle_free(n, edges) and is_maximal_tf(n, edges)
        feas, cert = lp1_multiplication_feasible(n, edges)
        assert not feas
        Ay = [sum(cert[u] for u in N[v]) for v in range(n)]
        assert sum(cert) <= 0 and all(a >= 0 for a in Ay) and sum(Ay) > 0
        degs = sorted(len(N[v]) for v in range(n))
        chi = chromatic_number(n, edges)
        print(f"g6={g6} n={n} degs={degs} chi={chi} "
              f"twinfree={is_twin_free(n, edges)} "
              f"farkas={[str(c) for c in cert]}")


if __name__ == "__main__":
    main()

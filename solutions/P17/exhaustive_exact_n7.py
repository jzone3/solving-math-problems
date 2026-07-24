#!/usr/bin/env python3
"""Exhaustive exact certification of WoW 20 & 21 for ALL graphs with n <= 7
vertices (nauty-geng enumeration, 1 + 2 + 4 + 11 + 34 + 156 + 1044 graphs).
No floats on the accept path: reuses the exact Sturm/rational-isolation
certifier from verify_corollary.py. Prints PASS iff every graph satisfies
max{n+, n-} <= sum of positive eigenvalues (exactly)."""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_corollary import inertia_and_S_cert

def g6_to_adj(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]
    bits = []
    for d in data[1:]:
        bits += [(d >> (5 - i)) & 1 for i in range(6)]
    A = [[0] * n for _ in range(n)]
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i][j] = A[j][i] = bits[k]; k += 1
    return n, A

def main():
    bad = total = 0
    for n in range(1, 8):
        out = subprocess.run(["nauty-geng", "-q", str(n)],
                             capture_output=True, text=True, check=True)
        cnt = 0
        for line in out.stdout.splitlines():
            nn, A = g6_to_adj(line)
            npos, nneg, cert = inertia_and_S_cert(A, nn)
            if not cert(max(npos, nneg)):
                print("VIOLATION:", line); bad += 1
            cnt += 1
        total += cnt
        print(f"n={n}: {cnt} graphs certified")
    print(f"total {total} graphs;", "PASS" if bad == 0 else f"FAIL ({bad})")

if __name__ == "__main__":
    main()

"""Exhaustive check of Graffiti 39/40 + proof-chain lemma over graph6 input (stdin).

Usage: nauty-geng -c N | python3 exhaust.py
       nauty-gentreeg N | python3 exhaust.py
Prints running best scores and any violation immediately.
"""
import sys
import numpy as np
from harness import invariants


def parse_graph6(line):
    line = line.strip()
    if line.startswith(">>graph6<<"):
        line = line[10:]
    data = [ord(c) - 63 for c in line]
    n = data[0]
    assert n < 63
    bits = []
    for b in data[1:]:
        for k in range(5, -1, -1):
            bits.append((b >> k) & 1)
    adj = [[] for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].append(j)
                adj[j].append(i)
            idx += 1
    return n, adj


def parse_sparse6(line):
    raise NotImplementedError


def main():
    best39 = -1e18
    best40 = -1e18
    best39_g = best40_g = None
    count = 0
    lemma_fail = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, adj = parse_graph6(line)
        inv = invariants(adj, n)
        if inv is None:
            continue
        count += 1
        s39 = inv["dev"] - inv["npos"]
        s40 = inv["dev"] - inv["nneg"]
        d = inv["diam"]
        if inv["dev"] > d / 2 + 1e-9 or (d + 1) // 2 > min(inv["npos"], inv["nneg"]):
            lemma_fail += 1
            print("LEMMA FAIL", line, inv, flush=True)
        if s39 > best39:
            best39, best39_g = s39, line
        if s40 > best40:
            best40, best40_g = s40, line
        if s39 > 1e-5 or s40 > 1e-5:
            print("VIOLATION", line, inv, flush=True)
    print(f"checked={count} lemma_fail={lemma_fail}")
    print(f"best39={best39:.6f} g6={best39_g}")
    print(f"best40={best40:.6f} g6={best40_g}")


if __name__ == "__main__":
    main()

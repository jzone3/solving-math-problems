#!/usr/bin/env python3
"""Second, independently written BTD verifier (different implementation style
from verify.py: numpy-free, checks via multiset/counter arithmetic).

Usage: verify2.py V B p1 p2 R K L witness_file  -> prints PASS or FAIL
"""
import sys
from collections import Counter


def main():
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    rows = []
    with open(sys.argv[8]) as f:
        for line in f:
            if line.strip():
                rows.append([int(t) for t in line.split()])
    assert len(rows) == V and all(len(r) == B for r in rows), "shape"
    assert all(x in (0, 1, 2) for r in rows for x in r), "entries"
    assert R == p1 + 2 * p2, "params"
    for r in rows:
        c = Counter(r)
        assert c[1] == p1 and c[2] == p2, "row multiplicity counts"
    for j in range(B):
        assert sum(rows[i][j] for i in range(V)) == K, f"col {j}"
    # pairwise via per-block expansion of multiset pairs
    pair = Counter()
    for j in range(B):
        blk = [(i, rows[i][j]) for i in range(V) if rows[i][j]]
        for a in range(len(blk)):
            for b in range(a + 1, len(blk)):
                (u, mu), (v, mv) = blk[a], blk[b]
                pair[(u, v)] += mu * mv
    for u in range(V):
        for v in range(u + 1, V):
            assert pair[(u, v)] == L, f"pair {(u, v)} = {pair[(u, v)]}"
    print("PASS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)

#!/usr/bin/env python3
"""Independent pure-CNF encoding of (v,6,1)-PMD existence (cross-check for CP-SAT).

Written deliberately from scratch (different structure from pmd_cpsat.py).
Variables: x[b][p][s] (block b, position p in 0..5, symbol s).
Clauses:
  - each cell exactly one symbol (ALO + pairwise AMO)
  - each symbol at most once per block
  - for each t in 1..5 and ordered pair (u,w): exactly one incidence,
    via Tseitin product vars e[(b,p)] with pairwise AMO + ALO
Symmetry breaking (sound, minimal):
  - block 0 = (0,1,2,3,4,5) (unit clauses)
  - every block: position 0 holds the block minimum (forbid x[b][0][s] & x[b][p][s'] , s'<=s isn't
    needed for s'==s since distinct-in-block; forbid s' < s)
  - blocks 0..r-1 (r = v-1) are exactly the blocks containing symbol 0, at position 0;
    ordered strictly by position-1 symbol. Blocks r..b-1 do not contain 0,
    ordered (non-strictly) by position-0 symbol.

Usage: gen_cnf.py v out.cnf [--weak]
  --weak: only fix block 0 = (0..5); skip rotation-min and block-order breaking
          (for soundness cross-checks of UNSAT results).
"""
import sys

K = 6


def main(v, out, weak=False):
    b = v * (v - 1) // K
    r = v - 1  # blocks containing any fixed symbol
    nv = 0
    def new():
        nonlocal nv
        nv += 1
        return nv
    X = [[[new() for s in range(v)] for p in range(K)] for bl in range(b)]
    cls = []
    for bl in range(b):
        for p in range(K):
            cls.append([X[bl][p][s] for s in range(v)])
            for s1 in range(v):
                for s2 in range(s1 + 1, v):
                    cls.append([-X[bl][p][s1], -X[bl][p][s2]])
        for s in range(v):
            for p1 in range(K):
                for p2 in range(p1 + 1, K):
                    cls.append([-X[bl][p1][s], -X[bl][p2][s]])
    for t in range(1, K):
        for u in range(v):
            for w in range(v):
                if u == w:
                    continue
                es = []
                for bl in range(b):
                    for p in range(K):
                        e = new()
                        a1, a2 = X[bl][p][u], X[bl][(p + t) % K][w]
                        cls.append([-e, a1])
                        cls.append([-e, a2])
                        cls.append([e, -a1, -a2])
                        es.append(e)
                cls.append(es)  # at least one
                for i in range(len(es)):
                    for j in range(i + 1, len(es)):
                        cls.append([-es[i], -es[j]])
    # symmetry breaking
    for p in range(K):
        cls.append([X[0][p][p]])
    if weak:
        with open(out, "w") as f:
            f.write(f"p cnf {nv} {len(cls)}\n")
            for c in cls:
                f.write(" ".join(map(str, c)) + " 0\n")
        print(f"v={v} b={b} vars={nv} clauses={len(cls)} (weak)")
        return
    for bl in range(b):
        for p in range(1, K):
            for s in range(v):
                for s2 in range(s):  # position p symbol s2 < position 0 symbol s: forbid
                    cls.append([-X[bl][0][s], -X[bl][p][s2]])
    # blocks 0..r-1 start with 0; blocks r.. don't contain 0
    for bl in range(r):
        cls.append([X[bl][0][0]])
    for bl in range(r, b):
        for p in range(K):
            cls.append([-X[bl][p][0]])
    # order blocks 0..r-1 strictly by position-1 symbol
    for bl in range(r - 1):
        for s in range(v):
            for s2 in range(1, s + 1):
                cls.append([-X[bl][1][s], -X[bl + 1][1][s2]])
    # order blocks r..b-1 non-strictly by position-0 symbol
    for bl in range(r, b - 1):
        for s in range(v):
            for s2 in range(1, s):
                cls.append([-X[bl][0][s], -X[bl + 1][0][s2]])
    with open(out, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")
    print(f"v={v} b={b} vars={nv} clauses={len(cls)}")


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2], "--weak" in sys.argv)

#!/usr/bin/env python3
"""Multiplicative construction of circular (n-1) x n Tuscan-2 arrays for
prime n, plus the cut trick to attempt an n x n Tuscan-2 SQUARE.

Rows: u * b (mod n) for u in Z_n^* where b = (b_0=0, b_1, ..., b_{n-1}) is a
circular arrangement of Z_n.  Pair (x,y) with x,y != 0 occurs at circular
distance d in row u at position c iff b_{c+d}/b_c = y/x (and u = x / b_c);
so each such pair occurs exactly once iff the n-2 nonzero distance-d ratios
b_{c+d}/b_c are pairwise distinct (values range over the n-2 elements of
Z_n^* \\ {1}... they are 9 slots for n=11: positions where both entries are
nonzero).  Pairs involving 0 are covered exactly once automatically.

Cut trick: cut each circular row once, losing one d1 pair and two d2 pairs
per row; if the n-1 lost d1 edges form a Hamiltonian path whose own d2 pairs
are among the lost d2 pairs, appending the path as a final row yields an
n x n Tuscan-2 square (all pair-uniqueness properties inherited).

Usage: python3 mult_circ.py n [max_arrays]
"""
import sys
from itertools import permutations


def find_bases(n):
    """circular sequences b, b[0]=0, distance-1 and distance-2 nonzero
    ratios distinct (mod n)."""
    inv = [0] * n
    for x in range(1, n):
        inv[x] = pow(x, n - 2, n)
    res = []
    b = [0] * n

    def rec(pos, used, r1, r2):
        if pos == n:
            # close circle: pairs (b[n-1], b[0]=0) involve 0: no ratio checks
            # d2 wrap pairs: (b[n-2], b[0]) and (b[n-1], b[1])
            e2 = b[1] * inv[b[n - 1]] % n
            if e2 == 1 or e2 in r2:
                return
            res.append(b[:])
            return
        for v in range(1, n):
            if used >> v & 1:
                continue
            ok = True
            ne1 = ne2 = None
            if pos >= 2:  # d1 ratio with previous (both nonzero)
                ne1 = v * inv[b[pos - 1]] % n
                if ne1 == 1 or ne1 in r1:
                    continue
            if pos >= 3:  # d2 ratio (both nonzero, no zero passed)
                ne2 = v * inv[b[pos - 2]] % n
                if ne2 == 1 or ne2 in r2:
                    continue
            if ne1 is not None:
                r1.add(ne1)
            if ne2 is not None:
                r2.add(ne2)
            b[pos] = v
            rec(pos + 1, used | 1 << v, r1, r2)
            if ne1 is not None:
                r1.discard(ne1)
            if ne2 is not None:
                r2.discard(ne2)

    rec(1, 1, set(), set())
    return res


def rows_from_base(n, b):
    return [[u * x % n for x in b] for u in range(1, n)]


def try_cuts(n, rows):
    """Path DFS with exact incremental d2 legality.

    Each ordered pair (x,y) occurs at circular distance 1 in exactly one row
    (edge location), and at distance 2 in exactly one row (span location).
    A path edge (path[d], path[d+1]) determines the cut of its row.  A path
    d2 pair p = (path[i], path[i+2]) at span (rp, cp..cp+2) is lost iff the
    cut of row rp is cp or cp+1, i.e. row rp's chosen edge is the one at
    position cp or cp+1.  We propagate these as constraints on rows.
    """
    m = n - 1
    cpos = [{r[c]: c for c in range(n)} for r in rows]
    # edge location: eloc[(x,y)] = (row, pos) with rows[row][pos..pos+1]=(x,y)
    eloc = {}
    sloc = {}
    for r in range(m):
        for c in range(n):
            eloc[(rows[r][c], rows[r][(c + 1) % n])] = (r, c)
            sloc[(rows[r][c], rows[r][(c + 2) % n])] = (r, c)

    rsel = [None] * m          # rsel[d] = row of edge d
    cutof = {}                 # row -> cut position (chosen edge position)
    allowed = {}               # row (unused) -> set of allowed cut positions
    path = []

    def extend(depth, cur, visited, usedrow):
        if depth == m:
            return True
        for nxt in range(n):
            if visited >> nxt & 1:
                continue
            e = eloc.get((cur, nxt))
            if e is None:
                continue
            r, c = e
            if usedrow >> r & 1:
                continue
            if r in allowed and c not in allowed[r]:
                continue
            # new d2 pair created: (path[-2], nxt) if depth >= 1
            new_constraint = None
            if depth >= 1:
                p = (path[-2], nxt)
                rp, cp = sloc[p]
                ok_positions = {cp, (cp + 1) % n}
                if rp == r:
                    if c not in ok_positions:
                        continue
                elif usedrow >> rp & 1:
                    if cutof[rp] not in ok_positions:
                        continue
                else:
                    prev = allowed.get(rp)
                    inter = ok_positions if prev is None else (prev & ok_positions)
                    if not inter:
                        continue
                    new_constraint = (rp, prev)
                    allowed[rp] = inter
            rsel[depth] = r
            cutof[r] = c
            old_allowed_r = allowed.pop(r, None)
            path.append(nxt)
            if extend(depth + 1, nxt, visited | 1 << nxt, usedrow | 1 << r):
                return True
            path.pop()
            del cutof[r]
            if old_allowed_r is not None:
                allowed[r] = old_allowed_r
            if new_constraint is not None:
                rp, prev = new_constraint
                if prev is None:
                    allowed.pop(rp, None)
                else:
                    allowed[rp] = prev
        return False

    for start in range(n):
        path[:] = [start]
        cutof.clear()
        allowed.clear()
        if extend(0, start, 1 << start, 0):
            sq = []
            for d in range(m):
                r = rsel[d]
                c = cpos[r][path[d]]
                sq.append([rows[r][(c + j) % n] for j in range(1, n + 1)])
            sq.append(path[:])
            return sq
    return None


def main():
    n = int(sys.argv[1])
    maxa = int(sys.argv[2]) if len(sys.argv) > 2 else None
    bases = find_bases(n)
    print(f"n={n}: {len(bases)} multiplicative circular Tuscan-2 bases",
          file=sys.stderr)
    for i, b in enumerate(bases if maxa is None else bases[:maxa]):
        rows = rows_from_base(n, b)
        sq = try_cuts(n, rows)
        if sq:
            print(f"SQUARE from base {b}", file=sys.stderr)
            for row in sq:
                print(" ".join(map(str, row)))
            return 0
        if i % 100 == 0:
            print(f"tried {i+1} bases, no conversion yet", file=sys.stderr)
    print("no conversion found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

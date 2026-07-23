#!/usr/bin/env python3
"""Exhaustive (complete) Kramer–Mesner decision for BTD(14,28;8,3,14;7,6)
with prescribed automorphism sigma = two 7-cycles, replacing the stalled
CP-SAT count-formulation (km_z7.py) with meet-in-the-middle enumeration.

Structure (see km_z7.py docstring): t block orbits of size 7 (t<=4) plus
n1/n2 fixed blocks (full point-orbit, multiplicity 1), 7t + n1 + n2 = 28.
Within-half pair-orbit targets force n1<=6, n2<=6, so n1+n2<=12 and hence
t=4 (n1=n2=0) or t=3 (n1+n2=7). We decide both cases exhaustively.

Signature of a base block = 17 nonneg ints:
 (c1(O1), c1(O2), c2(O1), c2(O2), A[13 pair orbits]).
Need a multiset of t signatures summing exactly to the (adjusted) target.

t=4: sorted quadruple (a<=b<=c<=d) <=> front pair (a,b) + back pair (c,d),
b<=c; hash join over pair-signature sums (coordinate-capped pruning first).
t=3: sorted triple <=> pair + single, join likewise.

Prints SOLUTION + witness or "NO sigma-invariant design (complete)".
"""
import itertools
import sys
from collections import defaultdict

import numpy as np

V, B, P1, P2, R, K, L = 14, 28, 8, 3, 14, 7, 6
sigma = [(i + 1) % 7 for i in range(7)] + [7 + (i + 1) % 7 for i in range(7)]
PAIR_REPS = ([(0, d) for d in (1, 2, 3)] + [(7, 7 + d) for d in (1, 2, 3)]
             + [(0, 7 + d) for d in range(7)])


def shift(m, k):
    return tuple(m[(i - k) % 7] for i in range(7)) + tuple(m[7 + (i - k) % 7] for i in range(7))


def signature(m):
    s = [sum(1 for i in range(7) if m[i] == 1),
         sum(1 for i in range(7, 14) if m[i] == 1),
         sum(1 for i in range(7) if m[i] == 2),
         sum(1 for i in range(7, 14) if m[i] == 2)]
    for (u, v) in PAIR_REPS:
        t = 0
        uu, vv = u, v
        for _ in range(7):
            t += m[uu] * m[vv]
            uu, vv = sigma[uu], sigma[vv]
        s.append(t)
    return tuple(s)


def enumerate_blocks():
    seen = set()
    reps = []
    for t2 in range(0, 4):
        n1 = 7 - 2 * t2
        for pos2 in itertools.combinations(range(14), t2):
            rest = [i for i in range(14) if i not in pos2]
            for pos1 in itertools.combinations(rest, n1):
                m = [0] * 14
                for i in pos2:
                    m[i] = 2
                for i in pos1:
                    m[i] = 1
                m = tuple(m)
                canon = min(shift(m, k) for k in range(7))
                if canon not in seen:
                    seen.add(canon)
                    reps.append(canon)
    return reps


def solve_case(S, idx, target, t):
    """S: (n,17) int16 array (already coordinate-capped <= target).
    Find sorted t-tuple of rows (indices into idx) summing to target.
    Returns list of original indices or None. Complete."""
    n = S.shape[0]
    T = np.array(target, dtype=np.int16)
    if t == 0:
        return [] if not target.any() else None
    # build pruned pair list (i<=j)
    pairs = []
    for i in range(n):
        s2 = S[i] + S[i:]
        ok = np.where((s2 <= T).all(axis=1))[0]
        for o in ok:
            pairs.append((i, i + int(o)))
    if t == 2:
        for (i, j) in pairs:
            if ((S[i] + S[j]) == T).all():
                return [idx[i], idx[j]]
        return None
    by_sum = defaultdict(list)
    for (i, j) in pairs:
        by_sum[(S[i] + S[j]).tobytes()].append((i, j))
    if t == 3:
        for i in range(n):
            rem = (T - S[i]).astype(np.int16)
            if (rem < 0).any():
                continue
            for (j, k) in by_sum.get(rem.tobytes(), []):
                if j >= i:
                    return [idx[i], idx[j], idx[k]]
        return None
    if t == 4:
        for (i, j) in pairs:
            rem = (T - S[i] - S[j]).astype(np.int16)
            if (rem < 0).any():
                continue
            for (k, l) in by_sum.get(rem.tobytes(), []):
                if k >= j:
                    return [idx[i], idx[j], idx[k], idx[l]]
        return None
    raise ValueError(t)


def main():
    reps = enumerate_blocks()
    SIG = np.array([signature(m) for m in reps], dtype=np.int16)
    print(f"{len(reps)} block-orbit representatives")
    base_target = [P1, P1, P2, P2] + [L] * 13

    solutions = None
    # case t=4, n1=n2=0
    cases = [(4, 0, 0)]
    # case t=3, n1+n2=7, n1,n2<=6
    cases += [(3, n1, 7 - n1) for n1 in range(1, 7)]
    for (t, n1, n2) in cases:
        tgt = list(base_target)
        tgt[0] -= n1   # c1(O1) from fixed type-1 blocks
        tgt[1] -= n2
        for pi in range(3):
            tgt[4 + pi] -= n1
        for pi in range(3, 6):
            tgt[4 + pi] -= n2
        tgt = np.array(tgt, dtype=np.int16)
        if (tgt < 0).any():
            print(f"case t={t} n1={n1} n2={n2}: target negative, skip")
            continue
        keep = np.where((SIG <= tgt).all(axis=1))[0]
        print(f"case t={t} n1={n1} n2={n2}: {len(keep)} candidate orbits")
        res = solve_case(SIG[keep], keep, tgt, t)
        if res is not None:
            print("SOLUTION:", res, "n1,n2 =", n1, n2)
            cols = []
            for r in res:
                for k in range(7):
                    cols.append(shift(reps[r], k))
            cols += [tuple([1] * 7 + [0] * 7)] * n1 + [tuple([0] * 7 + [1] * 7)] * n2
            rows = [" ".join(str(cols[j][i]) for j in range(B)) for i in range(V)]
            with open("witness-14-28-8-3-14-7-6.txt", "w") as f:
                f.write("\n".join(rows) + "\n")
            print("witness written")
            solutions = res
            break
    if solutions is None:
        print("NO sigma-invariant design exists (complete decision for two-7-cycle Z7)")


if __name__ == "__main__":
    main()

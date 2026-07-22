#!/usr/bin/env python3
"""Algebraic attack part 1: translate (terrace/sequencing) constructions.

A 'translate' T2(n) has rows {base + c mod n : c in Z_n}. Distance-1 exact
cover <=> first differences of base are a permutation of nonzero residues
(base is a directed terrace / sequencing of Z_n). Distance-2 at-most-once
<=> second-order differences s_{j+2}-s_j are pairwise distinct.

We exhaustively search for such '2-sequencings' of Z_n. For odd n Z_n is
not sequenceable (classical), so this construction cannot work for 11/13;
we machine-verify that, and confirm the construction WORKS for even n
(explaining why even T2(n) are easy).
"""
import sys
from itertools import permutations


def search(n, need_second=True, limit=1):
    """DFS for s_0=0, s_1,... perm of Z_n with distinct first diffs
    (and distinct second diffs if need_second). Returns list of found."""
    found = []
    s = [0]
    used = [False] * n
    used[0] = True
    d1 = [False] * n
    d2 = [False] * n

    def rec():
        if len(found) >= limit:
            return
        if len(s) == n:
            found.append(list(s))
            return
        for x in range(1, n):
            if used[x]:
                continue
            f = (x - s[-1]) % n
            if d1[f]:
                continue
            g = None
            if need_second and len(s) >= 2:
                g = (x - s[-2]) % n
                if d2[g]:
                    continue
            used[x] = True
            d1[f] = True
            if g is not None:
                d2[g] = True
            s.append(x)
            rec()
            s.pop()
            used[x] = False
            d1[f] = False
            if g is not None:
                d2[g] = False

    rec()
    return found


def translate_square(base, n):
    return [[(x + c) % n for x in base] for c in range(n)]


if __name__ == "__main__":
    sys.path.insert(0, ".")
    from t2lib import check_t2

    for n in range(2, 15):
        seqs = search(n, need_second=False, limit=1)
        seq2 = search(n, need_second=True, limit=1)
        msg = f"n={n}: sequencing={'YES' if seqs else 'NO'} 2-sequencing={'YES' if seq2 else 'NO'}"
        if seq2:
            sq = translate_square(seq2[0], n)
            msg += f" -> translate T2({n}) valid={check_t2(sq, n)} base={seq2[0]}"
        print(msg)

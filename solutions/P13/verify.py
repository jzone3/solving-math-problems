#!/usr/bin/env python3
"""P13 / V5 verifier — standalone, no dependencies beyond the stdlib.

CLAIM (new negative result): there is NO (9,6,1)-perfect Mendelsohn design.

A (v,k,1)-PMD is a set of b = v(v-1)/k cyclically ordered k-tuples of
distinct points from a v-set such that for every t in {1,...,k-1} every
ordered pair (x,y) of distinct points appears "t-apart" (y at cyclic
distance t after x) in exactly one block. For (v,k)=(9,6): b=12.

This script verifies the claim by a from-scratch exhaustive search:
  * Items: (t,x,y) for t=1..5 and ordered pairs of distinct points -> 360
    requirements, each to be covered exactly once.
  * Candidates: all cyclic 6-tuples of distinct points (each rotation class
    represented once, minimal element first): C(9,6)*5! = 10080 candidates,
    each covering exactly 30 items.
  * A (9,6,1)-PMD is precisely an exact cover of the 360 items by 12
    candidates.
  * WLOG (relabelling points) one block is (0,1,2,3,4,5): any PMD has a
    block, and its 6 points can be renamed 0..5 in cyclic order.
  * Depth-first exact-cover search branching on the uncovered item with the
    fewest remaining compatible candidates; exhaustive on termination.

Runs in ~2 minutes in CPython. Prints PASS if (and only if) the search
terminates having found no solution, plus two sanity controls: the same code
finds a (7,6,1)-PMD (known to exist) and refutes (6,6,1) (known nonexistent).

An independent second check with a different method/encoding (SAT/CaDiCaL,
cell variables) lives in runs/P13/v5/satcheck.py; a C reimplementation
(runs/P13/v5/xcover.c) reproduces the identical node count (36019).
"""
import itertools


def exhaustive_pmd_search(V, K, fix_first_block):
    items = {}
    for t in range(1, K):
        for x in range(V):
            for y in range(V):
                if x != y:
                    items[(t, x, y)] = len(items)
    N = len(items)

    def mask_of(block):
        m = 0
        for t in range(1, K):
            for i in range(K):
                m |= 1 << items[(t, block[i], block[(i + t) % K])]
        return m

    cands = []
    for sub in itertools.combinations(range(V), K):
        for perm in itertools.permutations(sub[1:]):
            block = (sub[0],) + perm
            cands.append((block, mask_of(block)))

    by_item = [[] for _ in range(N)]
    for ci, (_, m) in enumerate(cands):
        for n in range(N):
            if (m >> n) & 1:
                by_item[n].append(ci)

    target = (1 << N) - 1
    start = mask_of(tuple(range(K))) if fix_first_block else 0
    sol = []

    def dfs(cov, chosen):
        if cov == target:
            sol.append(list(chosen))
            return True
        rem = target & ~cov
        best = None
        x = rem
        while x:
            bb = x & -x
            i = bb.bit_length() - 1
            lst = [ci for ci in by_item[i] if not (cands[ci][1] & cov)]
            if best is None or len(lst) < len(best):
                best = lst
                if not lst:
                    return False
            x ^= bb
        for ci in best:
            chosen.append(ci)
            if dfs(cov | cands[ci][1], chosen):
                return True
            chosen.pop()
        return False

    dfs(start, [])
    if not sol:
        return None
    blocks = ([tuple(range(K))] if fix_first_block else []) + \
        [cands[ci][0] for ci in sol[0]]
    return blocks


def is_pmd(blocks, V, K):
    if len(blocks) != V * (V - 1) // K:
        return False
    seen = set()
    for blk in blocks:
        if len(blk) != K or len(set(blk)) != K or not all(0 <= p < V for p in blk):
            return False
        for t in range(1, K):
            for i in range(K):
                key = (t, blk[i], blk[(i + t) % K])
                if key in seen:
                    return False
                seen.add(key)
    return len(seen) == (K - 1) * V * (V - 1)


def main():
    ok = True
    # control 1: (7,6,1)-PMD exists
    b7 = exhaustive_pmd_search(7, 6, True)
    if b7 is None or not is_pmd(b7, 7, 6):
        print("FAIL: control (7,6) not found/invalid")
        ok = False
    else:
        print("control (7,6,1)-PMD found and validated: OK")
    # control 2: (6,6,1)-PMD does not exist (known)
    if exhaustive_pmd_search(6, 6, True) is not None:
        print("FAIL: control (6,6) unexpectedly found")
        ok = False
    else:
        print("control (6,6,1)-PMD correctly nonexistent: OK")
    # main claim
    b9 = exhaustive_pmd_search(9, 6, True)
    if b9 is not None:
        print("FAIL: a (9,6,1)-PMD was found?!", b9)
        ok = False
    else:
        print("exhaustive search: no (9,6,1)-PMD exists")
    print("PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()

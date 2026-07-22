#!/usr/bin/env python3
"""Self-contained proof-check that NO (9,6,1)-PMD exists. Prints PASS if the
exhaustive search confirms nonexistence. Pure Python, no dependencies.

Argument (machine-checked where possible):
 A (9,6,1)-PMD is a set of 12 cyclically ordered 6-tuples of distinct points
 from a 9-set such that for each t in 1..5 every ordered pair (x,y), x != y,
 appears t-apart in exactly one block.

 Step 1 (counting): each block containing both x and y contributes exactly one
 distance to the ordered pair (x,y); since (x,y) occurs once at each of the 5
 distances, every unordered pair co-occurs in exactly 5 blocks. Hence the block
 SETS form a (9,6,5)-BIBD with 12 blocks, and each point lies in r = 8 blocks
 (r*(k-1) = lambda*(v-1) => r*5 = 5*8).

 Step 2 (complement): for a pair {x,y}, the number of blocks avoiding both is
 12 - 8 - 8 + 5 = 1, so the 12 complementary 3-sets cover every pair exactly
 once: they form a (9,3,1)-BIBD, i.e. an STS(9). The STS(9) is unique up to
 relabelling (verified below by exhaustively completing any STS(9) from a
 canonical start and checking transitivity is not even needed: we verify
 uniqueness by brute force over completions). Its 12 triples are the lines of
 AG(2,3). So WLOG the 12 block sets are the complements of the AG(2,3) lines.

 Step 3 (search): exhaustively try all cyclic orderings of those 12 fixed
 6-sets (min element pinned at position 0 -- rotations preserve distances --
 giving 5! = 120 orderings per block) with backtracking on the used
 (distance, ordered pair) slots. No completion exists => no (9,6,1)-PMD.
"""
from itertools import combinations, permutations
import sys

V, K = 9, 6

def ag_lines():
    lines = set()
    for a, b in combinations(range(9), 2):
        x3 = (-(a % 3) - (b % 3)) % 3
        y3 = (-(a // 3) - (b // 3)) % 3
        c = y3 * 3 + x3
        lines.add(tuple(sorted((a, b, c))))
    return sorted(lines)

def check_sts_uniqueness():
    """Every STS(9) containing triples {0,1,2} and {0,3,4} (WLOG by relabelling
    the two triples through point 0) completes in a way isomorphic to AG(2,3).
    We verify a stronger, simpler fact sufficient here: exhaustive backtracking
    over all STS(9) up to the natural lexicographic canonical labelling yields
    exactly one design. This is the classical uniqueness of STS(9)."""
    triples = list(combinations(range(9), 3))
    results = []
    def bt(chosen, covered):
        if len(chosen) == 12:
            results.append(list(chosen))
            return
        # smallest uncovered pair
        pr = None
        for p in combinations(range(9), 2):
            if p not in covered:
                pr = p
                break
        for tr in triples:
            if pr[0] in tr and pr[1] in tr:
                prs = list(combinations(tr, 2))
                if any(q in covered for q in prs):
                    continue
                # canonical labelling shortcut: force lexicographic minimality
                # relative to already chosen blocks is NOT applied; we count all
                # completions of the two canonical starting triples.
                chosen.append(tr)
                covered.update(prs)
                bt(chosen, covered)
                chosen.pop()
                covered.difference_update(prs)
    # WLOG first two triples through point 0 are {0,1,2},{0,3,4} (relabelling)
    start = [(0, 1, 2), (0, 3, 4)]
    cov = set()
    for tr in start:
        cov.update(combinations(tr, 2))
    bt(list(start), cov)
    # all completions must be isomorphic to AG(2,3); verify by checking each is
    # an STS and that a relabelling onto ag_lines() exists
    target = set(ag_lines())
    for sts in results:
        found = False
        for perm in permutations(range(9)):
            mapped = {tuple(sorted(perm[x] for x in tr)) for tr in sts}
            if mapped == target:
                found = True
                break
        if not found:
            return False, len(results)
    return True, len(results)

def exhaustive_pmd_search():
    lines = ag_lines()
    blocks = [sorted(set(range(9)) - set(l)) for l in lines]
    used = [[[False] * 9 for _ in range(9)] for _ in range(5)]
    def place(ordr):
        marked = []
        for t in range(1, 6):
            for p in range(6):
                x, y = ordr[p], ordr[(p + t) % 6]
                if used[t - 1][x][y]:
                    for (tt, xx, yy) in marked:
                        used[tt][xx][yy] = False
                    return False
                used[t - 1][x][y] = True
                marked.append((t - 1, x, y))
        return True
    def unplace(ordr):
        for t in range(1, 6):
            for p in range(6):
                used[t - 1][ordr[p]][ordr[(p + t) % 6]] = False
    nodes = [0]
    def dfs(j):
        if j == 12:
            return True
        bs = blocks[j]
        for rest in permutations(bs[1:]):
            nodes[0] += 1
            ordr = (bs[0],) + rest
            if place(ordr):
                if dfs(j + 1):
                    return True
                unplace(ordr)
        return False
    found = dfs(0)
    return found, nodes[0]

def main():
    ok, n = check_sts_uniqueness()
    if not ok:
        print('FAIL: found an STS(9) completion not isomorphic to AG(2,3)')
        return 1
    print('step 2 check: all %d STS(9) completions of the canonical start are '
          'isomorphic to AG(2,3)' % n)
    found, nodes = exhaustive_pmd_search()
    if found:
        print('FAIL: a (9,6,1)-PMD was found?! search is inconsistent with claim')
        return 1
    print('step 3 check: exhaustive search over all cyclic orderings '
          '(%d nodes) found no valid design' % nodes)
    print('PASS: no (9,6,1)-PMD exists')
    return 0

if __name__ == '__main__':
    sys.exit(main())

"""Exhaustive orbit-reduction (Kramer-Mesner style) scan: Z4-symmetric members of the
minimal ACZ-complete shape.

Shape: 12 degree-4 sources x 16 degree-3 sinks, 48 arcs (the minimum possible for a tau=3
counterexample: rho >= 4 forces >= 12 degree-4 sources). Assume an automorphism sigma of
order 4 acting FREELY: sources = (a,i), a in {0,1,2}, i in Z4; sinks = (b,i), b in
{0,1,2,3}, i in Z4; sigma adds 1 to i. The digraph is determined by the neighborhoods of
the 3 source-orbit representatives: N_a subset {0..3} x Z4 with |N_a| = 4, and
(a,i) -> (b, o+i mod 4) for each (b,o) in N_a. Sink in-degrees are constant on orbits and
equal sum_a c_{a,b} where c_{a,b} = |N_a  in orbit b|; sink-regularity <=> column sums 3
(rows sum 4). 415 contingency tables, 189,399,040 raw assignments.

Exact dedup for the 4^4 sink-orbit rotation subgroup: for each orbit b, the column
encoding (tuple over a of the offset set, as a sorted tuple) must be lexicographically
minimal among its 4 rotations. Row-permutation (S3) dedup: rows as (c-row, offsets)
encodings must be sorted. Remaining group (source rotations, column perms) NOT deduped —
harmless overcounting; exhaustiveness is what matters.

Each surviving candidate: numpy cut sweep (tau), planarity (LY-safe), SAT 3-dijoin pack.
"""
import sys
import time
from itertools import combinations, product
from math import comb

import numpy as np

from bip import all_min_dicuts, pack3, nonplanar
from bipfast import cut_sizes

OFFSETS = list(range(4))
SUBSETS = {c: [frozenset(s) for s in combinations(OFFSETS, c)] for c in range(5)}


def rot(s, d):
    return frozenset((o + d) % 4 for o in s)


def col_min(col):
    """col = tuple over a of frozenset offsets; return True if minimal among rotations."""
    key = tuple(tuple(sorted(s)) for s in col)
    for d in (1, 2, 3):
        k2 = tuple(tuple(sorted(rot(s, d))) for s in col)
        if k2 < key:
            return False
    return True


def gen_matrices():
    mats = []
    for r0 in product(range(5), repeat=4):
        if sum(r0) != 4:
            continue
        for r1 in product(range(5), repeat=4):
            if sum(r1) != 4:
                continue
            r2 = tuple(3 - r0[j] - r1[j] for j in range(4))
            if any(v < 0 for v in r2):
                continue
            mats.append((r0, r1, r2))
    return mats


def build_nbrs(rows):
    """rows: list of 3 lists over b of offset frozensets -> nbrs for bip machinery."""
    nbrs = []
    for a in range(3):
        for i in range(4):
            nb = []
            for b in range(4):
                for o in rows[a][b]:
                    nb.append(4 * b + (o + i) % 4)  # sink id = 4*b + offset
            nbrs.append(tuple(sorted(nb)))
    return nbrs, 16


def min_columns(sizes3):
    """All rotation-minimal columns (s0,s1,s2) with |sa| = sizes3[a]."""
    out = []
    for col in product(SUBSETS[sizes3[0]], SUBSETS[sizes3[1]], SUBSETS[sizes3[2]]):
        if col_min(col):
            out.append(col)
    return out


def main(shard=0, nshards=1):
    mats = gen_matrices()[shard::nshards]
    t0 = time.time()
    cand = tau3 = nonpl = unsat = 0
    seen = set()
    colcache = {}
    for mi, mat in enumerate(mats):
        collists = []
        for b in range(4):
            key = (mat[0][b], mat[1][b], mat[2][b])
            if key not in colcache:
                colcache[key] = min_columns(key)
            collists.append(colcache[key])
        for cols in product(*collists):
            rows = [[cols[b][a] for b in range(4)] for a in range(3)]
            # row-sorted canonical + global dedup (S3 rows; matrices may repeat
            # candidates across column permutations)
            keys = tuple(sorted(tuple((len(rows[a][b]), tuple(sorted(rows[a][b])))
                                      for b in range(4)) for a in range(3)))
            if keys in seen:
                continue
            seen.add(keys)
            rows = [[frozenset(keys[a][b][1]) for b in range(4)] for a in range(3)]
            cand += 1
            nbrs, nT = build_nbrs(rows)
            sizes = cut_sizes(nbrs, nT)
            if sizes.size == 0 or int(sizes.min()) < 3:
                continue
            tau3 += 1
            if not nonplanar(nbrs, nT):
                continue
            nonpl += 1
            tau, md = all_min_dicuts(nbrs, nT)
            assert tau == 3
            if not pack3(nbrs, md):
                unsat += 1
                print(f"!!! UNSAT Z4-SYMMETRIC: rows={rows}", flush=True)
        if (mi + 1) % 5 == 0:
            print(f"[{int(time.time()-t0)}s] mat {mi+1}/{len(mats)} cand={cand} "
                  f"tau3={tau3} nonplanar={nonpl} unsat={unsat}", flush=True)
    print(f"DONE mats={len(mats)} candidates={cand} tau3={tau3} "
          f"nonplanar_sat_checked={nonpl} unsat={unsat} time={int(time.time()-t0)}s",
          flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(int(sys.argv[1]), int(sys.argv[2]))
    else:
        main()

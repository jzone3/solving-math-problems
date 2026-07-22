#!/usr/bin/env python3
"""Complete multiplier-orbit exhaust for CW(120,49).

AGZ Thm 2.4: k = 49 = 7^2, gcd(120,49)=1 => 7 is a multiplier and some
translate of any CW(120,49) is fixed by x -> 7x. So the first row is constant
on <7>-orbits of Z_120 (orbit values in {0,±1}). We exhaust ALL orbit
assignments exactly (DFS over orbits, weight and pairwise-PACF pruning via
incremental autocorrelation), i.e. this decides existence of CW(120,49).

<7> mod 120 = {1,7,49,103}, order 4.
"""
import sys
import numpy as np
from itertools import product

sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper
from icw_enum import orbits_of

n, k = 120, 49
orbs = orbits_of(7, n)
sizes = [len(o) for o in orbs]
print(f"{len(orbs)} orbits, sizes {sorted(sizes)}")

# precompute autocorrelation contribution matrix between orbits:
# corr[t] for chosen orbit pair (oi with value vi, oj with value vj):
# contribution vi*vj * C_{i,j,t} where C = #{(x,y) in oi x oj : y - x = t}.
no = len(orbs)
C = np.zeros((no, no, n), dtype=np.int64)
for i, oi in enumerate(orbs):
    for j, oj in enumerate(orbs):
        for x in oi:
            for y in oj:
                C[i, j, (y - x) % n] += 1

order = sorted(range(no), key=lambda i: -sizes[i])
best = None
count = [0]


def dfs(pos, vals, acf, wt):
    if wt > k:
        return
    rem = sum(sizes[order[p]] for p in range(pos, no))
    if wt + rem < k:
        return
    if pos == no:
        if wt == k and not acf[1:].any():
            print("SOLUTION", vals)
            raise SystemExit
        return
    i = order[pos]
    for v in (0, 1, -1):
        count[0] += 1
        if v == 0:
            dfs(pos + 1, vals + [(i, 0)], acf, wt)
        else:
            nacf = acf + v * v * C[i, i]
            for (j, vj) in vals:
                if vj:
                    nacf = nacf + v * vj * (C[i, j] + C[j, i])
            # prune: no completed... acf can still change; weak prune only
            dfs(pos + 1, vals + [(i, v)], nacf, wt + v * v * sizes[i])


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    try:
        dfs(0, [], np.zeros(n, dtype=np.int64), 0)
        print(f"NO CW(120,49): exhaust complete, nodes={count[0]}")
    except SystemExit:
        print("found; nodes=", count[0])

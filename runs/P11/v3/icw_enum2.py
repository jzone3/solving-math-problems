#!/usr/bin/env python3
"""Norm-pruned DFS enumeration of <t>-fixed ICW_d(m,k) (faster icw_enum).

Usage: python3 icw_enum2.py m d k t
"""
import sys

sys.path.insert(0, ".")
from icw_enum import orbits_of


def fixed_icws(m, d, k, t):
    orbs = orbits_of(t, m)
    sizes = [len(o) for o in orbs]
    no = len(orbs)
    sols = []

    def flat(w):
        return all(sum(w[i] * w[(i + s) % m] for i in range(m)) == 0
                   for s in range(1, m))

    cs = [0] * no

    def dfs(pos, norm):
        if norm > k:
            return
        if pos == no:
            if norm == k:
                w = [0] * m
                for c, o in zip(cs, orbs):
                    for x in o:
                        w[x] = c
                if flat(w):
                    sols.append(tuple(w))
            return
        # remaining max norm
        rem = sum(d * d * sizes[i] for i in range(pos, no))
        if norm + rem < k:
            return
        for c in range(-d, d + 1):
            cs[pos] = c
            dfs(pos + 1, norm + c * c * sizes[pos])
        cs[pos] = 0

    dfs(0, 0)
    return orbs, sols


if __name__ == "__main__":
    m, d, k, t = map(int, sys.argv[1:5])
    orbs, sols = fixed_icws(m, d, k, t)
    print(f"<{t}>-fixed ICW_{d}({m},{k}): {len(orbs)} orbits "
          f"{sorted(len(o) for o in orbs)}, {len(sols)} solutions")
    for w in sols[:40]:
        print(" ", w)

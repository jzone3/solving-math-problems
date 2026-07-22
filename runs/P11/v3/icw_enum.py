#!/usr/bin/env python3
"""Enumerate ICW_d(m, k): integer vectors w on Z_m, |w_i| <= d, with
w w* = k delta_0, assuming multiplier t (AGZ Thm 4.1) fixes a translate:
w constant on <t>-orbits. Expand back to all translates/multiplier images.

Usage: python3 icw_enum.py m d k t
"""
import sys
from itertools import product
from math import gcd


def orbits_of(t, m):
    seen, orbs = set(), []
    for x in range(m):
        if x in seen:
            continue
        o = set()
        y = x
        while y not in o:
            o.add(y)
            y = (y * t) % m
        orbs.append(sorted(o))
        seen |= o
    return orbs


def flat(w, m, k):
    for s in range(1, m):
        if sum(w[i] * w[(i + s) % m] for i in range(m)) != 0:
            return False
    return sum(x * x for x in w) == k


def enum_fixed(m, d, k, t):
    orbs = orbits_of(t, m)
    sizes = [len(o) for o in orbs]
    sols = []
    for cs in product(range(-d, d + 1), repeat=len(orbs)):
        if sum(c * c * s for c, s in zip(cs, sizes)) != k:
            continue
        w = [0] * m
        for c, o in zip(cs, orbs):
            for x in o:
                w[x] = c
        if flat(w, m, k):
            sols.append(tuple(w))
    return orbs, sols


def expand(sols, m):
    all_w = set()
    for w in sols:
        for u in range(1, m):
            if gcd(u, m) != 1:
                continue
            wu = tuple(w[(u * i) % m] for i in range(m))
            for s in range(m):
                all_w.add(tuple(wu[(i - s) % m] for i in range(m)))
    return sorted(all_w)


if __name__ == "__main__":
    m, d, k, t = map(int, sys.argv[1:5])
    orbs, sols = enum_fixed(m, d, k, t)
    print(f"ICW_{d}({m},{k}) multiplier {t}: {len(orbs)} orbits "
          f"{[len(o) for o in orbs]}")
    print(f"fixed solutions: {len(sols)}")
    for w in sols:
        print(" ", w)
    aw = expand(sols, m)
    print(f"total after translate/multiplier expansion: {len(aw)}")

#!/usr/bin/env python3
"""
P15 V4 phase 45 (v5): coarsen placeholder cells, then patch.

Column-counting shows why v2-v4 stall: k sibling cells mod n need
~k divisor-columns of n's lattice, but the lattice only has d(n)
columns.  However the placeholder tails come from parallel tower
branches, so unions of siblings often form complete coarser cells:
if all p cells r' + t*(n/p) (t = 0..p-1) are present, they merge
into the single cell (r', n/p).  Coarsening is applied to fixpoint
across ALL sections first, shrinking both the cell count and the
lattice pressure; then the scale-tree patcher of patch48 runs on
the merged cells.
"""
import json
import numpy as np
from math import gcd
from collections import defaultdict
from globalcheck import all_sections
from patch48 import CellPatcher, divisors

SMALLP = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
          59, 61, 67, 71, 73, 79, 83, 89, 97]


def coarsen(cells):
    cells = set(cells)
    changed = True
    while changed:
        changed = False
        byn = defaultdict(set)
        for r, n in cells:
            byn[n].add(r)
        for n, rs in byn.items():
            for p in SMALLP:
                if n % p:
                    continue
                np_ = n // p
                bycls = defaultdict(list)
                for r in rs:
                    bycls[r % np_].append(r)
                for rp, group in bycls.items():
                    if len(group) == p:
                        for r in group:
                            cells.discard((r, n))
                        cells.add((rp, np_))
                        changed = True
                if changed:
                    break
            if changed:
                break
    return sorted(cells, key=lambda c: -c[1])


def main():
    secs = all_sections()
    used = set()
    for name, cc, tt in secs:
        for r, n in cc:
            used.add(n)
    raw = [(r, n) for name, cc, tt in secs for r, n in tt]
    print(f"used moduli: {len(used)}, raw cells: {len(raw)}")
    cells = coarsen(raw)
    print(f"coarsened cells: {len(cells)}")

    patches = []
    percell = []
    todo = cells
    fail = []
    for cap, big in ((8, True), (4, False), (16, False), (64, False),
                     (512, False)):
        fail = []
        for r, n in todo:
            cp = CellPatcher(r, n, used, cap=cap, minm=n if big else 42)
            if cp.cover(0, 2) and cp.cover(1, 2):
                patches.extend(cp.out)
                percell.append(((r, n), cp.out))
            else:
                for _, m in cp.out:
                    used.discard(m)
                fail.append((r, n))
        print(f"pass cap={cap} big={big}: "
              f"patched {len(todo) - len(fail)}, remaining {len(fail)}")
        todo = fail
        if not fail:
            break
    print(f"cells patched: {len(cells) - len(fail)}/{len(cells)}, "
          f"failed: {len(fail)}")
    for f in fail[:10]:
        print("  FAIL", f)
    if patches:
        print(f"patch congruences: {len(patches)}")
        mods = [m for _, m in patches]
        assert len(set(mods)) == len(mods), "patch moduli collide"
        print(f"patch moduli all distinct; min patch modulus: "
              f"{min(mods)}")

    bad = 0
    for (r, n), got in percell:
        K = 4096
        cov = np.zeros(K, dtype=bool)
        for r2, m in got:
            g = gcd(n, m)
            if (r - r2) % g:
                continue
            mg = m // g
            inv = pow((n // g) % mg, -1, mg)
            i0 = ((r2 - r) // g * inv) % mg
            if i0 < K:
                cov[i0::mg] = True
        if not cov.all():
            bad += 1
    print(f"self-test: cells with incomplete patch cover: {bad}")

    with open("patches49.json", "w") as fh:
        json.dump({"cells": [list(c) for c, _ in percell],
                   "patches": patches,
                   "failed": [list(f) for f in fail]}, fh)
    print("wrote patches49.json")


if __name__ == "__main__":
    main()

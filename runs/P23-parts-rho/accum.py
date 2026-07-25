"""Simplified Parts-style accumulation loop: alternate
  expansion  (re-add members of partially-filled base orbits whose degree
              into the current graph is high, plus high-degree reserve
              vertices)  and
  reduction  (DRAT core jump + time-boxed 8-4-2-1 greedy deletion),
keeping the smallest UNSAT (non-4-colorable) vertex set seen.

Usage: POOL=pool16.pkl accum.py <seed> <start.pkl> <tag> [minutes_per_reduction]
"""
import os
import pickle
import random
import sys
import time

import lattice
from coremin import solve_core, NALL, adj
from greedy8 import attempt

POOLF = os.environ.get("POOL", "union.pkl")
allpts, E = pickle.load(open(POOLF, "rb"))

MIN_DEG = 4


def orbit_map():
    key = {}
    for i, (side, p) in enumerate(allpts):
        key[i] = (side, min(lattice.orbit24(p)))
    orbs = {}
    for i, k in key.items():
        orbs.setdefault(k, []).append(i)
    return key, orbs


KEY, ORBS = orbit_map()


def expansion(S, rnd, cap=400):
    """Candidates: vertices outside S in partially-filled orbits, or with
    degree >= MIN_DEG into S; prefer small orbits and high degree."""
    Sset = set(S)
    cand = []
    for k, members in ORBS.items():
        present = sum(1 for v in members if v in Sset)
        if present == 0 or present == len(members):
            partial = present > 0
        else:
            partial = True
        for v in members:
            if v in Sset:
                continue
            deg = sum(1 for u in adj[v] if u in Sset)
            if deg >= MIN_DEG or (partial and deg >= MIN_DEG - 1):
                cand.append((-(deg + (2 if partial else 0)
                              + (1 if len(members) <= 12 else 0)),
                             rnd.random(), v))
    cand.sort()
    return [v for _, _, v in cand[:cap]]


def reduction(S, rnd, tag, minutes):
    st, keep = solve_core(S, seed=rnd.randrange(10 ** 6), tag=tag)
    if st != "UNSAT":
        return None
    S = keep
    deadline = time.time() + 60 * minutes
    order = sorted(S)
    rnd.shuffle(order)
    k = 0
    while time.time() < deadline and k < len(order):
        group = [v for v in order[k:k + 8] if v in S]
        k += 8
        if not group:
            continue
        res = attempt(S, group, rnd, tag)
        if res is not None:
            S = res
            continue
        stack = [group[:4], group[4:]] if len(group) > 4 else [group]
        while stack and time.time() < deadline:
            g = [v for v in stack.pop() if v in S]
            if not g:
                continue
            res = attempt(S, g, rnd, tag)
            if res is not None:
                S = res
            elif len(g) > 1:
                h = len(g) // 2
                stack += [g[:h], g[h:]]
    return S


def main():
    seed = int(sys.argv[1])
    start = set(pickle.load(open(sys.argv[2], "rb")))
    tag = sys.argv[3]
    minutes = float(sys.argv[4]) if len(sys.argv) > 4 else 20.0
    rnd = random.Random(seed)
    best = set(start)
    S = set(start)
    it = 0
    while True:
        it += 1
        add = expansion(S, rnd)
        S2 = S | set(add)
        print(f"{tag} it{it}: expand +{len(S2) - len(S)} -> {len(S2)}",
              flush=True)
        red = reduction(sorted(S2), rnd, tag, minutes)
        if red is None:
            print(f"{tag} it{it}: reduction lost UNSAT?!", flush=True)
            S = best
            continue
        S = set(red)
        print(f"{tag} it{it}: reduced -> {len(S)} (best {len(best)})",
              flush=True)
        if len(S) < len(best):
            best = set(S)
            pickle.dump(sorted(best), open(f"accum_{tag}.pkl", "wb"))
            print(f"{tag} it{it}: NEW BEST {len(best)}", flush=True)


if __name__ == "__main__":
    main()

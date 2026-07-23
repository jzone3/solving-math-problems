#!/usr/bin/env python3
"""Hole-driven symbolic constructor (v2). Always attack the currently largest
hole (smallest modulus M): use the smallest unused modulus d = M*q (q smooth,
d >= m), covering exactly 1/q of the hole; also credit incidental hits on
other holes when the split factor is small (skipping a hit only under-credits
coverage, which is sound). Siblings that survive get merged back when a full
family remains.

Usage: coset_cover2.py m [frag_cap] [out.json] [max_steps]
"""
import heapq, json, math, sys
from fractions import Fraction

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
          59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113)


def gen_multipliers(limit):
    """Smooth numbers >= 2 up to limit, ascending."""
    heap = [1]
    seen = {1}
    out = []
    while heap:
        v = heapq.heappop(heap)
        if v > 1:
            out.append(v)
        for p in PRIMES:
            w = v * p
            if w <= limit and w not in seen:
                seen.add(w)
                heapq.heappush(heap, w)
    return out


MULTS = gen_multipliers(100000)


def merge_around(holes, parent_key):
    """Try to merge the family of cosets that share a given parent."""
    a, M = parent_key
    changed = True
    while changed:
        changed = False
        for p in PRIMES:
            if M % p:
                continue
            Mp = M // p
            fam = [(a % Mp + j * Mp, M) for j in range(p)]
            if all(h in holes for h in fam):
                for h in fam:
                    holes.discard(h)
                holes.add((a % Mp, Mp))
                a, M = a % Mp, Mp
                changed = True
                break


def run(m, frag_cap=None, out=None, max_steps=10**9,
        status_every=200):
    if frag_cap is None:
        frag_cap = 4 * m
    holes = {(0, 1)}
    density = Fraction(1)
    used = set()
    cover = []
    steps = 0
    while holes and steps < max_steps:
        steps += 1
        # largest hole = min M (tie: smallest a)
        a, M = min(holes, key=lambda h: (h[1], h[0]))
        # smallest unused d = M*q with d >= m
        d = None
        for q in MULTS:
            cand = M * q
            if cand >= m and cand not in used:
                d = cand
                qq = q
                break
        if d is None:
            print("modulus pool exhausted", flush=True)
            break
        used.add(d)
        # residue b = a + j*M for some 0 <= j < q; pick j maximizing
        # incidental coverage of other holes (weight 1/L per hit)
        jwts = {}  # (mod, r) -> weight: j = r (mod mod) hits that hole
        for (ha, hM) in holes:
            if (ha, hM) == (a, M):
                continue
            g = math.gcd(d, hM)
            L = d // g * hM
            if L // hM > frag_cap:
                continue
            gm = math.gcd(M, g)
            if (ha - a) % gm:
                continue
            gp = g // gm
            j0 = ((ha - a) // gm * pow(M // gm, -1, gp)) % gp if gp > 1 else 0
            jwts[(gp, j0)] = jwts.get((gp, j0), Fraction(0)) + Fraction(1, L)
        best_j, best_w = 0, Fraction(-1)
        for j in ({r for (_, r) in jwts} | {0}):
            wsum = sum(w for (md, r), w in jwts.items() if j % md == r)
            if wsum > best_w:
                best_j, best_w = j, wsum
        b = (a + best_j * M) % d
        cover.append((b, d))
        # exact hole update: all holes hit by (b, d)
        removed, newly = [], []
        gain = Fraction(0)
        for (ha, hM) in holes:
            g = math.gcd(d, hM)
            if b % g != ha % g:
                continue
            L = d // g * hM
            split = L // hM
            if split > frag_cap and (ha, hM) != (a, M):
                continue  # sound skip: under-credit
            removed.append((ha, hM))
            gain += Fraction(1, L)
            for j in range(split):
                aa = ha + j * hM
                if aa % d == b % d:
                    continue
                newly.append((aa, L))
        for h in removed:
            holes.discard(h)
        holes.update(newly)
        density -= gain
        # merge families around the new siblings
        for h in set(newly):
            if h in holes:
                merge_around(holes, h)
        if steps % status_every == 0:
            print(f"n={len(cover)} d={d} density={float(density):.3e} "
                  f"holes={len(holes)} maxM={max(h[1] for h in holes)}",
                  flush=True)
    print(f"DONE cover={len(cover)} density={float(density):.3e} "
          f"holes={len(holes)}", flush=True)
    if not holes:
        print(f"COVERED min_mod={min(n for _, n in cover)}", flush=True)
        if out:
            json.dump({"m": m, "cover": [[a, n] for a, n in
                                         sorted(cover, key=lambda x: x[1])]},
                      open(out, "w"))
    return cover, holes, density


if __name__ == "__main__":
    m = int(sys.argv[1])
    frag_cap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    out = sys.argv[3] if len(sys.argv) > 3 else None
    max_steps = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    run(m, frag_cap, out, max_steps)

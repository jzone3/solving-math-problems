#!/usr/bin/env python3
"""Multiplier-orbit search for CW(n,k).

Assume the first row a is fixed by a multiplier t (unit of Z_n): a_{t*j} = a_j.
Then a is constant on orbits of j -> t*j, so it is determined by one ternary
value per orbit. Requirements: sum of sizes of nonzero orbits = k, and PAF = 0
for all nontrivial shifts. Enumerate: subset-sum over orbit sizes to hit k,
then all sign patterns (global negation fixed), exact integer PAF check.

This is how many known CWs arise (cf. Arasu-Gordon-Zhang); cheap and exhaustive
per multiplier.

Usage: multiplier_search.py n k [max_orbits] [ord_min]
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def orbits_of(n, t, r=0):
    """orbits of the affine bijection j -> t*j + r (t a unit)."""
    seen = [False] * n
    orbs = []
    for j in range(n):
        if seen[j]:
            continue
        o = []
        x = j
        while not seen[x]:
            seen[x] = True
            o.append(x)
            x = (x * t + r) % n
        orbs.append(o)
    return orbs


def paf_ok(a, n):
    for s in range(1, n // 2 + 1):
        if sum(a[i] * a[(i + s) % n] for i in range(n)) != 0:
            return False
    return True


def search(n, k, max_orbits=22, affine=False):
    tried = set()
    found = []
    cands = []
    for t in range(2, n):
        if np.gcd(t, n) != 1:
            continue
        for r in (range(n) if affine else (0,)):
            cands.append((t, r))
    for (t, r) in cands:
        orbs = orbits_of(n, t, r)
        key = tuple(sorted(tuple(sorted(o)) for o in orbs))
        if key in tried:
            continue
        tried.add(key)
        if len(orbs) > max_orbits:
            continue
        sizes = [len(o) for o in orbs]
        m = len(orbs)
        print(f"t={t},r={r}: {m} orbits sizes={sorted(sizes, reverse=True)[:10]}...", flush=True)
        # subset-sum: subsets of orbits with total size k
        subs = []

        def dfs(i, rem, cur):
            if rem == 0:
                subs.append(list(cur))
                return
            if i == m or rem < 0:
                return
            # prune: remaining total
            if sum(sizes[i:]) < rem:
                return
            cur.append(i)
            dfs(i + 1, rem - sizes[i], cur)
            cur.pop()
            dfs(i + 1, rem, cur)

        dfs(0, k, [])
        s = int(np.sqrt(k))
        cnt = 0
        hit = []

        def signdfs(sub, i, acc, sgns):
            nonlocal cnt
            if i == len(sub):
                if acc == s:
                    a = np.zeros(n, dtype=np.int64)
                    for bi, oi in enumerate(sub):
                        a[orbs[oi]] = sgns[bi]
                    cnt += 1
                    f = np.fft.rfft(a)
                    p = np.fft.irfft(f * np.conj(f), n)
                    p = np.rint(p).astype(np.int64)
                    if np.all(p[1:] == 0):
                        al = [int(v) for v in a]
                        if paf_ok(al, n):  # exact integer double-check
                            hit.append(al)
                    return
                return
            rem = sum(sizes[sub[j]] for j in range(i, len(sub)))
            if acc - rem > s or acc + rem < s:
                return
            for sg in (1, -1):
                sgns.append(sg)
                signdfs(sub, i + 1, acc + sg * sizes[sub[i]], sgns)
                sgns.pop()

        for sub in subs:
            signdfs(sub, 0, 0, [])
            if hit:
                a = hit[0]
                found.append((t, a))
                print(f"  HIT t={t} row={a}", flush=True)
                wp = os.path.join(HERE, f"witness_mult_{n}_{k}.json")
                json.dump({"n": n, "k": k, "row": a}, open(wp, "w"))
                return found
        print(f"  t={t},r={r}: {len(subs)} subsets, {cnt} sum-ok patterns PAF-checked, none valid", flush=True)
    return found


if __name__ == "__main__":
    n, k = int(sys.argv[1]), int(sys.argv[2])
    mo = int(sys.argv[3]) if len(sys.argv) > 3 else 22
    affine = len(sys.argv) > 4 and sys.argv[4] == "--affine"
    res = search(n, k, mo, affine)
    print("DONE", len(res), "witnesses", flush=True)

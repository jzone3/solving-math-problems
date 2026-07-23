#!/usr/bin/env python3
"""
Stage-2 hole cover for P18 phase B (multi-level Krukenberg-style build).

Input: a stage-1 best assignment json (from anneal.py) over Z/N0 with
bestE > 0 holes H = {h : uncovered mod N0}. Choose Q squarefree, coprime
to N0. Stage-2 pool: moduli m = d*q with d | N0, q | Q, q > 1, and
2*d*q + 1 prime (i.e. m in M). Such m never divides N0, so stage-2 moduli
are automatically distinct from stage-1 moduli.

A congruence (a mod d*q) covers hole point (h, t) — representing the
integer x = h + N0*t, t in Z/Q — iff h ≡ a (mod d) and
t ≡ (a - h)/N0 (mod q). Universe size |H|*Q; we anneal over it exactly
like anneal.py (repair-targeted Metropolis moves).

Usage: stage2.py stage1.json Q [seconds] [seed] [T0] [alpha]
On success writes phaseB_staged_N{N0}_Q{Q}.json with the FULL m-space
family (stage-1 + stage-2 congruences via CRT); verify by lifting and
running solutions/P18/verify.py.
"""
import json
import math
import random
import sys
import time

import numpy as np

from twophase import is_prime, divisors


def crt(r1, n1, r2, n2):
    # gcd(n1, n2) = 1
    g, x = n1, pow(n1, -1, n2)
    return (r1 + n1 * ((r2 - r1) * x % n2)) % (n1 * n2)


def main():
    st1 = json.load(open(sys.argv[1]))
    Q = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 3600.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    T0 = float(sys.argv[5]) if len(sys.argv) > 5 else 8.0
    alpha = float(sys.argv[6]) if len(sys.argv) > 6 else 0.99995
    N0 = st1["N"]
    fam1 = [(a, m) for a, m in st1["family"]]
    assert math.gcd(N0, Q) == 1
    rng = random.Random(seed)

    cov0 = np.zeros(N0, dtype=np.int16)
    for a, m in fam1:
        cov0[a::m] += 1
    H = np.flatnonzero(cov0 == 0)
    nH = len(H)
    print("N0=%d Q=%d holes=%d universe=%d" % (N0, Q, nH, nH * Q), flush=True)
    hidx = {int(h): i for i, h in enumerate(H)}

    used1 = {m for _, m in fam1}
    pool = []
    for d in divisors(N0):
        for q in divisors(Q):
            if q == 1:
                continue
            m = d * q
            if m in used1:
                continue
            if is_prime(2 * m + 1):
                pool.append((d, q, m))
    mass = sum(1.0 / m for _, _, m in pool)
    need = nH / N0
    print("stage2 pool=%d mass=%.5f need>=%.5f" % (len(pool), mass, need),
          flush=True)
    if mass < need:
        print("INSUFFICIENT stage-2 mass; enlarge Q", flush=True)
        return

    # Precompute, for each modulus (d,q): the hole indices with h ≡ a (mod d)
    # depend on a; we store holes by residue mod d lazily per modulus.
    Ninv = {q: pow(N0 % q, -1, q) for q in divisors(Q) if q > 1}
    holes_mod = {}  # d -> {r: np.array of hole indices with H % d == r}

    def holes_by_d(d):
        if d not in holes_mod:
            r = H % d
            order = np.argsort(r, kind="stable")
            rs = r[order]
            table = {}
            start = 0
            for i in range(1, len(rs) + 1):
                if i == len(rs) or rs[i] != rs[i - 1]:
                    table[int(rs[start])] = order[start:i]
                    start = i
            holes_mod[d] = table
        return holes_mod[d]

    def cover_points(d, q, a):
        """Universe flat indices covered by congruence a mod (d*q)."""
        tab = holes_by_d(d)
        idxs = tab.get(a % d)
        if idxs is None:
            return np.empty(0, dtype=np.int64)
        hvals = H[idxs]
        t = ((a - hvals) % q) * Ninv[q] % q
        reps = np.arange(0, Q, q, dtype=np.int64)
        return ((idxs.astype(np.int64) * Q)[:, None]
                + t[:, None] + reps[None, :]).ravel()

    # initial assignment: greedy fill by fresh coverage
    cov = np.zeros(nH * Q, dtype=np.int16)
    assign = {}
    for d, q, m in sorted(pool, key=lambda x: x[2]):
        best = None
        for _ in range(30):  # sample residues
            a = rng.randrange(d * q)
            pts = cover_points(d, q, a)
            g = int((cov[pts] == 0).sum()) if len(pts) else 0
            if best is None or g > best[0]:
                best = (g, a)
        assign[(d, q)] = best[1]
        pts = cover_points(d, q, best[1])
        if len(pts):
            cov[pts] += 1
    E = int((cov == 0).sum())
    bestE = E
    best_assign = dict(assign)
    print("init E=%d / %d" % (E, nH * Q), flush=True)

    keys = list(assign.keys())
    T = T0
    t0 = time.time()
    it = 0
    last = t0
    while time.time() - t0 < secs and E > 0:
        it += 1
        d, q = keys[rng.randrange(len(keys))]
        a_old = assign[(d, q)]
        if rng.random() < 0.7:
            zeros = np.flatnonzero(cov == 0)
            z = int(zeros[rng.randrange(len(zeros))])
            hi, t = divmod(z, Q)
            h = int(H[hi])
            # choose a ≡ h (mod d) and matching t (mod q): a mod dq via CRT
            a_new = crt(h % d, d, (h + N0 * t) % q, q)
        else:
            a_new = rng.randrange(d * q)
        if a_new == a_old:
            continue
        old_pts = cover_points(d, q, a_old)
        new_pts = cover_points(d, q, a_new)
        created = int((cov[old_pts] == 1).sum()) if len(old_pts) else 0
        filled = int((cov[new_pts] == 0).sum()) if len(new_pts) else 0
        dE = created - filled
        if dE <= 0 or rng.random() < np.exp(-dE / T):
            if len(old_pts):
                cov[old_pts] -= 1
            if len(new_pts):
                cov[new_pts] += 1
            assign[(d, q)] = a_new
            E += dE
            if E < bestE:
                bestE = E
                best_assign = dict(assign)
                print("it=%d T=%.3f bestE=%d %.1fs"
                      % (it, T, bestE, time.time() - t0), flush=True)
        T *= alpha
        if T < 0.02:
            T = T0 * 0.3
        if time.time() - last > 120:
            last = time.time()
            print("... it=%d T=%.3f E=%d best=%d (%.1fs)"
                  % (it, T, E, bestE, time.time() - t0), flush=True)
    if E == 0:
        fam = [[a, m] for a, m in fam1]
        for (d, q), a in assign.items():
            fam.append([a, d * q])
        fn = "phaseB_staged_N%d_Q%d.json" % (N0, Q)
        json.dump({"N0": N0, "Q": Q, "family": fam}, open(fn, "w"))
        print("STAGE-2 SUCCESS -> %s (family size %d)" % (fn, len(fam)),
              flush=True)
    else:
        print("stage2 FAILED bestE=%d its=%d" % (bestE, it), flush=True)


if __name__ == "__main__":
    main()

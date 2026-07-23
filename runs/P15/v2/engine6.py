#!/usr/bin/env python3
"""Symbolic Nielsen-style constructor for covering systems, min modulus >= T.

State: set of uncovered residue classes (r mod M), M = current lcm (bigint —
never materialize Z_M). Incorporate primes one power at a time: step p turns
each uncovered class into p children r + j*M (mod M*p). Only *new* divisors
v of M*p (i.e. p-exponent exactly the new one, v = d * p^e) can partially
cover children without having covered the parent. Greedy set-cover over
columns (v, a): column covers every child c with c ≡ a (mod v). Each modulus
value used at most once globally. Leftover children become the new state.

This is the cross-branch alignment engines 3-5 lacked: one congruence kills
children across many branches at once, exactly like Nielsen's x-inputs.

Usage: python3 engine6.py -T 12 --steps "2:6,3:4,5:2,7:1,11:1,13:1,17:1,..."
       [--vmax 2000000] [-o cover.txt]
"""
import argparse
import sys
import time
from collections import defaultdict


def parse_steps(s):
    """"2:6,3:4,5:2" -> [2,2,2,2,2,2,3,3,3,3,5,5]"""
    out = []
    for part in s.split(","):
        p, e = part.split(":")
        out += [int(p)] * int(e)
    return out


def divisors_of(fac, cap=None):
    divs = [1]
    for p, e in fac.items():
        new = []
        for d in divs:
            pk = 1
            for _ in range(e + 1):
                nd = d * pk
                if cap is None or nd <= cap:
                    new.append(nd)
                pk *= p
                if cap is not None and d * pk > cap:
                    break
        divs = new
    return divs


def run(T, steps, vmax, out=None, verbose=True):
    M = 1
    fac = {}          # factorization of M
    uncovered = [0]   # residues mod M
    used = set()
    congs = []
    t0 = time.time()

    for si, p in enumerate(steps):
        e_new = fac.get(p, 0) + 1
        pe = p ** e_new
        # children of uncovered classes mod M*p
        Mp = M * p
        children = []
        for r in uncovered:
            for j in range(p):
                children.append(r + j * M)
        # candidate new moduli: v = d * pe, d | M/p^{e_new-1}, gcd(d,p)=1 part
        # handled by requiring d | M with p-exponent <= e_new-1 -> v | Mp and
        # p-exp(v) == e_new
        base_fac = dict(fac)
        if p in base_fac:
            del base_fac[p]
        cap_d = None if vmax is None else vmax // pe
        cands = []
        if cap_d is None or cap_d >= 1:
            for d in divisors_of(base_fac, cap=cap_d):
                # also allow lower powers of p in d? no: p-exp must equal e_new
                v = d * pe
                if v >= T and v not in used:
                    cands.append(v)
        cands.sort()
        # greedy set cover over children
        rem = set(children)
        while rem and cands:
            best = None  # (count, v, a)
            for v in cands:
                buckets = defaultdict(int)
                for c in rem:
                    buckets[c % v] += 1
                a, cnt = max(buckets.items(), key=lambda kv: kv[1])
                # prefer max kills; tiebreak small v (cheap moduli first is
                # wrong here: small v are scarce/valuable later; tiebreak
                # LARGE v to save small ones)
                if best is None or cnt > best[0] or \
                        (cnt == best[0] and v > best[1]):
                    best = (cnt, v, a)
            cnt, v, a = best
            if cnt == 0:
                break
            used.add(v)
            congs.append((a % v, v))
            cands.remove(v)
            rem = {c for c in rem if c % v != a % v}
        M = Mp
        fac[p] = e_new
        uncovered = sorted(rem)
        if verbose:
            print(f"step {si+1}/{len(steps)} p={p}^{e_new}: "
                  f"uncovered {len(uncovered)}, congs {len(congs)}, "
                  f"t={time.time()-t0:.0f}s", flush=True)
        if not uncovered:
            print(f"COVERED. lcm has {len(fac)} primes, {len(congs)} congs, "
                  f"min mod {min(v for _, v in congs)}")
            if out:
                with open(out, "w") as f:
                    f.write(f"# engine6 T={T} steps up to {p}^{e_new}\n")
                    for a, v in congs:
                        f.write(f"{a} {v}\n")
                print(f"wrote {out}")
            return True
    print(f"FAILED: {len(uncovered)} classes uncovered after all steps "
          f"({len(congs)} congs)")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--steps", required=True)
    ap.add_argument("--vmax", type=int, default=None)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    run(args.T, parse_steps(args.steps), args.vmax, args.out)


if __name__ == "__main__":
    main()

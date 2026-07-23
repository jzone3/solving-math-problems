#!/usr/bin/env python3
"""Symbolic Nielsen-style constructor, v2: prime-power block steps + fast greedy.

Differences from engine6:
  - steps are (p, k) blocks: M -> M * p^k in one step, children = p^k per
    class, candidate moduli v = d * p^j (old_e < j <= new_e, d | coprime part)
    with T <= v <= vmax.  Block steps give far richer alignment choices.
  - proportional-threshold sweep greedy instead of full argmax per pick:
    rounds over candidates ascending; take (v, best a) if it kills >=
    eff * |rem| / v children; final round accepts any positive kill.
  - abort if uncovered count exceeds --budget (schedule infeasible).

Usage: python3 engine7.py -T 12 --steps "2^8,3^5,5^3,7^2,11,13,..." \
       --vmax 2000000 --budget 3000000 [-o cover.txt]
"""
import argparse
import time
from collections import defaultdict

import numpy as np

NP_LIMIT = 1 << 62  # use numpy path while lcm fits in int64


def parse_steps(s):
    out = []
    for part in s.split(","):
        if "^" in part:
            p, k = part.split("^")
            out.append((int(p), int(k)))
        else:
            out.append((int(part), 1))
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


def cover_step_np(rem, cands, used, congs, eff, final_any=True):
    """numpy fast path: rem is a uint64 array of class labels (< 2^62)."""
    cands = sorted(v for v in cands if v not in used)
    for rnd in range(60):
        if rem.size == 0 or not cands:
            break
        kills = 0
        keep = []
        thresh_final = final_any and (rnd >= 8)
        for v in cands:
            if rem.size == 0:
                keep.append(v)
                continue
            r = (rem % v).astype(np.int64)
            bc = np.bincount(r, minlength=v)
            a = int(bc.argmax())
            cnt = int(bc[a])
            need = 1 if thresh_final else max(1, int(eff * rem.size / v))
            if cnt >= need:
                used.add(v)
                congs.append((a, v))
                rem = rem[r != a]
                kills += cnt
            else:
                keep.append(v)
        cands = keep
        if kills == 0 and (thresh_final or not final_any):
            break
    return rem


def cover_step(rem, cands, used, congs, eff, verbose):
    """Sweep-greedy set cover of `rem` (set of bigints, classes mod M') using
    candidate moduli (each usable once). Mutates used/congs; returns leftover."""
    cands = sorted(v for v in cands if v not in used)
    for rnd in range(60):
        if not rem or not cands:
            break
        kills_this_round = 0
        keep = []
        thresh_final = (rnd >= 8)
        for v in cands:
            if not rem:
                keep.append(v)
                continue
            buckets = defaultdict(int)
            for c in rem:
                buckets[c % v] += 1
            a, cnt = max(buckets.items(), key=lambda kv: kv[1])
            need = 1 if thresh_final else max(1, int(eff * len(rem) / v))
            if cnt >= need:
                used.add(v)
                congs.append((a, v))
                rem = {c for c in rem if c % v != a}
                kills_this_round += cnt
            else:
                keep.append(v)
        cands = keep
        if kills_this_round == 0 and thresh_final:
            break
    return rem


def run(T, steps, vmax, budget, out=None, eff=0.5, verbose=True):
    M = 1
    fac = {}
    uncovered = [0]
    used = set()
    congs = []
    t0 = time.time()
    for si, (p, k) in enumerate(steps):
        e_old = fac.get(p, 0)
        e_new = e_old + k
        pk = p ** k
        if len(uncovered) * pk > budget:
            print(f"ABORT step {si+1}: children {len(uncovered)*pk} > budget")
            return False
        Mp = M * pk
        use_np = Mp < NP_LIMIT
        if use_np:
            base = np.asarray(uncovered, dtype=np.uint64)
            children = (base[:, None] +
                        (np.arange(pk, dtype=np.uint64) * np.uint64(M))[None, :]
                        ).ravel()
        else:
            children = set()
            for r in uncovered:
                for j in range(pk):
                    children.add(r + j * M)
        base_fac = dict(fac)
        base_fac.pop(p, None)
        cands = set()
        pj = p ** (e_old + 1)
        for j in range(e_old + 1, e_new + 1):
            cap_d = None if vmax is None else vmax // pj
            if cap_d is not None and cap_d < 1:
                break
            for d in divisors_of(base_fac, cap=cap_d):
                v = d * pj
                if v >= T:
                    cands.add(v)
            pj *= p
        if use_np:
            rem = cover_step_np(children, cands, used, congs, eff)
            uncovered = [int(c) for c in rem]
        else:
            rem = cover_step(children, cands, used, congs, eff, verbose)
            uncovered = sorted(rem)
        M = Mp
        fac[p] = e_new
        if verbose:
            print(f"step {si+1}/{len(steps)} p={p}^{e_new}: "
                  f"uncovered {len(uncovered)}, congs {len(congs)}, "
                  f"t={time.time()-t0:.0f}s", flush=True)
        if not uncovered:
            print(f"COVERED. {len(congs)} congs, min mod "
                  f"{min(v for _, v in congs)}, lcm ~ 10^{len(str(M))-1}")
            if out:
                with open(out, "w") as f:
                    f.write(f"# engine7 T={T}\n")
                    for a, v in congs:
                        f.write(f"{a} {v}\n")
                print(f"wrote {out}")
            return True
    print(f"FAILED: {len(uncovered)} uncovered, {len(congs)} congs")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--steps", required=True)
    ap.add_argument("--vmax", type=int, default=2_000_000)
    ap.add_argument("--budget", type=int, default=3_000_000)
    ap.add_argument("--eff", type=float, default=0.5)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    run(args.T, parse_steps(args.steps), args.vmax, args.budget, args.out,
        args.eff)


if __name__ == "__main__":
    main()

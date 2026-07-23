#!/usr/bin/env python3
"""Native local search over the covering-system search space itself.

State: residue a_n for every divisor n>=m of N (every modulus used; recip surplus
means unused moduli are wasteful anyway). Energy: number of uncovered t in Z_N,
maintained incrementally via a coverage-multiplicity array. Move: reassign one
modulus to the residue minimizing resulting energy (min-conflicts), with noise.
Cost of evaluating all residues of modulus n: O(N) via bucket counts.

Usage: anneal.py N m time_s [out.json] [seed]
"""
import json, random, sys, time


def divisors(N):
    ds = []
    i = 1
    while i * i <= N:
        if N % i == 0:
            ds.append(i)
            if i != N // i:
                ds.append(N // i)
        i += 1
    return sorted(ds)


def run(N, m, budget, out=None, seed=1):
    rng = random.Random(seed)
    mods = [d for d in divisors(N) if d >= m and d > 1]
    res = {n: rng.randrange(n) for n in mods}
    cnt = [0] * N  # coverage multiplicity
    for n in mods:
        for t in range(res[n], N, n):
            cnt[t] += 1
    energy = sum(1 for c in cnt if c == 0)
    best = energy
    t0 = time.time()
    it = 0
    while energy and time.time() - t0 < budget:
        it += 1
        n = rng.choice(mods)
        a_old = res[n]
        # uniquely-covered counts per residue class of n, and hole counts
        holes = [0] * n   # holes[b] = #uncovered t with t%n==b (if n moved away)
        uniq = [0] * n    # uniq[b] = #t covered ONLY by n at residue b
        for t in range(a_old, N, n):
            if cnt[t] == 1:
                uniq[a_old] += 1
        for t in range(N):
            if cnt[t] == 0:
                holes[t % n] += 1
        # energy delta of moving n from a_old to b:
        #   + uniq[a_old] (t's that lose their only cover)  - holes[b]
        # except b == a_old: 0
        if rng.random() < 0.02:
            b = rng.randrange(n)  # noise
        else:
            gain = [holes[b] - (0 if b == a_old else uniq[a_old])
                    for b in range(n)]
            gmax = max(gain)
            cands = [b for b in range(n) if gain[b] == gmax]
            b = rng.choice(cands)
        if b != a_old:
            for t in range(a_old, N, n):
                cnt[t] -= 1
                if cnt[t] == 0:
                    energy += 1
            for t in range(b, N, n):
                if cnt[t] == 0:
                    energy -= 1
                cnt[t] += 1
            res[n] = b
        if energy < best:
            best = energy
            if it % 1 == 0:
                print(f"best={best} it={it} t={time.time()-t0:.1f}s", flush=True)
    if energy == 0:
        sol = sorted(((res[n], n) for n in mods), key=lambda x: x[1])
        cov = bytearray(N)
        for a, n in sol:
            for t in range(a, N, n):
                cov[t] = 1
        assert all(cov)
        print(f"SOLVED size={len(sol)} t={time.time()-t0:.1f}s", flush=True)
        if out:
            json.dump({"m": m, "N": N, "cover": sol}, open(out, "w"))
        return sol
    print(f"NOSOLUTION best={best} t={time.time()-t0:.1f}s", flush=True)
    return None


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    out = sys.argv[4] if len(sys.argv) > 4 else None
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    run(N, m, budget, out, seed)

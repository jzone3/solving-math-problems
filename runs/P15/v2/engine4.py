#!/usr/bin/env python3
"""P15 V2 engine v4: fixed smooth N, dense bitmask set cover over Z_N.

Covering Z with distinct moduli dividing N (all >= T) == covering Z_N with
residue classes a mod v, v | N, each divisor value used at most once.

Greedy: several sweeps over divisor values (ascending), each value placed at
the argmax uncovered residue class, accepted if kills >= gate * |U|/v (gate
relaxed each sweep). Endgame: any remaining uncovered point can be finished by
any unused divisor (residue = point mod v), assigned greedily by kills.
"""
import argparse
import time
import numpy as np


def factorize_spec(s):
    """'2^7,3^4,5^2,7,11,13' -> dict {2:7,3:4,5:2,7:1,11:1,13:1}"""
    out = {}
    for tok in s.split(","):
        if "^" in tok:
            b, e = tok.split("^")
            out[int(b)] = int(e)
        else:
            out[int(tok)] = out.get(int(tok), 0) + 1
    return out


def divisors(fac, lo=1, hi=None):
    out = [1]
    for p, e in fac.items():
        out = [d * p ** k for d in out for k in range(e + 1)]
    out = [d for d in out if d >= lo and (hi is None or d <= hi)]
    return sorted(out)


def class_counts(U, v):
    """Uncovered count per residue class mod v; U bool array len N, v | N."""
    return U.reshape(-1, v).sum(axis=0, dtype=np.int64)


def best_class(pts, v):
    """argmax residue class of v over an index array, memory O(len(pts))."""
    if pts.size == 0:
        return 0, 0
    r = pts % v
    if v <= 4 * pts.size:
        bc = np.bincount(r.astype(np.int64), minlength=v)
        a = int(bc.argmax())
        return a, int(bc[a])
    vals, counts = np.unique(r, return_counts=True)
    j = int(counts.argmax())
    return int(vals[j]), int(counts[j])


def cover(N_fac, T, gates=(0.99, 0.9, 0.7, 0.4, 0.15, 0.0, 0.0), verbose=True):
    N = 1
    for p, e in N_fac.items():
        N *= p ** e
    divs = divisors(N_fac, lo=T)
    U = np.ones(N, dtype=bool)
    used = set()
    congs = []
    t0 = time.time()
    rem = N
    for si, gate in enumerate(gates):
        placed = 0
        for v in divs:
            if v in used:
                continue
            if rem == 0:
                break
            cnt = class_counts(U, v)
            a = int(cnt.argmax())
            c = int(cnt[a])
            if c == 0:
                continue
            if gate > 0 and c < gate * (N // v):
                continue  # class not full enough; save value for later
            # accept
            idx = np.arange(a, N, v)
            U[idx] = False
            rem -= c
            used.add(v)
            congs.append((a, v))
            placed += 1
        rem = int(U.sum())
        if verbose:
            print(f" sweep {si} (gate={gate}): placed={placed} "
                  f"uncovered={rem} congs={len(congs)} t={time.time()-t0:.0f}s",
                  flush=True)
        if rem == 0:
            break
    rem = int(U.sum())
    return congs, rem, N


def repair(N, divs, congs, U, rounds=200, frac=0.06, seed=0, t_budget=600,
           verbose=True):
    """Ruin-and-recreate with incremental coverage counts. Repeatedly remove a
    random subset of placements, re-place those values greedily on the current
    uncovered set (argmax residue class). Accepts non-worsening moves."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    cnt_cover = np.zeros(N, dtype=np.uint16)
    for a, v in congs:
        cnt_cover[a::v] += 1
    cur = list(congs)
    rem = int((cnt_cover == 0).sum())
    best, bestrem = list(cur), rem
    it = 0
    while it < rounds and time.time() - t0 < t_budget and bestrem > 0:
        it += 1
        k = max(1, int(len(cur) * frac))
        drop = rng.choice(len(cur), size=k, replace=False)
        drop_set = set(drop.tolist())
        dropped = [cur[i] for i in drop_set]
        kept = [c for i, c in enumerate(cur) if i not in drop_set]
        for a, v in dropped:
            cnt_cover[a::v] -= 1
        uncov = np.flatnonzero(cnt_cover == 0)
        newc = list(kept)
        for a_old, v in sorted(dropped, key=lambda t: t[1]):
            if uncov.size:
                a, _ = best_class(uncov, v)
            else:
                a = int(rng.integers(v))
            cnt_cover[a::v] += 1
            uncov = uncov[uncov % v != a]
            newc.append((a, v))
        rem = uncov.size
        if rem <= bestrem:
            if rem < bestrem:
                best, bestrem = list(newc), rem
            cur = newc
        else:
            # revert
            for a, v in newc[len(kept):]:
                cnt_cover[a::v] -= 1
            for a, v in dropped:
                cnt_cover[a::v] += 1
        if verbose and it % 50 == 0:
            print(f"  repair it={it}: best uncovered={bestrem} t={time.time()-t0:.0f}s",
                  flush=True)
    return best, bestrem


def one_opt(N, congs, t_budget=600, seed=0, verbose=True):
    """Exact 1-opt: re-place a used value v elsewhere when the number of new
    points covered exceeds the exclusive coverage lost. Iterate to fixpoint."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    cnt = np.zeros(N, dtype=np.uint16)
    for a, v in congs:
        cnt[a::v] += 1
    cur = {(a, v) for a, v in congs}
    improved = True
    while improved and time.time() - t0 < t_budget:
        improved = False
        uncov = np.flatnonzero(cnt == 0)
        if uncov.size == 0:
            break
        for a, v in sorted(cur, key=lambda t: -t[1]):
            if time.time() - t0 > t_budget:
                break
            idx = np.arange(a, N, v)
            excl = int((cnt[idx] == 1).sum())
            a2, kills = best_class(uncov, v)
            gain = kills - excl
            if gain > 0 or (gain == 0 and excl > 0 and rng.random() < 0.1):
                cnt[idx] -= 1
                cnt[a2::v] += 1
                cur.discard((a, v))
                cur.add((a2, v))
                uncov = np.flatnonzero(cnt == 0)
                improved = True
                if uncov.size == 0:
                    break
        if verbose:
            print(f"  one_opt pass: uncovered={uncov.size} t={time.time()-t0:.0f}s",
                  flush=True)
    rem = int((cnt == 0).sum())
    return sorted(cur, key=lambda t: t[1]), rem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("-N", required=True, help="factor spec e.g. 2^7,3^4,5^2,7,11,13")
    ap.add_argument("--gates", default="0.99,0.9,0.7,0.4,0.15,0,0")
    ap.add_argument("--repair", action="store_true")
    ap.add_argument("--repair-rounds", type=int, default=400)
    ap.add_argument("--repair-budget", type=int, default=600)
    ap.add_argument("--cycles", type=int, default=4)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    gates = tuple(float(x) for x in args.gates.split(","))
    congs, rem, N = cover(fac, args.T, gates)
    if rem > 0 and args.repair:
        for cycle in range(args.cycles):
            U = np.ones(N, dtype=bool)
            for a, v in congs:
                U[np.arange(a, N, v)] = False
            congs, rem = repair(N, None, congs, U, rounds=args.repair_rounds,
                                t_budget=args.repair_budget, seed=cycle)
            if rem == 0:
                break
            congs, rem = one_opt(N, congs, t_budget=args.repair_budget,
                                 seed=cycle)
            if rem == 0:
                break
            print(f" cycle {cycle}: uncovered={rem}", flush=True)
    status = "SUCCESS" if rem == 0 else "INCOMPLETE"
    print(f"T={args.T} N={N} ({args.N}): {status} congs={len(congs)} uncovered={rem}")
    if args.out:
        path = args.out if rem == 0 else args.out + ".part"
        with open(path, "w") as f:
            f.write(f"# T={args.T} N={args.N} engine4 status={status} uncovered={rem}\n")
            for a, v in congs:
                f.write(f"{a} {v}\n")
        print(f"wrote {len(congs)} -> {path}")


if __name__ == "__main__":
    main()

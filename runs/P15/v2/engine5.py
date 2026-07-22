#!/usr/bin/env python3
"""P15 V2 engine v5: huge-N covering search (N beyond RAM bitmask).

Pipeline:
  1. sample-guided greedy sweeps for small/mid values (counts estimated on a
     large uniform sample of Z_N);
  2. exact hole materialization by streaming segments;
  3. exact greedy placement of remaining values on the hole list;
  4. streaming one_opt (re-place a value when new kills > exclusive coverage,
     exclusive coverage computed by streaming its class against the other
     placements) until covered or budget exhausted.

Witness written for solutions/P15/verify.py.
"""
import argparse
import time
import numpy as np
from engine4 import factorize_spec, divisors


def make_sample(N, size, seed=0):
    rng = np.random.default_rng(seed)
    s = rng.integers(0, N, size=size, dtype=np.int64)
    return np.unique(s)


def sample_sweeps(N, divs, sample, gates, vmax_sample, verbose=True):
    used = {}
    S = sample.copy()
    total = S.size
    t0 = time.time()
    for si, gate in enumerate(gates):
        placed = 0
        for v in divs:
            if v in used or v > vmax_sample:
                continue
            if S.size == 0:
                break
            a, c = best_class(S, v)
            if c == 0:
                continue
            exp_full = total / v  # sample points per class if class untouched
            if gate > 0 and c < gate * exp_full:
                continue
            used[v] = a
            S = S[S % v != a]
            placed += 1
        if verbose:
            print(f" sample sweep {si} (gate={gate}): placed={placed} "
                  f"sample_uncov={S.size}/{total} t={time.time()-t0:.0f}s",
                  flush=True)
    return used


def materialize_holes(N, placements, seg=1 << 24, cap=1_200_000_000,
                      verbose=True):
    holes = []
    nholes = 0
    t0 = time.time()
    items = sorted(placements.items())
    for s in range(0, N, seg):
        L = min(seg, N - s)
        cov = np.zeros(L, dtype=bool)
        for v, a in items:
            first = (a - s) % v
            cov[first::v] = True
        h = np.flatnonzero(~cov).astype(np.int64) + s
        nholes += h.size
        if nholes > cap:
            raise MemoryError(f"holes exceed cap ({nholes} > {cap})")
        holes.append(h)
        if verbose and (s // seg) % 256 == 0:
            print(f"  materialize {s/N:.0%}: holes so far {nholes} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    return np.concatenate(holes) if holes else np.zeros(0, dtype=np.int64)


def best_class(holes, v):
    """argmax residue class of v on the hole list, memory O(|holes|)."""
    if holes.size == 0:
        return 0, 0
    r = holes % v
    if v <= 4 * holes.size:
        bc = np.bincount(r.astype(np.int64), minlength=v)
        a = int(bc.argmax())
        return a, int(bc[a])
    vals, counts = np.unique(r, return_counts=True)
    j = int(counts.argmax())
    return int(vals[j]), int(counts[j])


def place_on_holes(holes, divs, used, verbose=True):
    t0 = time.time()
    placed = 0
    for v in divs:
        if v in used:
            continue
        if holes.size == 0:
            break
        a, c = best_class(holes, v)
        if c == 0:
            continue
        used[v] = a
        holes = holes[holes % v != a]
        placed += 1
    if verbose:
        print(f" hole placement: {placed} values, holes left {holes.size} "
              f"t={time.time()-t0:.0f}s", flush=True)
    return holes, used


def stream_excl(N, placements, want=None, seg=1 << 24):
    """One full pass over Z_N. Returns dict v -> exclusive-coverage size for
    every placement, and (if want) dict v -> np.array of exclusive points for
    v in want. Exclusive = covered only by that placement."""
    items = sorted(placements.items())
    sizes = {v: 0 for v, _ in items}
    pts = {v: [] for v in (want or ())}
    for s in range(0, N, seg):
        L = min(seg, N - s)
        cnt = np.zeros(L, dtype=np.int16)
        for v, a in items:
            first = (a - s) % v
            cnt[first::v] += 1
        for v, a in items:
            first = (a - s) % v
            sel = cnt[first::v] == 1
            ns = int(sel.sum())
            sizes[v] += ns
            if want and v in pts and ns:
                pts[v].append(s + first + v * np.flatnonzero(sel).astype(np.int64))
    out_pts = {v: (np.concatenate(l) if l else np.zeros(0, dtype=np.int64))
               for v, l in pts.items()}
    return sizes, out_pts


def one_opt_stream(N, used, holes, t_budget=3600, seed=0, verbose=True):
    """Pass-based batched 1-opt. Each pass: one stream computes exclusive
    sizes for all placements; candidate moves (new kills > exclusive loss)
    are selected; a second stream collects the exclusive points of just the
    candidates; moves are applied sequentially with exact hole updates."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    npasses = 0
    best_used, best_holes = dict(used), holes
    while holes.size and time.time() - t0 < t_budget:
        npasses += 1
        p_bad = max(0.02, 0.25 * 0.8 ** npasses)
        sizes, _ = stream_excl(N, used)
        cand = []
        for v, a in used.items():
            a2, gain = best_class(holes, v)
            if gain == 0:
                continue
            if gain > sizes[v] or (gain == sizes[v] and rng.random() < 0.15):
                cand.append(v)
        if not cand:
            # plateau: force-move a few placements with smallest exclusive sets
            worst = sorted(used, key=lambda v: sizes[v])[:8]
            cand = [v for v in worst if sizes[v] < 4 * max(1, holes.size)]
            if not cand:
                break
        _, excl_pts = stream_excl(N, used, want=set(cand))
        moved = 0
        for v in sorted(cand, reverse=True):
            if holes.size == 0:
                break
            a2, gain = best_class(holes, v)
            ep = excl_pts[v]
            if gain < ep.size and not (npasses > 1 and rng.random() < p_bad):
                continue
            used[v] = a2
            holes = holes[holes % v != a2]
            if ep.size:
                keep = ep[ep % v != a2]
                holes = np.unique(np.concatenate([holes, keep]))
            moved += 1
        # incremental hole tracking is only a heuristic within the pass
        # (exclusive-point snapshots go stale as moves are applied); recompute
        # holes exactly before deciding anything further.
        holes = materialize_holes(N, used, verbose=False)
        if holes.size < best_holes.size:
            best_used, best_holes = dict(used), holes
        elif holes.size > 2 * best_holes.size:
            used, holes = dict(best_used), best_holes  # elitist restore
        if verbose:
            print(f"  one_opt pass {npasses}: moved={moved} holes={holes.size} "
                  f"best={best_holes.size} t={time.time()-t0:.0f}s", flush=True)
        if moved == 0:
            break
    if best_holes.size < holes.size:
        used, holes = best_used, best_holes
    return holes, used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("-N", required=True)
    ap.add_argument("--sample", type=int, default=20_000_000)
    ap.add_argument("--vmax-sample", type=int, default=100_000)
    ap.add_argument("--gates", default="0.98,0.9,0.7,0.4,0.15,0,0")
    ap.add_argument("--budget", type=int, default=7200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    fac = factorize_spec(args.N)
    N = 1
    for p, e in fac.items():
        N *= p ** e
    divs = divisors(fac, lo=args.T)
    print(f"N={N} ({args.N}) T={args.T}: {len(divs)} divisor values, "
          f"recip={sum(1/d for d in divs):.3f}", flush=True)
    gates = tuple(float(x) for x in args.gates.split(","))
    sample = make_sample(N, args.sample, seed=args.seed)
    used = sample_sweeps(N, divs, sample, gates, args.vmax_sample)
    print(f"phase1 done: {len(used)} placements", flush=True)
    holes = materialize_holes(N, used)
    print(f"phase2: exact holes = {holes.size} (density {holes.size/N:.2e})",
          flush=True)
    holes, used = place_on_holes(holes, divs, used)
    holes, used = one_opt_stream(N, used, holes, t_budget=args.budget,
                                 seed=args.seed)
    status = "SUCCESS" if holes.size == 0 else "INCOMPLETE"
    print(f"T={args.T} N={N}: {status} congs={len(used)} holes={holes.size}")
    path = args.out if holes.size == 0 else args.out + ".part"
    with open(path, "w") as f:
        f.write(f"# T={args.T} N={args.N} engine5 status={status} "
                f"holes={holes.size}\n")
        for v in sorted(used):
            f.write(f"{used[v]} {v}\n")
    print(f"wrote {len(used)} -> {path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Full-N greedy set-cover + kissat repair of the residual holes.
Usage: greedy_sat.py N m stop_ratio sat_timeout [out.json] [seed]"""
import json, random, sys, time
from collections import defaultdict
from layered2 import sat_final, divisors


def run(N, m, stop_ratio=0.02, sat_timeout=1800, out=None, seed=0):
    rng = random.Random(seed)
    mods = [d for d in divisors(N) if d >= m and d > 1]
    holes = set(range(N))
    avail = set(mods)
    chosen = []
    t0 = time.time()
    while holes and avail:
        best = None
        for n in avail:
            cnt = defaultdict(int)
            for h in holes:
                cnt[h % n] += 1
            a, c = max(cnt.items(), key=lambda kv: (kv[1], rng.random()))
            if best is None or c > best[2] or (c == best[2] and n > best[1]):
                best = (a, n, c)
        a, n, c = best
        if c < stop_ratio * len(holes):
            break
        chosen.append((a, n))
        avail.discard(n)
        holes = {h for h in holes if h % n != a}
    print(f"greedy: used {len(chosen)} mods, {len(holes)} holes left, "
          f"{len(avail)} mods for SAT, t={time.time()-t0:.1f}s", flush=True)
    sol, status = sat_final(sorted(holes), sorted(avail), sat_timeout)
    print(f"final SAT: {status}", flush=True)
    if sol is None:
        return None
    cover = chosen + sol
    cov = bytearray(N)
    ms = [n for _, n in cover]
    assert len(ms) == len(set(ms)) and min(ms) >= m
    for a, n in cover:
        for t in range(a, N, n):
            cov[t] = 1
    assert all(cov)
    print(f"COVER size={len(cover)} verified", flush=True)
    if out:
        json.dump({"m": m, "N": N, "cover": cover}, open(out, "w"))
    return cover


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    sr = float(sys.argv[3]) if len(sys.argv) > 3 else 0.02
    st = float(sys.argv[4]) if len(sys.argv) > 4 else 1800
    out = sys.argv[5] if len(sys.argv) > 5 else None
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    run(N, m, sr, st, out, seed)

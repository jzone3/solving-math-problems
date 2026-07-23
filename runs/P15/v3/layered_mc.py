#!/usr/bin/env python3
"""Layered (Krukenberg-style) construction driven by the C hole-set engine.

Ladder of prime powers builds N; at each layer, holes are lifted and the
holes_mc engine assigns residues to ALL still-unused divisors of the current
partial lcm, minimizing leftover holes. Layer solutions are frozen (moduli
consumed). Succeeds when a layer reaches 0 holes.

Usage: layered_mc.py m "q1,q2,..." layer_secs [out.json] [seed]
"""
import json, subprocess, sys, time


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


def solve_layer(holes, mods, secs, seed, tag):
    prob = f"/tmp/lay_{tag}.txt"
    with open(prob, "w") as f:
        f.write(f"{len(holes)} {len(mods)}\n")
        f.write(" ".join(map(str, holes)) + "\n")
        f.write(" ".join(map(str, mods)) + "\n")
    outp = f"/tmp/lay_{tag}.out"
    p = subprocess.run(["./holes_mc", prob, str(secs), str(seed), outp,
                        str(max(5.0, secs / 10))],
                       capture_output=True, text=True)
    sol = []
    for line in open(outp):
        a, n = map(int, line.split())
        sol.append((a, n))
    solved = p.returncode == 0
    return sol, solved


def run(m, ladder, layer_secs, out=None, seed=1, hole_cap=5000000):
    Nk = 1
    holes = [0]
    used = set()
    cover = []
    for idx, q in enumerate(ladder):
        holes = [h + j * Nk for h in holes for j in range(q)]
        Nk *= q
        if len(holes) > hole_cap:
            print(f"hole cap exceeded {len(holes)}", flush=True)
            return None, Nk
        mods = [d for d in divisors(Nk) if d >= m and d not in used]
        if not mods:
            print(f"layer {idx}: no mods left", flush=True)
            continue
        t0 = time.time()
        sol, solved = solve_layer(holes, mods, layer_secs, seed + idx, f"{m}_{idx}")
        # freeze only classes that cover at least one current hole (keep others
        # unused for later layers)
        hs = set(holes)
        kept = []
        for a, n in sol:
            hit = any(h % n == a for h in holes)
            if hit:
                kept.append((a, n))
        covered = set()
        for a, n in kept:
            for h in holes:
                if h % n == a:
                    covered.add(h)
        holes = [h for h in holes if h not in covered]
        for a, n in kept:
            used.add(n)
        cover += kept
        print(f"layer {idx} q={q} N={Nk} kept={len(kept)} holes={len(holes)} "
              f"t={time.time()-t0:.1f}s", flush=True)
        if not holes:
            ms = [n for _, n in cover]
            assert len(ms) == len(set(ms)) and min(ms) >= m
            print(f"COVER size={len(cover)} lcm={Nk}", flush=True)
            if out:
                json.dump({"m": m, "N": Nk,
                           "cover": sorted(cover, key=lambda x: x[1])},
                          open(out, "w"))
            return cover, Nk
    print("FAILED", flush=True)
    return None, Nk


if __name__ == "__main__":
    m = int(sys.argv[1])
    ladder = [int(x) for x in sys.argv[2].split(",")]
    secs = float(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else None
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    run(m, ladder, secs, out, seed)

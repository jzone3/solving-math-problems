#!/usr/bin/env python3
"""P15 V3 layered engine v2 (scales to large lcm):
interior layers: fast greedy set-cover over current holes (best residue per unused
divisor, repeatedly picking the globally best class);
final phase: exact SAT (kissat) requiring all remaining holes covered by still-unused
divisors of the final lcm.

Holes are tracked explicitly, so lcm can vastly exceed direct-SAT range.
Distinct moduli enforced globally.
"""
import json, subprocess, sys, time
from collections import defaultdict

KISSAT = "/home/ubuntu/kissat/build/kissat"


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


def greedy_layer(holes, mods, stop_ratio=0.0):
    """Repeatedly pick class (n,a) hitting most holes. Returns chosen, remaining holes.
    Stops when the best class hits <= stop_ratio * len(holes) (then leave for later)."""
    holes = set(holes)
    chosen = []
    avail = set(mods)
    while holes and avail:
        best = None
        for n in avail:
            cnt = defaultdict(int)
            for h in holes:
                cnt[h % n] += 1
            a, c = max(cnt.items(), key=lambda kv: kv[1])
            # prefer larger modulus on ties (conserve small moduli)
            if best is None or c > best[2] or (c == best[2] and n > best[1]):
                best = (a, n, c)
        a, n, c = best
        if c <= stop_ratio * len(holes) or c == 0:
            break
        chosen.append((a, n))
        avail.discard(n)
        holes = {h for h in holes if h % n != a}
    return chosen, holes


def sat_final(holes, mods, timeout=3600):
    """Exact: cover all holes with unused mods (one residue each). kissat decision."""
    holes = sorted(holes)
    nv = 0
    var = {}
    hits = defaultdict(list)
    lines = []
    for n in mods:
        byres = defaultdict(list)
        for h in holes:
            byres[h % n].append(h)
        lits = []
        for a, hs in byres.items():
            nv += 1
            var[(n, a)] = nv
            lits.append(nv)
            for h in hs:
                hits[h].append(nv)
        # sequential AMO
        if len(lits) > 1:
            s = list(range(nv + 1, nv + len(lits)))
            nv += len(lits) - 1
            lines.append((-lits[0], s[0]))
            for i in range(1, len(lits) - 1):
                lines.append((-lits[i], s[i]))
                lines.append((-s[i - 1], s[i]))
                lines.append((-lits[i], -s[i - 1]))
            lines.append((-lits[-1], -s[-1]))
    for h in holes:
        lines.append(tuple(hits[h]))
    cnf = f"/tmp/final_{len(holes)}_{time.time():.0f}.cnf"
    with open(cnf, "w") as f:
        f.write(f"p cnf {nv} {len(lines)}\n")
        for cl in lines:
            f.write(" ".join(map(str, cl)) + " 0\n")
    p = subprocess.run([KISSAT, "-q", f"--time={int(timeout)}", cnf],
                       capture_output=True, text=True)
    if "s SATISFIABLE" not in p.stdout:
        return None, ("UNSAT" if "s UNSATISFIABLE" in p.stdout else "TIMEOUT")
    assign = set()
    for line in p.stdout.splitlines():
        if line.startswith("v "):
            for tok in line[2:].split():
                l = int(tok)
                if l > 0:
                    assign.add(l)
    return [(a, n) for (n, a), v in var.items() if v in assign], "SAT"


def run(m, ladder, hole_cap=3000000, stop_ratio=0.0, final_timeout=3600,
        final_window=2, final_greedy=None, maxsat_holes=4000, maxsat_budget=240):
    """Interior layers: MaxSAT (small hole sets) or greedy. Final phase: the last
    final_window ladder factors are lifted at once and solved exactly with kissat
    (joint choice over all remaining unused divisors of the full lcm)."""
    Nk = 1
    holes = [0]
    used = set()
    cover = []
    cut = max(0, len(ladder) - final_window)
    for idx, q in enumerate(ladder[:cut]):
        holes = [h + j * Nk for h in holes for j in range(q)]
        if len(holes) > hole_cap:
            print(f"hole cap exceeded ({len(holes)})", flush=True)
            return None, Nk * q
        Nk *= q
        mods = [d for d in divisors(Nk) if d >= m and d not in used]
        t0 = time.time()
        if len(holes) <= maxsat_holes:
            from layered import layer_solve
            chosen, cost, dt = layer_solve(holes, mods, per_layer_budget=maxsat_budget)
            holes = {h for h in holes if all(h % n != a for a, n in chosen)}
        else:
            chosen, holes = greedy_layer(holes, mods, stop_ratio)
        for a, n in chosen:
            used.add(n)
        cover += chosen
        print(f"layer {idx} q={q} N={Nk} used={len(chosen)} "
              f"holes_left={len(holes)} t={time.time()-t0:.1f}s", flush=True)
        if not holes:
            return cover, Nk
    # final phase: lift through remaining factors jointly
    for q in ladder[cut:]:
        holes = [h + j * Nk for h in holes for j in range(q)]
        Nk *= q
    if len(holes) > hole_cap:
        print(f"hole cap exceeded in final phase ({len(holes)})", flush=True)
        return None, Nk
    mods = [d for d in divisors(Nk) if d >= m and d not in used]
    if final_greedy is not None:
        chosen, holes2 = greedy_layer(holes, mods, stop_ratio=final_greedy)
    else:
        chosen, holes2 = [], set(holes)
    rem_mods = [d for d in mods if d not in {n for _, n in chosen}]
    print(f"  final phase: N={Nk} holes={len(holes2)} mods={len(rem_mods)}", flush=True)
    t0 = time.time()
    sat_sol, status = sat_final(holes2, rem_mods, final_timeout)
    print(f"  final SAT: {status} t={time.time()-t0:.1f}s", flush=True)
    if sat_sol is None:
        return None, Nk
    cover += chosen + sat_sol
    return cover, Nk


def verify_explicit(cover, m, N):
    mods = [n for _, n in cover]
    assert len(mods) == len(set(mods)) and min(mods) >= m
    cov = bytearray(N)
    for a, n in cover:
        assert N % n == 0
        for t in range(a % n, N, n):
            cov[t] = 1
    return all(cov)


if __name__ == "__main__":
    m = int(sys.argv[1])
    ladder = [int(x) for x in sys.argv[2].split(",")]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    ft = float(sys.argv[4]) if len(sys.argv) > 4 else 3600
    fw = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    cover, N = run(m, ladder, final_timeout=ft, final_window=fw)
    if cover is None:
        print("FAILED, lcm", N)
        sys.exit(1)
    ok = verify_explicit(cover, m, N)
    print(f"cover: {len(cover)} congruences, lcm={N}, verified={ok}")
    if ok and out:
        json.dump({"m": m, "N": N, "cover": cover}, open(out, "w"))
        print("written", out)

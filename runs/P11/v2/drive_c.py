#!/usr/bin/env python3
"""Driver: enumerate (subgroup H, character chi) cases for CW(n,k) and run the
C DFS engine (orbit_dfs) on each.  Mirrors orbit_search.py's case enumeration.

Usage: python3 drive_c.py n k [--max-orbits M] [--signed] [--case-timeout S]
                              [--only-exceeded FILE]  # not implemented; runs all
"""
import subprocess, sys, time, os
from orbit_search import subgroups, orbits_of, characters, build_pats, units

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orbit_dfs")


def case_input(n, k, pats, fold_d=0):
    lines = [f"{n} {k} {len(pats)}"]
    for size, ent, _es in pats:
        if ent is None:
            lines.append("0")
        else:
            parts = [str(len(ent))]
            for p, s in sorted(ent.items()):
                parts.append(f"{p} {s}")
            lines.append(" ".join(parts))
    if fold_d:
        tg = fold_targets(fold_d, k)
        lines.append(f"FOLD {fold_d} {len(tg)}")
        for size, ent, _es in pats:
            cnt = [0] * fold_d
            if ent is not None:
                for p, s in ent.items():
                    cnt[p % fold_d] += s
            lines.append(" ".join(map(str, cnt)))
        for t in tg:
            lines.append(" ".join(map(str, t)))
    return "\n".join(lines) + "\n"


_fold_cache = {}


def fold_targets(d, k):
    """All integer vectors b of length d with sum b = +-sqrt(k), sum b^2 = k,
    and folded autocorrelation over Z_d zero for all nonzero shifts."""
    key = (d, k)
    if key in _fold_cache:
        return _fold_cache[key]
    import math
    s = math.isqrt(k)
    assert s * s == k
    out = []
    vec = [0] * d

    def rec(j, rem_sq, cur_sum):
        if j == d:
            if rem_sq == 0 and abs(cur_sum) == s:
                for t in range(1, d):
                    if sum(vec[i] * vec[(i + t) % d] for i in range(d)) != 0:
                        return
                out.append(tuple(vec))
            return
        # bound remaining sum reachability
        m = math.isqrt(rem_sq)
        rem_slots = d - j
        if abs(cur_sum) - m * rem_slots > s:
            return
        for v in range(-m, m + 1):
            if v * v <= rem_sq:
                vec[j] = v
                rec(j + 1, rem_sq - v * v, cur_sum + v)
        vec[j] = 0

    rec(0, k, 0)
    _fold_cache[key] = out
    return out


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    signed = "--signed" in sys.argv
    mo, ct, fd = 40, 3600, 0
    for i, arg in enumerate(sys.argv):
        if arg == "--max-orbits":
            mo = int(sys.argv[i + 1])
        if arg == "--case-timeout":
            ct = int(sys.argv[i + 1])
        if arg == "--fold":
            fd = int(sys.argv[i + 1])
    subs = subgroups(n)
    print(f"# CW({n},{k}) C-driver: |Z_{n}^*|={len(units(n))}, {len(subs)} subgroups, "
          f"max_orbits={mo} signed={signed} case_timeout={ct}s", flush=True)
    t0 = time.time()
    total_w, exceeded, done = 0, [], 0
    for H in subs:
        if len(H) == 1:
            continue
        orbs = orbits_of(n, H)
        r = len(orbs)
        if r > mo:
            continue
        chars = characters(H, n) if signed else [None]
        for ci, chi in enumerate(chars):
            if chi is not None and all(v == 1 for v in chi.values()):
                continue
            pats = build_pats(n, H, orbs, chi)
            inp = case_input(n, k, pats, fd)
            res = subprocess.run([BIN, str(ct)], input=inp, capture_output=True, text=True)
            out = res.stdout.strip().splitlines()
            tag = f"|H|={len(H)} r={r} chi#{ci}"
            for line in out:
                if line.startswith("WITNESS"):
                    total_w += 1
                    print(f"!! {tag} {line}", flush=True)
            last = out[-1] if out else "NO_OUTPUT"
            if last.startswith("EXCEEDED"):
                exceeded.append((sorted(H), ci))
                print(f"  EXCEEDED {tag}: {last}", flush=True)
            else:
                done += 1
                print(f"  case {tag}: {last}", flush=True)
    print(f"# done CW({n},{k}): {done} cases complete, {len(exceeded)} exceeded, "
          f"{time.time()-t0:.1f}s, {total_w} witnesses", flush=True)
    if exceeded:
        print(f"# exceeded cases: {exceeded}", flush=True)


if __name__ == "__main__":
    main()

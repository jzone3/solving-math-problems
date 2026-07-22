#!/usr/bin/env python3
"""Driver: enumerate (subgroup H, character chi) cases for CW(n,k) and run the
C DFS engine (orbit_dfs) on each.  Mirrors orbit_search.py's case enumeration.

Usage: python3 drive_c.py n k [--max-orbits M] [--signed] [--case-timeout S]
                              [--only-exceeded FILE]  # not implemented; runs all
"""
import subprocess, sys, time, os
from orbit_search import subgroups, orbits_of, characters, build_pats, units

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orbit_dfs")


def case_input(n, k, pats):
    lines = [f"{n} {k} {len(pats)}"]
    for size, ent, _es in pats:
        if ent is None:
            lines.append("0")
        else:
            parts = [str(len(ent))]
            for p, s in sorted(ent.items()):
                parts.append(f"{p} {s}")
            lines.append(" ".join(parts))
    return "\n".join(lines) + "\n"


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    signed = "--signed" in sys.argv
    mo, ct = 40, 3600
    for i, arg in enumerate(sys.argv):
        if arg == "--max-orbits":
            mo = int(sys.argv[i + 1])
        if arg == "--case-timeout":
            ct = int(sys.argv[i + 1])
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
            inp = case_input(n, k, pats)
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

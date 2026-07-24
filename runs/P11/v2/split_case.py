#!/usr/bin/env python3
"""Run one (n,k,H) orbit case split into parallel prefix jobs.

Usage: python3 split_case.py n k "h1,h2,..." depth nprocs [timeout_per_job] [fold_d] [skip_file]
skip_file: file with one already-completed prefix per line (resume support).
H is given by generators (comma-separated); the full subgroup is generated.
Splits the DFS over all {0,+,-} prefixes of the given depth (first nonzero
forced '+'), runs orbit_dfs on each prefix with nprocs-way parallelism.
"""
import subprocess, sys, os, itertools, time
from concurrent.futures import ThreadPoolExecutor
from orbit_search import orbits_of, build_pats
from drive_c import case_input, BIN


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    gens = [int(x) for x in sys.argv[3].split(",")]
    depth, nprocs = int(sys.argv[4]), int(sys.argv[5])
    tmo = float(sys.argv[6]) if len(sys.argv) > 6 else 0
    fold_d = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    skip = set()
    if len(sys.argv) > 8:
        with open(sys.argv[8]) as f:
            skip = {line.strip() for line in f if line.strip()}
    # generate subgroup
    H = {1}
    frontier = [1]
    while frontier:
        nf = []
        for x in frontier:
            for g in gens:
                y = (x * g) % n
                if y not in H:
                    H.add(y)
                    nf.append(y)
        frontier = nf
    H = frozenset(H)
    orbs = orbits_of(n, H)
    pats = build_pats(n, H, orbs, None)
    inp = case_input(n, k, pats, fold_d)
    # engine's descending-size order for the first `depth` orbits
    order = sorted(range(len(pats)), key=lambda i: -pats[i][0])
    sizes = [pats[order[i]][0] for i in range(depth)]
    print(f"# split CW({n},{k}) |H|={len(H)} r={len(orbs)} depth={depth} "
          f"first sizes={sizes} fold_d={fold_d}", flush=True)
    prefixes = []
    for tup in itertools.product("0+-", repeat=depth):
        # first nonzero must be '+'
        nz = [c for c in tup if c != "0"]
        if nz and nz[0] == "-":
            continue
        w = sum(sizes[i] for i, c in enumerate(tup) if c != "0")
        if w > k:
            continue
        p = "".join(tup)
        if p not in skip:
            prefixes.append(p)
    print(f"# {len(prefixes)} prefix jobs ({len(skip)} skipped)", flush=True)

    t0 = time.time()
    results = {}

    def run(pfx):
        args = [BIN, str(tmo), pfx] if tmo > 0 else [BIN, "0", pfx]
        res = subprocess.run(args, input=inp, capture_output=True, text=True)
        out = res.stdout.strip()
        results[pfx] = out
        for line in out.splitlines():
            if line.startswith("WITNESS"):
                print(f"!! pfx={pfx} {line}", flush=True)
        last = out.splitlines()[-1] if out else "NO_OUTPUT"
        print(f"  pfx={pfx}: {last}", flush=True)

    with ThreadPoolExecutor(max_workers=nprocs) as ex:
        list(ex.map(run, prefixes))
    ndone = sum(1 for v in results.values() if "DONE" in v)
    nexc = sum(1 for v in results.values() if "EXCEEDED" in v)
    nwit = sum(v.count("WITNESS") for v in results.values())
    print(f"# split done: {ndone}/{len(prefixes)} jobs complete, {nexc} exceeded, "
          f"{nwit} witnesses, {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stabilizer decomposition for the sigma^6 quotient."""
import itertools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import highspy
import numpy as np

from orbit_sat_feas import CNF, BALL, N, build_g, digits, orbits_of, totalizer_atmost

ROOT = os.path.dirname(__file__)
KISSAT = os.environ.get("KISSAT", "/home/ubuntu/repos/kissat-build/build/kissat")
VERIFY = os.path.join(os.path.dirname(ROOT), "v1", "verify.py")


def neg_word(w):
    return sum(((-v) % 3) * 3**i for i, v in enumerate(digits(w)))


def quotient_setup(budget):
    perm, smap = build_g([(1, "sigma")] * 6)
    orbits, orb_id = orbits_of(perm, smap)
    reps = [o[0] for o in orbits]
    qball = [tuple(sorted({orb_id[b] for b in BALL[w]})) for w in reps]
    return orbits, orb_id, qball, budget


def stabilizer_maps(orbits, orb_id):
    maps = []
    for negate in (False, True):
        for p in itertools.permutations(range(6)):
            mapping = []
            for orbit in orbits:
                d = digits(orbit[0])
                e = [0] * 6
                for i, j in enumerate(p):
                    e[j] = d[i]
                if negate:
                    e = [(-v) % 3 for v in e]
                w = sum(v * 3**i for i, v in enumerate(e))
                mapping.append(orb_id[w])
            maps.append(tuple(mapping))
    return sorted(set(maps))


def representatives(orbits, orb_id):
    maps = stabilizer_maps(orbits, orb_id)
    seen = set()
    reps = []
    sizes = {}
    for j in range(1, len(orbits)):
        if j in seen:
            continue
        orbit = {m[j] for m in maps}
        seen.update(orbit)
        r = min(orbit)
        reps.append(r)
        sizes[r] = len(orbit)
    return maps, reps, sizes


def write_cnf(path, budget, second):
    orbits, orb_id, qball, _ = quotient_setup(budget)
    cnf = CNF()
    cnf.nv = len(orbits)
    for cols in qball:
        cnf.add(*[j + 1 for j in cols])
    totalizer_atmost(cnf, list(range(1, len(orbits) + 1)), budget)
    cnf.add(1)
    cnf.add(second + 1)
    cnf.write(path)
    return orbits


def make_instances(outdir, budget):
    os.makedirs(outdir, exist_ok=True)
    orbits, orb_id, _, _ = quotient_setup(budget)
    maps, reps, sizes = representatives(orbits, orb_id)
    metadata = {"budget": budget, "orbits": len(orbits), "stabilizer_order": len(maps),
                "representatives": reps,
                "representative_sizes": {str(k): v for k, v in sizes.items()}}
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    for r in reps:
        write_cnf(os.path.join(outdir, f"rep_{r:03d}.cnf"), budget, r)
    return metadata


def decode_verify(output, path, orbits):
    model = set()
    for line in output.splitlines():
        if line.startswith("v "):
            model.update(int(x) for x in line.split()[1:] if x != "0")
    chosen = [w for j, orbit in enumerate(orbits, 1) if j in model for w in orbit]
    code = path + ".code"
    with open(code, "w") as f:
        for w in sorted(chosen):
            f.write("".join(map(str, digits(w))) + "\n")
    check = subprocess.run([sys.executable, VERIFY, code], text=True,
                           capture_output=True)
    return len(chosen), check.returncode


def sat_one(path, timeout):
    started = time.monotonic()
    try:
        proc = subprocess.run([KISSAT, path], text=True, capture_output=True,
                              timeout=timeout)
        status = {10: "SAT", 20: "UNSAT"}.get(proc.returncode, "UNDECIDED")
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        status, output = "UNDECIDED", ""
    elapsed = time.monotonic() - started
    size = verify_rc = None
    if status == "SAT":
        orbits, _, _, _ = quotient_setup(26)
        size, verify_rc = decode_verify(output, path, orbits)
        if verify_rc:
            status = "INVALID_SAT"
    return status, elapsed, size, verify_rc


def ilp_one(rep, budget, timeout, threads, outdir):
    orbits, orb_id, qball, _ = quotient_setup(budget)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", timeout)
    h.setOptionValue("threads", threads)
    h.addVars(len(orbits), np.zeros(len(orbits)), np.ones(len(orbits)))
    ids = np.arange(len(orbits), dtype=np.int32)
    h.changeColsIntegrality(len(orbits), ids,
                            np.full(len(orbits), highspy.HighsVarType.kInteger))
    h.changeColsCost(len(orbits), ids, np.zeros(len(orbits)))
    inf = highspy.kHighsInf
    for cols in qball:
        cols = np.asarray(cols, dtype=np.int32)
        h.addRow(1, inf, len(cols), cols, np.ones(len(cols)))
    h.addRow(-inf, budget, len(orbits), ids, np.ones(len(orbits)))
    h.changeColBounds(0, 1, 1)
    h.changeColBounds(rep, 1, 1)
    started = time.monotonic()
    h.run()
    elapsed = time.monotonic() - started
    status = h.getModelStatus()
    info = h.getInfo()
    if status == highspy.HighsModelStatus.kOptimal:
        x = np.asarray(h.getSolution().col_value)
        chosen = np.where(x > 0.5)[0]
        result = f"FEASIBLE rep={rep} orbits={len(chosen)} seconds={elapsed:.3f}"
    elif status == highspy.HighsModelStatus.kInfeasible:
        result = f"INFEASIBLE rep={rep} seconds={elapsed:.3f}"
    else:
        result = (f"UNDECIDED rep={rep} status={status} seconds={elapsed:.3f} "
                  f"dual_bound={info.mip_dual_bound}")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"rep_{rep:03d}.txt"), "w") as f:
        f.write(result + "\n")
    print(result, flush=True)
    return result


def run_sat(indir, workers, timeout):
    with open(os.path.join(indir, "metadata.json")) as f:
        metadata = json.load(f)
    paths = sorted(x for x in os.listdir(indir) if x.endswith(".cnf"))
    tally = {"SAT": 0, "UNSAT": 0, "UNDECIDED": 0, "INVALID_SAT": 0}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fs = {pool.submit(sat_one, os.path.join(indir, p), timeout): p for p in paths}
        for future in as_completed(fs):
            p = fs[future]
            result = future.result()
            status = result[0]
            tally[status] += 1
            print(f"SAT_RESULT {p} status={status} seconds={result[1]:.3f} "
                  f"size={result[2]} verify_rc={result[3]}", flush=True)
            if status == "SAT":
                print("SAT_VALIDATION_WITNESS " + p, flush=True)
                return tally
    print("SAT_COMPLETE " + json.dumps(tally, sort_keys=True), flush=True)
    return tally


def main():
    cmd = sys.argv[1]
    if cmd == "stats":
        orbits, orb_id, _, _ = quotient_setup(24)
        maps, reps, sizes = representatives(orbits, orb_id)
        print(json.dumps({"orbits": len(orbits), "stabilizer_order": len(maps),
                          "representatives": reps,
                          "sizes": sizes}, sort_keys=True))
    elif cmd == "generate":
        print(json.dumps(make_instances(sys.argv[2], int(sys.argv[3])), sort_keys=True))
    elif cmd == "sat":
        run_sat(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    elif cmd == "ilp":
        ilp_one(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]),
                int(sys.argv[5]), sys.argv[6])
    else:
        raise SystemExit("stats | generate OUTDIR BUDGET | sat INDIR WORKERS TIMEOUT | ilp REP BUDGET TIMEOUT THREADS OUTDIR")


if __name__ == "__main__":
    main()

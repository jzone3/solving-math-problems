#!/usr/bin/env python3
"""Focused cube-and-conquer search for [1,1,1,1,1,1], sigma^6.

The symmetry is translation by the all-ones ternary vector.  Orbit zero is
fixed in every instance, and cube files add unit literals for selected orbit
variables.
"""
import itertools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from orbit_sat_feas import BALL, CNF, N, build_g, digits, orbits_of, totalizer_atmost

LAM = [1] * 6
ASSIGN = ("sigma",) * 6
BRANCH_COUNT = 10
TARGET_DEFAULT = 72


def instance(target):
    perm, smap = build_g(list(zip(LAM, ASSIGN)))
    orbits, orb_id = orbits_of(perm, smap)
    cnf = CNF()
    cnf.nv = len(orbits)
    for w in range(N):
        cnf.add(*sorted({orb_id[b] + 1 for b in BALL[w]}))
    totalizer_atmost(cnf, list(range(1, len(orbits) + 1)), target // 3)
    cnf.add(1)
    return cnf, orbits, orb_id


def write_cnf(cnf, path, units=()):
    with open(path, "w") as f:
        f.write(f"p cnf {cnf.nv} {len(cnf.clauses) + len(units)}\n")
        for clause in cnf.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
        for lit in units:
            f.write(f"{lit} 0\n")


def make_cubes(target, branch_count, outdir):
    cnf, orbits, orb_id = instance(target)
    os.makedirs(outdir, exist_ok=True)
    branch = list(range(2, branch_count + 2))
    metadata = {
        "target": target,
        "branch_vars": branch,
        "orbits": len(orbits),
        "fixed_orbit": 1,
        "base_clauses": len(cnf.clauses),
    }
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    for idx, bits in enumerate(itertools.product((False, True), repeat=len(branch))):
        units = [v if bit else -v for v, bit in zip(branch, bits)]
        write_cnf(cnf, os.path.join(outdir, f"cube_{idx:05d}.cnf"), units)
    return metadata, 2 ** len(branch)


def parse_model(output):
    model = set()
    for line in output.splitlines():
        if line.startswith("v "):
            for token in line.split()[1:]:
                if token != "0":
                    try:
                        value = int(token)
                    except ValueError:
                        continue
                    if value > 0:
                        model.add(value)
    return model


def solve_one(path, timeout, target, orbits):
    kissat = os.environ.get("KISSAT", "/home/ubuntu/repos/kissat-build/build/kissat")
    started = time.monotonic()
    try:
        proc = subprocess.run([kissat, path], text=True, capture_output=True,
                              timeout=timeout)
        status = {10: "SAT", 20: "UNSAT"}.get(proc.returncode, "UNDECIDED")
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired as exc:
        status = "UNDECIDED"
        output = (exc.stdout or "") + (exc.stderr or "")
    elapsed = time.monotonic() - started
    if status == "SAT":
        model = parse_model(output)
        chosen = [w for j, orbit in enumerate(orbits, 1)
                  if j in model for w in orbit]
        workdir = os.path.dirname(path)
        code_path = os.path.join(workdir, os.path.basename(path) + ".code")
        with open(code_path, "w") as f:
            for w in sorted(chosen):
                f.write("".join(map(str, digits(w))) + "\n")
        verify = subprocess.run(
            [sys.executable, "/home/ubuntu/repos/solving-math-problems/runs/P25/v1/verify.py",
             code_path], text=True, capture_output=True)
        if verify.returncode != 0:
            status = "INVALID_SAT"
        return status, elapsed, len(chosen), verify.returncode
    return status, elapsed, None, None


def run_cubes(cubedir, workers, timeout):
    with open(os.path.join(cubedir, "metadata.json")) as f:
        metadata = json.load(f)
    perm, smap = build_g(list(zip(LAM, ASSIGN)))
    orbits, _ = orbits_of(perm, smap)
    paths = sorted(os.path.join(cubedir, x) for x in os.listdir(cubedir)
                   if x.endswith(".cnf"))
    tally = {"total": len(paths), "refuted": 0, "sat": 0, "invalid": 0,
             "undecided": 0}
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(solve_one, p, timeout, metadata["target"], orbits): p
                   for p in paths}
        for future in as_completed(futures):
            path = futures[future]
            status, elapsed, size, verify_rc = future.result()
            if status == "UNSAT":
                tally["refuted"] += 1
            elif status == "SAT":
                tally["sat"] += 1
                print(f"FEASIBLE cube={os.path.basename(path)} size={size} "
                      f"verify_rc={verify_rc}", flush=True)
                return tally
            elif status == "INVALID_SAT":
                tally["invalid"] += 1
            else:
                tally["undecided"] += 1
            done = sum(tally[k] for k in ("refuted", "sat", "invalid", "undecided"))
            if done % 32 == 0 or done == tally["total"]:
                pending = tally["total"] - done
                print(f"PROGRESS done={done}/{tally['total']} "
                      f"refuted={tally['refuted']} sat={tally['sat']} "
                      f"undecided={tally['undecided']} pending={pending} "
                      f"elapsed={time.monotonic()-started:.1f}", flush=True)
    print("COMPLETE " + json.dumps(tally, sort_keys=True), flush=True)
    return tally


def stats():
    cnf, orbits, orb_id = instance(72)
    counts = [len({orb_id[b] for b in BALL[w]}) for w in range(N)]
    print(f"orbits={len(orbits)} sizes={sorted(set(map(len, orbits)))} "
          f"ball_quotient={sorted(set(counts))} clauses={len(cnf.clauses)}")
    print(f"fixed_orbit_words={orbits[0]}")
    print(f"integer_counting_lb={-(-len(orbits)//counts[0])}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: cube_sigma.py stats|single|generate|run ...")
    command = sys.argv[1]
    if command == "stats":
        stats()
    elif command == "single":
        target, workdir = int(sys.argv[2]), sys.argv[3]
        timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 1200
        cnf, orbits, _ = instance(target)
        os.makedirs(workdir, exist_ok=True)
        write_cnf(cnf, os.path.join(workdir, "instance.cnf"))
        print(solve_one(os.path.join(workdir, "instance.cnf"), timeout, target, orbits))
    elif command == "generate":
        target, branch_count, outdir = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        print(make_cubes(target, branch_count, outdir))
    elif command == "run":
        run_cubes(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    else:
        raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    main()

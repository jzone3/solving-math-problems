#!/usr/bin/env python3
"""Cube-and-conquer driver: takes an iCNF cube file ("a <lits> 0" lines) from
march_cu, solves base CNF + each cube with kissat in parallel, with a per-cube
time limit. Reports per-cube status (SAT / UNSAT / TIMEOUT) so cube hardness
can be measured. Any SAT cube => coloring extracted and verified.
Usage: cnc_run.py <base.cnf> <cubes.icnf> <per_cube_seconds> <jobs> [max_cubes]
"""
import subprocess, sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

base_path, cube_path, tlim, jobs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
max_cubes = int(sys.argv[5]) if len(sys.argv) > 5 else None

with open(base_path) as f:
    header = f.readline().split()
    nv, nc = int(header[2]), int(header[3])
    base = f.read()

cubes = []
for line in open(cube_path):
    if line.startswith("a "):
        cubes.append([int(x) for x in line.split()[1:-1]])
if max_cubes:
    cubes = cubes[:max_cubes]
print(f"{len(cubes)} cubes, per-cube limit {tlim}s, {jobs} jobs", flush=True)

def solve(i):
    cube = cubes[i]
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        f.write(f"p cnf {nv} {nc + len(cube)}\n")
        f.write(base)
        for lit in cube:
            f.write(f"{lit} 0\n")
        path = f.name
    try:
        r = subprocess.run(["kissat", "-q", f"--time={tlim}", path],
                           capture_output=True, text=True)
        if r.returncode == 10:
            with open(f"cube_{i}_sat.out", "w") as o:
                o.write(r.stdout)
            return i, "SAT"
        if r.returncode == 20:
            return i, "UNSAT"
        return i, "TIMEOUT"
    finally:
        os.unlink(path)

stats = {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}
with ThreadPoolExecutor(max_workers=jobs) as ex:
    futs = [ex.submit(solve, i) for i in range(len(cubes))]
    for n, fut in enumerate(as_completed(futs), 1):
        i, st = fut.result()
        stats[st] += 1
        print(f"cube {i}: {st}   [{n}/{len(cubes)} done: {stats}]", flush=True)
        if st == "SAT":
            print("!!! SAT cube found — model in cube_%d_sat.out" % i, flush=True)
print("FINAL:", stats)

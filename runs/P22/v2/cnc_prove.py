#!/usr/bin/env python3
"""Cube-and-conquer with per-cube DRAT verification.
For each cube: solve base CNF + cube units with kissat (time limit); on
UNSAT, generate & check DRAT with drat-trim, record VERIFIED; on timeout,
record for recursion. Results appended to a status file (resumable).
Usage: cnc_prove.py <base.cnf> <cubes.icnf> <per_cube_seconds> <jobs> <status_file>
"""
import subprocess, sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

base_path, cube_path, tlim, jobs, status_path = (
    sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])

with open(base_path) as f:
    header = f.readline().split()
    nv, nc = int(header[2]), int(header[3])
    base = f.read()

cubes = []
for line in open(cube_path):
    if line.startswith("a "):
        cubes.append([int(x) for x in line.split()[1:-1]])

done = {}
if os.path.exists(status_path):
    for line in open(status_path):
        i, st = line.split()[:2]
        done[int(i)] = st
todo = [i for i in range(len(cubes)) if done.get(i) not in ("VERIFIED", "SAT")]
print(f"{len(cubes)} cubes, {len(todo)} to do, limit {tlim}s, {jobs} jobs", flush=True)

lock = __import__("threading").Lock()
out = open(status_path, "a")

def record(i, st):
    with lock:
        out.write(f"{i} {st}\n")
        out.flush()

def solve(i):
    cube = cubes[i]
    fd, path = tempfile.mkstemp(suffix=".cnf"); os.close(fd)
    drat = path + ".drat"
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {nc + len(cube)}\n")
        f.write(base)
        for lit in cube:
            f.write(f"{lit} 0\n")
    try:
        r = subprocess.run(["kissat", "-q", f"--time={tlim}", path, drat],
                           capture_output=True, text=True)
        if r.returncode == 10:
            with open(f"cube_{i}_sat.out", "w") as o:
                o.write(r.stdout)
            record(i, "SAT")
            return i, "SAT"
        if r.returncode == 20:
            v = subprocess.run(["drat-trim", path, drat],
                               capture_output=True, text=True)
            st = "VERIFIED" if "s VERIFIED" in v.stdout else "UNSAT_UNVERIFIED"
            record(i, st)
            return i, st
        record(i, "TIMEOUT")
        return i, "TIMEOUT"
    finally:
        for q in (path, drat):
            if os.path.exists(q):
                os.unlink(q)

stats = {}
with ThreadPoolExecutor(max_workers=jobs) as ex:
    futs = [ex.submit(solve, i) for i in todo]
    for n, fut in enumerate(as_completed(futs), 1):
        i, st = fut.result()
        stats[st] = stats.get(st, 0) + 1
        if n % 50 == 0 or st in ("SAT", "UNSAT_UNVERIFIED"):
            print(f"[{n}/{len(todo)}] {stats}", flush=True)
print("FINAL:", stats)

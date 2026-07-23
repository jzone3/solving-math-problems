#!/usr/bin/env python3
"""Hardness-scaling experiment: fix the colors of the first k star edges of
vertex 0 (random values, avoiding immediate empty clauses), run kissat with a
time limit, record solve time / status. Measures how deep a star-edge cube
must be before the residual instance becomes tractable.
Usage: scaling.py <k> <trials> <tlim>
"""
import random, subprocess, sys, tempfile, os, time

k, trials, tlim = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
with open("plain.cnf") as f:
    header = f.readline().split()
    nv, nc = int(header[2]), int(header[3])
    base = f.read()

random.seed(k * 1000 + 7)
for t in range(trials):
    # plain.cnf already fixes var 1 = True; cube over star vars 2..k+1
    units = [(i + 2) if random.random() < 0.5 else -(i + 2) for i in range(k)]
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        f.write(f"p cnf {nv} {nc + len(units)}\n")
        f.write(base)
        for u in units:
            f.write(f"{u} 0\n")
        path = f.name
    t0 = time.time()
    r = subprocess.run(["kissat", "-q", f"--time={tlim}", path], capture_output=True)
    dt = time.time() - t0
    os.unlink(path)
    st = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "TIMEOUT")
    print(f"k={k} trial={t}: {st} {dt:.1f}s", flush=True)

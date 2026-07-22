#!/usr/bin/env python3
"""Sweep prescribed cyclic automorphism types for open PMD instances.

For each (v,k) and each cycle type sigma = c cycles of length n + f fixed
points (n*c+f=v, n>=2), run pmd_dlx with a timeout; log outcome:
  SAT (witness found), UNSAT-exhausted (no design with that automorphism),
  or TIMEOUT. Results appended to sweep_results.tsv.
"""
import subprocess, sys, time, os

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "pmd_dlx")
OUT = os.path.join(HERE, "sweep_results.tsv")

def types(v):
    out = []
    for n in range(v, 1, -1):
        for c in range(1, v // n + 1):
            f = v - n * c
            out.append((n, c, f))
    return out

def run(v, k, n, c, f, timeout):
    t0 = time.time()
    try:
        p = subprocess.run([BIN, str(v), str(k), str(n), str(c), str(f), "1"],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None, time.time() - t0
    el = time.time() - t0
    sols = 0
    for line in p.stdout.splitlines():
        if line.startswith("SOLUTIONS"):
            sols = int(line.split()[1])
    if sols > 0:
        wfile = os.path.join(HERE, f"witness_{v}_{k}_{n}_{c}_{f}.txt")
        with open(wfile, "w") as fh:
            grab = False
            for line in p.stdout.splitlines():
                if line == "SOLUTION BEGIN": grab = True; continue
                if line == "SOLUTION END": break
                if grab: fh.write(line + "\n")
        return "SAT", wfile, el
    return "UNSAT-exhausted", None, el

def main():
    instances = [(int(a.split(",")[0]), int(a.split(",")[1])) for a in sys.argv[1].split()]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    with open(OUT, "a") as log:
        for v, k in instances:
            for n, c, f in types(v):
                status, wfile, el = run(v, k, n, c, f, timeout)
                line = f"{v}\t{k}\t{n}\t{c}\t{f}\t{status}\t{el:.1f}\t{wfile or ''}"
                print(line, flush=True)
                log.write(line + "\n"); log.flush()
                if status == "SAT":
                    print(f"*** WITNESS FOUND for ({v},{k})-PMD: {wfile}", flush=True)

if __name__ == "__main__":
    main()

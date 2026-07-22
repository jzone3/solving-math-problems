#!/usr/bin/env python3
"""Direct full-N covering SAT via DIMACS + kissat binary (stronger than pysat solvers).

Same encoding as cover_sat.py: vars x[n][a] for divisors n >= m of N;
at-most-one per modulus (pairwise <=10, sequential-ladder otherwise);
coverage clause per t in Z_N; translation symmetry break on smallest modulus.
"""
import json, subprocess, sys, time

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


def build_dimacs(N, m, path):
    mods = [d for d in divisors(N) if d >= m and d > 1]
    nv = 0
    x = {}
    for n in mods:
        x[n] = list(range(nv + 1, nv + 1 + n))
        nv += n
    clauses = []
    for n in mods:
        v = x[n]
        if n <= 10:
            for i in range(n):
                for j in range(i + 1, n):
                    clauses.append((-v[i], -v[j]))
        else:  # sequential AMO with auxiliary s_i
            s = list(range(nv + 1, nv + n))
            nv += n - 1
            clauses.append((-v[0], s[0]))
            for i in range(1, n - 1):
                clauses.append((-v[i], s[i]))
                clauses.append((-s[i - 1], s[i]))
                clauses.append((-v[i], -s[i - 1]))
            clauses.append((-v[n - 1], -s[n - 2]))
    d1 = mods[0]
    for a in range(1, d1):
        clauses.append((-x[d1][a],))
    ncl = len(clauses) + N
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {ncl}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
        for t in range(N):
            f.write(" ".join(str(x[n][t % n]) for n in mods) + " 0\n")
    return mods, x


def run(N, m, timeout=3600, out=None):
    cnf = f"/tmp/cover_{N}_{m}.cnf"
    t0 = time.time()
    mods, x = build_dimacs(N, m, cnf)
    print(f"N={N} m={m} mods={len(mods)} built {time.time()-t0:.1f}s", flush=True)
    p = subprocess.run([KISSAT, "-q", f"--time={int(timeout)}", cnf],
                       capture_output=True, text=True)
    dt = time.time() - t0
    if "s SATISFIABLE" in p.stdout:
        assign = set()
        for line in p.stdout.splitlines():
            if line.startswith("v "):
                for tok in line[2:].split():
                    l = int(tok)
                    if l > 0:
                        assign.add(l)
        sol = [(a, n) for n in mods for a in range(n) if x[n][a] in assign]
        cov = bytearray(N)
        for a, n in sol:
            for t in range(a, N, n):
                cov[t] = 1
        assert all(cov), "cover check failed"
        print(f"STATUS SAT({dt:.0f}s) size={len(sol)}", flush=True)
        if out:
            json.dump({"N": N, "m": m, "cover": sol}, open(out, "w"))
        return True
    elif "s UNSATISFIABLE" in p.stdout:
        print(f"STATUS UNSAT({dt:.0f}s)", flush=True)
        return False
    else:
        print(f"STATUS TIMEOUT({dt:.0f}s)", flush=True)
        return None


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 3600
    out = sys.argv[4] if len(sys.argv) > 4 else None
    run(N, m, timeout, out)

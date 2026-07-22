#!/usr/bin/env python3
"""Local-search (YalSAT) attack on direct full-N covering instances.
Discovery of this run: CDCL (kissat) stalls for hours on these instances, but
stochastic local search cracks them in seconds/minutes (m=5/N=1440: <8 s).

Usage: python3 ylocal.py N m timeout_s [out.json] [seed]
"""
import json, subprocess, sys, time
from collections import Counter

YALSAT = "/home/ubuntu/yalsat/yalsat"


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


def build(N, m, path, pairwise_max=64):
    mods = [d for d in divisors(N) if d >= m and d > 1]
    nv = 0
    x = {}
    for n in mods:
        x[n] = list(range(nv + 1, nv + 1 + n))
        nv += n
    lines = []
    for n in mods:
        v = x[n]
        if n <= pairwise_max:
            for i in range(n):
                for j in range(i + 1, n):
                    lines.append(f"-{v[i]} -{v[j]}")
        else:  # sequential counter
            s = list(range(nv + 1, nv + n))
            nv += n - 1
            lines.append(f"-{v[0]} {s[0]}")
            for i in range(1, n - 1):
                lines.append(f"-{v[i]} {s[i]}")
                lines.append(f"-{s[i-1]} {s[i]}")
                lines.append(f"-{v[i]} -{s[i-1]}")
            lines.append(f"-{v[n-1]} -{s[n-2]}")
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(lines) + N}\n")
        for l in lines:
            f.write(l + " 0\n")
        for t in range(N):
            f.write(" ".join(str(x[n][t % n]) for n in mods) + " 0\n")
    return mods, x


def run(N, m, timeout, out=None, seed=1234):
    cnf = f"/tmp/ycover_{N}_{m}.cnf"
    t0 = time.time()
    mods, x = build(N, m, cnf)
    print(f"N={N} m={m} mods={len(mods)} built {time.time()-t0:.1f}s", flush=True)
    p = subprocess.run(["timeout", str(int(timeout)), YALSAT,
                        cnf, str(seed)], capture_output=True, text=True)
    dt = time.time() - t0
    if "s SATISFIABLE" not in p.stdout:
        print(f"STATUS NOSOLUTION({dt:.0f}s)", flush=True)
        return None
    assign = set()
    for line in p.stdout.splitlines():
        if line.startswith("v "):
            for tok in line[2:].split():
                l = int(tok)
                if l > 0:
                    assign.add(l)
    sol = [(a, n) for n in mods for a in range(n) if x[n][a] in assign]
    dup = [n for n, c in Counter(n for _, n in sol).items() if c > 1]
    assert not dup, f"duplicate moduli {dup}"
    cov = bytearray(N)
    for a, n in sol:
        for t in range(a, N, n):
            cov[t] = 1
    assert all(cov), "not covered"
    print(f"STATUS SAT({dt:.0f}s) size={len(sol)}", flush=True)
    if out:
        json.dump({"m": m, "N": N, "cover": sol}, open(out, "w"))
    return sol


if __name__ == "__main__":
    N, m = int(sys.argv[1]), int(sys.argv[2])
    timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 3600
    out = sys.argv[4] if len(sys.argv) > 4 else None
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1234
    run(N, m, timeout, out, seed)

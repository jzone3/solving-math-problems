#!/usr/bin/env python3
"""Cube-and-conquer for direct covering instances.

Cubes: joint residue choices for a small set of 'scarce' moduli (the pure prime
powers of the dominant prime, which carry the most structural weight), with
translation symmetry canonicalized by fixing the smallest cube modulus residue 0
in the first orbit of cubes only where valid. Each cube is a unit-clause
assumption set appended to the base CNF and solved by kissat independently.

Usage: cube_conquer.py N m cube_mods(comma) time_per_cube parallel [out.json]
"""
import itertools, json, multiprocessing, os, subprocess, sys, time

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


def build_base(N, m, path):
    mods = [d for d in divisors(N) if d >= m and d > 1]
    nv = 0
    x = {}
    for n in mods:
        x[n] = list(range(nv + 1, nv + 1 + n))
        nv += n
    lines = []
    for n in mods:
        v = x[n]
        if n <= 64:
            for i in range(n):
                for j in range(i + 1, n):
                    lines.append(f"-{v[i]} -{v[j]}")
        else:
            s = list(range(nv + 1, nv + n))
            nv += n - 1
            lines.append(f"-{v[0]} {s[0]}")
            for i in range(1, n - 1):
                lines.append(f"-{v[i]} {s[i]}")
                lines.append(f"-{s[i-1]} {s[i]}")
                lines.append(f"-{v[i]} -{s[i-1]}")
            lines.append(f"-{v[n-1]} -{s[n-2]}")
    for t in range(N):
        lines.append(" ".join(str(x[n][t % n]) for n in mods))
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(lines)}\n")
        for l in lines:
            f.write(l + " 0\n")
    return mods, x, nv, len(lines)


def solve_cube(args):
    base, nv, ncl, units, tlim, tag = args
    path = f"/tmp/cube_{tag}.cnf"
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {ncl + len(units)}\n")
        with open(base) as b:
            b.readline()
            for line in b:
                f.write(line)
        for u in units:
            f.write(f"{u} 0\n")
    p = subprocess.run([KISSAT, "-q", f"--time={int(tlim)}", path],
                       capture_output=True, text=True)
    os.unlink(path)
    if "s SATISFIABLE" in p.stdout:
        assign = set()
        for line in p.stdout.splitlines():
            if line.startswith("v "):
                for tok in line[2:].split():
                    l = int(tok)
                    if l > 0:
                        assign.add(l)
        return ("SAT", tag, assign)
    if "s UNSATISFIABLE" in p.stdout:
        return ("UNSAT", tag, None)
    return ("TIMEOUT", tag, None)


def main():
    N, m = int(sys.argv[1]), int(sys.argv[2])
    cube_mods = [int(v) for v in sys.argv[3].split(",")]
    tlim = float(sys.argv[4])
    par = int(sys.argv[5])
    out = sys.argv[6] if len(sys.argv) > 6 else None
    base = f"/tmp/cc_base_{N}_{m}.cnf"
    t0 = time.time()
    mods, x, nv, ncl = build_base(N, m, base)
    print(f"N={N} m={m} mods={len(mods)} base built {time.time()-t0:.1f}s", flush=True)
    # cubes: each cube modulus takes a specific residue (translation symmetry:
    # residue of the smallest cube modulus fixed to 0..g-1 where g minimal orbit)
    c0 = cube_mods[0]
    cubes = []
    for r0 in range(1):  # translation: WLOG smallest cube modulus has residue 0
        for rest in itertools.product(*[range(n) for n in cube_mods[1:]]):
            units = [x[c0][r0]] + [x[n][r] for n, r in zip(cube_mods[1:], rest)]
            cubes.append(units)
    print(f"{len(cubes)} cubes (mods {cube_mods}), {par} workers, "
          f"{tlim:.0f}s each", flush=True)
    jobs = [(base, nv, ncl, u, tlim, i) for i, u in enumerate(cubes)]
    stats = {"UNSAT": 0, "TIMEOUT": 0}
    with multiprocessing.Pool(par) as pool:
        for res, tag, assign in pool.imap_unordered(solve_cube, jobs):
            if res == "SAT":
                sol = [(a, n) for n in mods for a in range(n)
                       if x[n][a] in assign]
                cov = bytearray(N)
                ms = [n for _, n in sol]
                assert len(ms) == len(set(ms)) and min(ms) >= m
                for a, n in sol:
                    for t in range(a, N, n):
                        cov[t] = 1
                assert all(cov)
                print(f"SAT cube {tag}! size={len(sol)} "
                      f"t={time.time()-t0:.0f}s", flush=True)
                if out:
                    json.dump({"m": m, "N": N, "cover": sol}, open(out, "w"))
                pool.terminate()
                return
            stats[res] += 1
            if (stats["UNSAT"] + stats["TIMEOUT"]) % 8 == 0:
                print(f"  progress {stats} t={time.time()-t0:.0f}s", flush=True)
    print(f"DONE no SAT: {stats} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run HiGHS orbit feasibility for explicit classes.

Usage: orbit_ilp_feas.py TARGET TIME_LIMIT THREADS "lam" "assign" OUTDIR
"""
import ast
import os
import sys
import time
import highspy
import numpy as np

N = 729
S3 = {"id": (0, 1, 2), "tau": (1, 0, 2), "sigma": (1, 2, 0)}


def digits(w):
    return [(w // 3**i) % 3 for i in range(6)]


def undig(d):
    return sum(v * 3**i for i, v in enumerate(d))


BALL = []
for w in range(N):
    d = digits(w)
    b = [w]
    for i in range(6):
        for v in (1, 2):
            e = d[:]
            e[i] = (e[i] + v) % 3
            b.append(undig(e))
    BALL.append(b)


def build_g(cycles):
    perm = [0] * 6
    smap = [S3["id"]] * 6
    pos = 0
    for length, symbol in cycles:
        idxs = list(range(pos, pos + length))
        for k, i in enumerate(idxs):
            perm[i] = idxs[(k + 1) % length]
        smap[idxs[-1]] = S3[symbol]
        pos += length
    return perm, smap


def apply_g(perm, smap, w):
    d = digits(w)
    e = [0] * 6
    for i in range(6):
        e[perm[i]] = smap[i][d[i]]
    return undig(e)


def orbits_of(perm, smap):
    seen = [False] * N
    orbits = []
    orb_id = [0] * N
    for w in range(N):
        if seen[w]:
            continue
        orbit = []
        x = w
        while not seen[x]:
            seen[x] = True
            orb_id[x] = len(orbits)
            orbit.append(x)
            x = apply_g(perm, smap, x)
        orbits.append(orbit)
    return orbits, orb_id


def main():
    target, limit, threads = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    lam, assign = ast.literal_eval(sys.argv[4]), ast.literal_eval(sys.argv[5])
    if isinstance(assign, str):
        assign = (assign,)
    outdir = sys.argv[6]
    os.makedirs(outdir, exist_ok=True)
    orbits, orb_id = orbits_of(*build_g(list(zip(lam, assign))))
    m = len(orbits)
    sizes = np.array([float(len(o)) for o in orbits])
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", limit)
    h.setOptionValue("threads", threads)
    inf = highspy.kHighsInf
    h.addVars(m, np.zeros(m), np.ones(m))
    h.changeColsIntegrality(m, np.arange(m, dtype=np.int32),
                             np.full(m, highspy.HighsVarType.kInteger))
    for w in range(N):
        cols = sorted({orb_id[b] for b in BALL[w]})
        h.addRow(1.0, inf, len(cols), np.array(cols, dtype=np.int32),
                 np.ones(len(cols)))
    h.addRow(-inf, float(target), m, np.arange(m, dtype=np.int32), sizes)
    start = time.monotonic()
    h.run()
    elapsed = time.monotonic() - start
    st = h.getModelStatus()
    if st == highspy.HighsModelStatus.kOptimal:
        sol = np.array(h.getSolution().col_value)
        chosen = [w for j in np.where(sol > 0.5)[0] for w in orbits[int(j)]]
        code_path = os.path.join(outdir, "code.txt")
        with open(code_path, "w") as f:
            for w in sorted(chosen):
                f.write("".join(map(str, digits(w))) + "\n")
        status = f"FEASIBLE size={len(chosen)}"
    elif st == highspy.HighsModelStatus.kInfeasible:
        status = "INFEASIBLE"
    else:
        status = f"UNDECIDED status={st}"
    line = (f"{status} lam={lam} assign={assign} orbits={m} "
            f"seconds={elapsed:.3f}")
    print(line, flush=True)
    with open(os.path.join(outdir, "result.txt"), "w") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    main()

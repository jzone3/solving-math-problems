#!/usr/bin/env python3
"""Cube-and-conquer for the CW(120,49) multiplier-orbit decision CNF.

Cubes = assignments of the first CUBE_DEPTH orbit ternary variables (ordered by
orbit size descending). Each cube adds unit clauses to the base CNF; kissat
solves each with a time budget; timed-out cubes are split one level deeper.
All cubes UNSAT => no CW(120,49) exists. Any SAT cube => witness.
"""
import os
import subprocess
import sys
import multiprocessing as mp

sys.path.insert(0, ".")
sys.path.insert(0, "../../../solutions/P11")
from icw_enum import orbits_of
from verify import check, is_proper

KISSAT = "/home/ubuntu/kissat/build/kissat"
BASE = "/home/ubuntu/orbit120.cnf"  # built by orbit120_kissat.py encoder
n, k = 120, 49
orbs = orbits_of(7, n)
sizes = [len(o) for o in orbs]
no = len(orbs)
order = sorted(range(no), key=lambda i: -sizes[i])

# Variable ids: reconstruct the same IDPool order used in orbit120_kissat.py.
# pos_i = pool.id(("pos", i)); ternary() called for i in range(no) after TRUE?
# In orbit120_kissat: Builder(), tv = [ternary(b,i) ...] FIRST, so
# pos_0=1, neg_0=2, pos_1=3, neg_1=4, ... pos_i=2i+1, neg_i=2i+2.
POS = lambda i: 2 * i + 1
NEG = lambda i: 2 * i + 2

with open(BASE) as f:
    header = f.readline().split()
NV, NC = int(header[2]), int(header[3])


def cube_units(assign):
    """assign: list of (orbit_index, value)."""
    units = []
    for i, v in assign:
        if v == 0:
            units += [[-POS(i)], [-NEG(i)]]
        elif v == 1:
            units += [[POS(i)], [-NEG(i)]]
        else:
            units += [[-POS(i)], [NEG(i)]]
    return units


def weight_feasible(assign):
    w = sum(sizes[i] for i, v in assign if v != 0)
    if w > k:
        return False
    rem = sum(sizes[i] for i in order if i not in [a for a, _ in assign])
    return w + rem >= k


def run_cube(args):
    assign, budget = args
    units = cube_units(assign)
    path = f"/tmp/cube_{os.getpid()}.cnf"
    with open(path, "w") as f:
        f.write(f"p cnf {NV} {NC + len(units)}\n")
        with open(BASE) as base:
            base.readline()
            for line in base:
                f.write(line)
        for u in units:
            f.write(" ".join(map(str, u)) + " 0\n")
    r = subprocess.run(["timeout", str(budget), KISSAT, "-q", path],
                       capture_output=True, text=True)
    out = r.stdout
    if "s SATISFIABLE" in out:
        return ("SAT", assign, out)
    if "s UNSATISFIABLE" in out:
        return ("UNSAT", assign, None)
    return ("UNKNOWN", assign, None)


def expand(assign, depth_orbit):
    return [assign + [(depth_orbit, v)] for v in (0, 1, -1)]


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    depth0 = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    frontier = [[]]
    for d in range(depth0):
        frontier = [a2 for a in frontier for a2 in expand(a, order[d])
                    if weight_feasible(a2)]
    print(f"initial cubes: {len(frontier)} (depth {depth0})", flush=True)
    level = depth0
    stats = {"UNSAT": 0, "UNKNOWN": 0}
    with mp.Pool(7) as pool:
        while frontier:
            results = pool.imap_unordered(
                run_cube, [(a, budget) for a in frontier], chunksize=1)
            nxt = []
            done = 0
            for res, assign, out in results:
                done += 1
                if res == "SAT":
                    print("SAT CUBE FOUND:", assign, flush=True)
                    model = set()
                    for line in out.splitlines():
                        if line.startswith("v "):
                            for tok in line[2:].split():
                                t = int(tok)
                                if t > 0:
                                    model.add(t)
                    a = [0] * n
                    for i, o in enumerate(orbs):
                        v = 1 if POS(i) in model else (-1 if NEG(i) in model else 0)
                        for x in o:
                            a[x] = v
                    P = [i for i, x in enumerate(a) if x == 1]
                    N = [i for i, x in enumerate(a) if x == -1]
                    check(n, k, P, N, proper=False)
                    print("VERIFIED CW(120,49)! proper =", is_proper(n, P, N))
                    print("P =", P, "\nN =", N, flush=True)
                    sys.exit(0)
                stats[res] = stats.get(res, 0) + 1
                if res == "UNKNOWN":
                    if level < no:
                        nxt.extend(a2 for a2 in expand(assign, order[level])
                                   if weight_feasible(a2))
                    else:
                        print("cube exhausted depth, still UNKNOWN:", assign)
                if done % 50 == 0:
                    print(f"  level {level}: {done}/{len(frontier)} done, "
                          f"stats {stats}", flush=True)
            print(f"level {level} complete: {len(frontier)} cubes, "
                  f"stats {stats}; next frontier {len(nxt)}", flush=True)
            frontier = nxt
            level += 1
            budget = int(budget * 1.5)
    print("ALL CUBES UNSAT => no CW(120,49) exists.", flush=True)

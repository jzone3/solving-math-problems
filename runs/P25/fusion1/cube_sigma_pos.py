#!/usr/bin/env python3
"""Positive-branching cube-and-conquer for the sigma^6 quotient."""
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
H_WORDS = (0, 364, 728)


def add_word(x, y):
    a, b = digits(x), digits(y)
    return sum(((u + v) % 3) * 3**i for i, (u, v) in enumerate(zip(a, b)))


def setup(budget):
    perm, smap = build_g(list(zip(LAM, ASSIGN)))
    orbits, orb_id = orbits_of(perm, smap)
    reps = [orbit[0] for orbit in orbits]
    quotient_ball = []
    for w in reps:
        quotient_ball.append(tuple(sorted({orb_id[b] for b in BALL[w]})))
    cnf = CNF()
    cnf.nv = len(orbits)
    for cols in quotient_ball:
        cnf.add(*[j + 1 for j in cols])
    totalizer_atmost(cnf, list(range(1, len(orbits) + 1)), budget)
    cnf.add(1)
    return orbits, orb_id, quotient_ball, cnf


def group_maps(orbits, orb_id):
    """Maps on quotient IDs from H translations and all coordinate permutations."""
    maps = []
    for c in H_WORDS:
        for p in itertools.permutations(range(6)):
            mapping = []
            for orbit in orbits:
                w = orbit[0]
                d = digits(w)
                e = [0] * 6
                for i, j in enumerate(p):
                    e[j] = d[i]
                y = sum(v * 3**i for i, v in enumerate(e))
                mapping.append(orb_id[add_word(y, c)])
            maps.append(tuple(mapping))
    return maps


def canonical_child(parent, child, maps):
    """Canonicalize children under maps stabilizing the parent's chosen set."""
    pset = frozenset(parent)
    stabilizer = [m for m in maps if frozenset(m[j] for j in pset) == pset]
    best = None
    for m in stabilizer:
        image = tuple(sorted(m[j] for j in child))
        if best is None or image < best:
            best = image
    return best


def build_tree(budget, depth, outdir):
    orbits, orb_id, qball, cnf = setup(budget)
    maps = group_maps(orbits, orb_id)
    root = (0,)
    nodes = [(root, 0)]
    stats = {
        "budget": budget, "depth": depth, "group_maps": len(maps),
        "nodes": 0, "pruned_cardinality": 0, "pruned_bound": 0,
        "deduped_symmetry": 0, "leaves_covered": 0, "cubes": 0,
    }
    cubes = []
    while nodes:
        chosen, level = nodes.pop()
        stats["nodes"] += 1
        chosen_set = set(chosen)
        covered = set()
        for j in chosen_set:
            covered.update(qball[j])
        uncovered = set(range(len(qball))) - covered
        if not uncovered:
            stats["leaves_covered"] += 1
            cubes.append(chosen)
            continue
        if level >= depth:
            cubes.append(chosen)
            continue
        if len(chosen) > budget:
            stats["pruned_cardinality"] += 1
            continue
        if len(uncovered) > 13 * (budget - len(chosen)):
            stats["pruned_bound"] += 1
            continue
        p = min(uncovered, key=lambda x: (len([j for j in qball[x] if j not in chosen_set]), x))
        candidates = [j for j in qball[p] if j not in chosen_set]
        seen_children = set()
        for j in candidates:
            child = tuple(sorted((*chosen, j)))
            key = canonical_child(chosen, child, maps)
            if key in seen_children:
                stats["deduped_symmetry"] += 1
                continue
            seen_children.add(key)
            nodes.append((child, level + 1))
    os.makedirs(outdir, exist_ok=True)
    for i, chosen in enumerate(cubes):
        path = os.path.join(outdir, f"cube_{i:05d}.cnf")
        with open(path, "w") as f:
            f.write(f"p cnf {cnf.nv} {len(cnf.clauses) + len(chosen)}\n")
            for clause in cnf.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
            for j in chosen:
                f.write(f"{j + 1} 0\n")
    stats["cubes"] = len(cubes)
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump({"budget": budget, "depth": depth, "orbits": len(orbits),
                   "stats": stats}, f, indent=2)
    return stats, len(cubes), orbits


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


def solve_one(path, timeout, orbits):
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
    size = None
    verify_rc = None
    if status == "SAT":
        model = parse_model(output)
        chosen = [w for j, orbit in enumerate(orbits, 1)
                  if j in model for w in orbit]
        code = os.path.join(os.path.dirname(path), os.path.basename(path) + ".code")
        with open(code, "w") as f:
            for w in sorted(chosen):
                f.write("".join(map(str, digits(w))) + "\n")
        verify = subprocess.run(
            [sys.executable, "/home/ubuntu/repos/solving-math-problems/runs/P25/v1/verify.py",
             code], text=True, capture_output=True)
        size, verify_rc = len(chosen), verify.returncode
        if verify_rc != 0:
            status = "INVALID_SAT"
    return status, elapsed, size, verify_rc


def run_cubes(cubedir, workers, timeout):
    with open(os.path.join(cubedir, "metadata.json")) as f:
        metadata = json.load(f)
    perm, smap = build_g(list(zip(LAM, ASSIGN)))
    orbits, _ = orbits_of(perm, smap)
    paths = sorted(os.path.join(cubedir, x) for x in os.listdir(cubedir)
                   if x.endswith(".cnf"))
    tally = {"total": len(paths), "refuted": 0, "sat": 0,
             "invalid": 0, "undecided": 0}
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(solve_one, p, timeout, orbits): p for p in paths}
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
            if done % 16 == 0 or done == tally["total"]:
                print("PROGRESS " + json.dumps({
                    **tally, "done": done, "pending": tally["total"] - done,
                    "elapsed": round(time.monotonic() - started, 1)}, sort_keys=True),
                      flush=True)
    print("COMPLETE " + json.dumps(tally, sort_keys=True), flush=True)
    return tally


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: cube_sigma_pos.py tree|run ...")
    if sys.argv[1] == "tree":
        budget, depth, outdir = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        print(json.dumps(build_tree(budget, depth, outdir)[:2], sort_keys=True))
    elif sys.argv[1] == "run":
        run_cubes(sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    else:
        raise SystemExit("unknown command")


if __name__ == "__main__":
    main()

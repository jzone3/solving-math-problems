"""Exact radius/asymmetry refinement for a scanned translation."""
import os
import pickle
import subprocess
import time
from fractions import Fraction

from build_pool import build_universe_generic
from rotations import in_field_rotations
from sat import KISSAT, color_cnf, write_cnf

ROT = os.environ.get("ROT", "w[15]")
IDENT = os.environ["ID"]
RA = float(os.environ["RA"])
RB = float(os.environ["RB"])
LAYERS = int(os.environ.get("LAYERS", "3"))
TIME = int(os.environ.get("TIME", "300"))
RESULTS = os.environ.get("RESULTS", os.path.join(
    os.path.dirname(__file__), "results.tsv"))


def source_translation():
    with open(RESULTS) as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 3 and fields[0] == ROT and fields[1] == IDENT:
                return eval(fields[2], {"Fraction": Fraction}), fields[8]
    raise KeyError(IDENT)


def decide(points, edges):
    nv, clauses = color_cnf(len(points), edges, 4)
    cnf = f"/tmp/p23_refine_{os.getpid()}.cnf"
    write_cnf(cnf, nv, clauses)
    start = time.time()
    try:
        proc = subprocess.run([KISSAT, f"--time={TIME}", cnf],
                              capture_output=True, text=True)
    finally:
        os.unlink(cnf)
    elapsed = time.time() - start
    status = ("UNSAT" if "s UNSATISFIABLE" in proc.stdout else
              "SAT" if "s SATISFIABLE" in proc.stdout else "timeout")
    return status, elapsed


def main():
    field, omega = in_field_rotations()[ROT]
    translation, cross = source_translation()
    start = time.time()
    points, edges = build_universe_generic(
        (field, omega), translation, RA, RB, LAYERS)
    status, seconds = decide(points, edges)
    with open(RESULTS, "a") as f:
        f.write(f"{ROT}\t{IDENT}\t{translation}\t{LAYERS}\t{RA}\t{RB}\t"
                f"{len(points)}\t{len(edges)}\t{cross}\t{status}\t"
                f"{seconds:.3f}\n")
    if status == "UNSAT":
        path = os.path.join(os.path.dirname(RESULTS),
                            f"tuniv_{IDENT}_{RA:g}_{RB:g}.pkl")
        with open(path, "wb") as f:
            pickle.dump({"primes": field.primes, "points": points,
                         "edges": edges}, f)
    print(f"{ROT} {IDENT} {RA:g}/{RB:g}: {len(points)} vtx "
          f"{len(edges)} edges -> {status} ({seconds:.1f}s; "
          f"total {time.time()-start:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

"""Find each rotation's symmetric T=0 obstruction floor."""
import os
import subprocess
import time

from build_pool import build_universe_generic
from rotations import in_field_rotations
from sat import color_cnf, write_cnf, KISSAT

LAYERS = int(os.environ.get("LAYERS", "3"))
TIME = int(os.environ.get("TIME", "600"))
RADII = [float(x) for x in os.environ.get(
    "RADII", "2.4,2.2,2.0,1.9,1.8").split(",")]
ROT = os.environ.get("ROT", "w[15]")
OUT = os.environ.get("RESULTS", os.path.join(os.path.dirname(__file__),
                                             "results.tsv"))


def decide(pts, edges):
    nv, clauses = color_cnf(len(pts), edges, 4)
    cnf = f"/tmp/p23_floor_{os.getpid()}.cnf"
    write_cnf(cnf, nv, clauses)
    try:
        t0 = time.time()
        p = subprocess.run([KISSAT, f"--time={TIME}", cnf],
                           capture_output=True, text=True)
        elapsed = time.time() - t0
    finally:
        os.unlink(cnf)
    status = ("UNSAT" if "s UNSATISFIABLE" in p.stdout else
              "SAT" if "s SATISFIABLE" in p.stdout else "timeout")
    return status, elapsed


def main():
    field, omega = in_field_rotations()[ROT]
    zero = (field.ZERO, field.ZERO)
    for radius in RADII:
        t0 = time.time()
        pts, edges = build_universe_generic(
            (field, omega), zero, radius, radius, LAYERS)
        status, seconds = decide(pts, edges)
        with open(OUT, "a") as f:
            f.write(f"{ROT}\tT0\tzero\t{LAYERS}\t{radius}\t{radius}\t"
                    f"{len(pts)}\t{len(edges)}\t0\t{status}\t{seconds:.3f}\n")
        print(f"{ROT} T=0 r={radius}: {len(pts)} vtx {len(edges)} e "
              f"-> {status} ({seconds:.1f}s, total {time.time()-t0:.1f}s)",
              flush=True)


if __name__ == "__main__":
    main()

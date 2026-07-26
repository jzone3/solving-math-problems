"""Phase-2 translation scan and symmetric-radius exact test."""
import hashlib
import os
import pickle
import random
import subprocess
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.spatial import cKDTree

import lattice
from build_pool import build_universe_generic, to_generic_field
from rotations import in_field_rotations
from sat import color_cnf, write_cnf, KISSAT

ROT = os.environ.get("ROT", "w[15]")
LAYERS = int(os.environ.get("LAYERS", "3"))
RAD = float(os.environ.get("RAD", "1.6"))
NSHIFT = int(os.environ.get("NSHIFT", "10000"))
TOP = int(os.environ.get("TOP", "15"))
TIME = int(os.environ.get("TIME", "300"))
OUT = os.environ.get("RESULTS", os.path.join(os.path.dirname(__file__),
                                             "results.tsv"))
SEED = int(os.environ.get("SEED", "1"))


def cmul(field, a, b):
    x, y = a
    u, v = b
    return (field.sub(field.mul(x, u), field.mul(y, v)),
            field.add(field.mul(x, v), field.mul(y, u)))


def csub(field, a, b):
    return (field.sub(a[0], b[0]), field.sub(a[1], b[1]))


def cneg(field, a):
    return (tuple(-x for x in a[0]), tuple(-x for x in a[1]))


def translation_id(field, t):
    raw = repr(t).encode()
    return hashlib.sha1(raw).hexdigest()[:12]


def main():
    field, omega = in_field_rotations()[ROT]
    A0 = lattice.build_base(LAYERS, RAD)
    A = [to_generic_field(p, field) for p in A0]
    B = [cmul(field, omega, p) for p in A]
    za = np.array([[field.to_float(x), field.to_float(y)] for x, y in A])
    zb = np.array([[field.to_float(x), field.to_float(y)] for x, y in B])
    ta, tb = cKDTree(za), cKDTree(zb)
    units = [to_generic_field(p, field) for p in lattice.UNIT]
    rng = random.Random(SEED)

    def count(t):
        shift = np.array([field.to_float(t[0]), field.to_float(t[1])])
        near = tb.query_ball_tree(ta, 1.0 + 1e-7)
        # Recompute with shifted coordinates; the KD tree is only a prefilter.
        shifted = zb + shift
        tree = cKDTree(shifted)
        return tree.count_neighbors(ta, 1.0 + 1e-7) - \
            tree.count_neighbors(ta, 1.0 - 1e-7)

    candidates = [(0, (field.ZERO, field.ZERO))]
    seen = {(0.0, 0.0)}
    for _ in range(NSHIFT):
        p = A[rng.randrange(len(A))]
        q = B[rng.randrange(len(B))]
        u = units[rng.randrange(len(units))]
        t = csub(field, csub(field, p, q), u)
        key = (round(field.to_float(t[0]), 9), round(field.to_float(t[1]), 9))
        if key in seen:
            continue
        seen.add(key)
        candidates.append((count(t), t))
    candidates.sort(key=lambda x: -x[0])
    for score, translation in candidates[:TOP + 1]:
        start = time.time()
        pts, edges = build_universe_generic(
            (field, omega), translation, RAD, RAD, LAYERS)
        nv, clauses = color_cnf(len(pts), edges, 4)
        cnf = f"/tmp/p23_{os.getpid()}.cnf"
        write_cnf(cnf, nv, clauses)
        try:
            proc = subprocess.run([KISSAT, f"--time={TIME}", cnf],
                                  capture_output=True, text=True)
        finally:
            os.unlink(cnf)
        status = ("UNSAT" if "s UNSATISFIABLE" in proc.stdout else
                  "SAT" if "s SATISFIABLE" in proc.stdout else "timeout")
        elapsed = time.time() - start
        ident = f"{ROT.replace('[','_').replace(']','')}_{translation_id(field, translation)}"
        with open(OUT, "a") as f:
            f.write(f"{ROT}\t{ident}\t{translation}\t{LAYERS}\t{RAD}\t{RAD}\t"
                    f"{len(pts)}\t{len(edges)}\t{score}\t{status}\t{elapsed:.3f}\n")
        print(f"{ROT} {ident}: {len(pts)} vtx {len(edges)} e "
              f"cross~{score} -> {status} ({elapsed:.1f}s)", flush=True)
        if status == "UNSAT":
            with open(os.path.join(os.path.dirname(OUT),
                                   f"tuniv_{ident}.pkl"), "wb") as f:
                pickle.dump({"primes": field.primes, "points": pts,
                             "edges": edges}, f)


if __name__ == "__main__":
    main()

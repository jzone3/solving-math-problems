"""Standalone exact verifier for a saved universe pickle."""
import pickle
import sys

import numpy as np

import mfield


def verify(path, primes=None):
    with open(path, "rb") as f:
        rec = pickle.load(f)
    if isinstance(rec, dict):
        points, claimed = rec["points"], rec["edges"]
        primes = tuple(rec["primes"]) if primes is None else primes
    else:
        points, claimed = rec
    field = mfield.MField(primes)
    z = np.array([complex(field.to_float(x), field.to_float(y))
                  for x, y in points])
    exact = set()
    for i in range(len(points)):
        near = np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]
        for k in near:
            j = i + 1 + int(k)
            dx = field.sub(points[i][0], points[j][0])
            dy = field.sub(points[i][1], points[j][1])
            if field.add(field.mul(dx, dx), field.mul(dy, dy)) == field.ONE:
                exact.add((i, j))
    claimed = {tuple(e) for e in claimed}
    if exact != claimed:
        raise AssertionError(f"edge mismatch: claimed {len(claimed)}, "
                             f"exact {len(exact)}")
    print(f"{len(points)} vertices, {len(exact)} exact edges: PASS")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: verify_universe.py PICKLE [PRIME ...]")
    extra = tuple(int(x) for x in sys.argv[2:])
    verify(sys.argv[1], extra or None)

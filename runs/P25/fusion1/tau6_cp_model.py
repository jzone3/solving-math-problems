#!/usr/bin/env python3
"""Prepare (but do not solve) the tau^6 quotient CP-SAT model."""
import json
import os
from ortools.sat.python import cp_model


def digits(w):
    return [(w // (3 ** i)) % 3 for i in range(6)]


def undig(ds):
    return sum(v * (3 ** i) for i, v in enumerate(ds))


def tau(w):
    return undig([1 - v if v < 2 else 2 for v in digits(w)])


def main():
    outdir = "logs/tau6_cp_model"
    os.makedirs(outdir, exist_ok=True)
    orbits = []
    orb_id = [-1] * 729
    for w in range(729):
        if orb_id[w] >= 0:
            continue
        v = tau(w)
        j = len(orbits)
        orbit = [w] if v == w else [w, v]
        for z in orbit:
            orb_id[z] = j
        orbits.append(orbit)
    fixed = [j for j, o in enumerate(orbits) if len(o) == 1]
    sizes = sorted(len(o) for o in orbits)
    assert len(orbits) == 365 and sizes.count(1) == 1 and sizes.count(2) == 364
    assert len(fixed) == 1 and orbits[fixed[0]] == [728]
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{j}") for j in range(len(orbits))]
    for w in range(729):
        cols = sorted({orb_id[b] for b in [w] + [
            w + (((digits(w)[i] + d) % 3) - digits(w)[i]) * (3 ** i)
            for i in range(6) for d in (1, 2)
        ]})
        model.Add(sum(x[j] for j in cols) >= 1)
    model.Add(sum(2 * x[j] for j, o in enumerate(orbits) if len(o) == 2) <= 72)
    model.Add(x[fixed[0]] == 0)
    path = os.path.join(outdir, "tau6.cp_model")
    model.ExportToFile(path)
    metadata = {
        "orbits": len(orbits), "fixed_orbit": fixed[0],
        "fixed_word": 728, "pair_orbits": 364,
        "even_72_bound_pair_limit": 36, "model": path,
    }
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()

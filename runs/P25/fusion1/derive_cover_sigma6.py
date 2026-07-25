#!/usr/bin/env python3
"""Recover a feasible 26-orbit sigma^6 cover and save its witness."""
import os
import sys
import time

import highspy
import numpy as np

from cube_sigma_pos import setup


def main():
    outdir = sys.argv[1]
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    os.makedirs(outdir, exist_ok=True)
    orbits, _, qball, _ = setup(26)
    m = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", limit)
    h.setOptionValue("threads", 8)
    h.addVars(m, np.zeros(m), np.ones(m))
    ids = np.arange(m, dtype=np.int32)
    h.changeColsIntegrality(m, ids,
                            np.full(m, highspy.HighsVarType.kInteger))
    h.changeColsCost(m, ids, np.zeros(m))
    inf = highspy.kHighsInf
    for cols in qball:
        cols = np.asarray(cols, dtype=np.int32)
        h.addRow(1, inf, len(cols), cols, np.ones(len(cols)))
    h.addRow(-inf, 26, m, ids, np.ones(m))
    h.changeColBounds(0, 1, 1)
    started = time.monotonic()
    h.run()
    elapsed = time.monotonic() - started
    status = h.getModelStatus()
    info = h.getInfo()
    line = (f"status={status} elapsed={elapsed:.3f} "
            f"objective={info.objective_function_value} "
            f"dual_bound={info.mip_dual_bound}")
    print(line, flush=True)
    with open(os.path.join(outdir, "result.txt"), "w") as f:
        f.write(line + "\n")
    if status in (highspy.HighsModelStatus.kOptimal,
                  highspy.HighsModelStatus.kTimeLimit):
        x = np.asarray(h.getSolution().col_value)
        chosen = np.where(x > 0.5)[0]
        if len(chosen) <= 26:
            with open(os.path.join(outdir, "chosen_orbits.txt"), "w") as f:
                for j in chosen:
                    f.write(f"{int(j)}\n")
            with open(os.path.join(outdir, "code.txt"), "w") as f:
                for w in sorted(w for j in chosen for w in orbits[int(j)]):
                    f.write("".join(map(str, __import__("cube_sigma_pos").digits(w))) + "\n")
            print(f"WITNESS orbits={len(chosen)} words={3*len(chosen)}", flush=True)


if __name__ == "__main__":
    main()

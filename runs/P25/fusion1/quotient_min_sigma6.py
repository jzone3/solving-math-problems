#!/usr/bin/env python3
"""Exact quotient minimization for the sigma^6 invariant class."""
import os
import sys
import time

import highspy
import numpy as np

from cube_sigma_pos import setup


def main():
    workdir = sys.argv[1] if len(sys.argv) > 1 else "logs/quotient_min_sigma6"
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 10800.0
    os.makedirs(workdir, exist_ok=True)
    orbits, _, quotient_ball, _ = setup(25)
    m = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", limit)
    h.setOptionValue("threads", 8)
    h.setOptionValue("mip_rel_gap", 0.0)
    h.setOptionValue("presolve", "on")
    h.addVars(m, np.zeros(m), np.ones(m))
    indices = np.arange(m, dtype=np.int32)
    h.changeColsIntegrality(
        m, indices, np.full(m, highspy.HighsVarType.kInteger))
    h.changeColsCost(m, indices, np.ones(m))
    inf = highspy.kHighsInf
    for cols in quotient_ball:
        cols = np.asarray(cols, dtype=np.int32)
        h.addRow(1.0, inf, len(cols), cols, np.ones(len(cols)))
    h.changeColBounds(0, 1.0, 1.0)
    started = time.monotonic()
    h.run()
    elapsed = time.monotonic() - started
    status = h.getModelStatus()
    info = h.getInfo()
    objective = info.objective_function_value
    dual = info.mip_dual_bound
    print(
        f"RESULT status={status} elapsed={elapsed:.3f} vars={m} "
        f"constraints={len(quotient_ball)} objective={objective} "
        f"dual_bound={dual}",
        flush=True,
    )
    with open(os.path.join(workdir, "result.txt"), "w") as f:
        f.write(f"status={status}\n")
        f.write(f"elapsed={elapsed:.3f}\n")
        f.write(f"objective={objective}\n")
        f.write(f"dual_bound={dual}\n")
    if status == highspy.HighsModelStatus.kOptimal:
        solution = np.asarray(h.getSolution().col_value)
        chosen = np.where(solution > 0.5)[0]
        with open(os.path.join(workdir, "chosen_orbits.txt"), "w") as f:
            for j in chosen:
                f.write(f"{int(j)}\n")
        print(f"OPTIMAL_ORBITS count={len(chosen)}", flush=True)


if __name__ == "__main__":
    main()

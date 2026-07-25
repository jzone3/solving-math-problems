#!/usr/bin/env python3
"""Long HiGHS feasibility attempt for sigma^6 at a 24-orbit bound."""
import os
import sys
import time

import highspy
import numpy as np

from cube_sigma_pos import setup


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "logs/quotient_feas_sigma6"
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 28800.0
    os.makedirs(outdir, exist_ok=True)
    orbits, _, qball, _ = setup(24)
    m = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", limit)
    h.setOptionValue("threads", 2)
    h.setOptionValue("mip_rel_gap", 0.0)
    h.addVars(m, np.zeros(m), np.ones(m))
    ids = np.arange(m, dtype=np.int32)
    h.changeColsIntegrality(m, ids,
                            np.full(m, highspy.HighsVarType.kInteger))
    h.changeColsCost(m, ids, np.zeros(m))
    inf = highspy.kHighsInf
    for cols in qball:
        cols = np.asarray(cols, dtype=np.int32)
        h.addRow(1, inf, len(cols), cols, np.ones(len(cols)))
    h.addRow(-inf, 24, m, ids, np.ones(m))
    h.changeColBounds(0, 1, 1)
    started = time.monotonic()
    h.run()
    elapsed = time.monotonic() - started
    status = h.getModelStatus()
    info = h.getInfo()
    line = (f"status={status} elapsed={elapsed:.3f} objective="
            f"{info.objective_function_value} dual_bound={info.mip_dual_bound}")
    print(line, flush=True)
    with open(os.path.join(outdir, "result.txt"), "w") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    main()

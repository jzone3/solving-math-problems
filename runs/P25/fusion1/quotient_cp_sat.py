#!/usr/bin/env python3
"""CP-SAT feasibility solver for the sigma^6 quotient."""
import json
import os
import sys
import time

from ortools.sat.python import cp_model

from cube_sigma_pos import digits, setup


VERIFY = os.path.join(os.path.dirname(__file__), "..", "v1", "verify.py")


def solve(budget, workers, limit, outdir, second=None):
    os.makedirs(outdir, exist_ok=True)
    orbits, _, qball, _ = setup(budget)
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{j}") for j in range(len(orbits))]
    for cols in qball:
        model.Add(sum(x[j] for j in cols) >= 1)
    model.Add(sum(x) <= budget)
    model.Add(x[0] == 1)
    if second is not None:
        model.Add(x[second] == 1)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = False
    started = time.monotonic()
    status = solver.Solve(model)
    elapsed = time.monotonic() - started
    names = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }
    label = names.get(status, str(status))
    line = f"status={label} elapsed={elapsed:.3f} budget={budget} second={second}"
    print(line, flush=True)
    with open(os.path.join(outdir, "result.txt"), "w") as f:
        f.write(line + "\n")
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [j for j, v in enumerate(x) if solver.Value(v)]
        words = sorted(w for j in chosen for w in orbits[j])
        code = os.path.join(outdir, "code.txt")
        with open(code, "w") as f:
            for w in words:
                f.write("".join(map(str, digits(w))) + "\n")
        print(f"WITNESS orbits={len(chosen)} words={len(words)} code={code}", flush=True)
        print(f"VERIFY_COMMAND python3 {VERIFY} {code}", flush=True)
    with open(os.path.join(outdir, "metadata.json"), "w") as f:
        json.dump({"budget": budget, "second": second, "orbits": len(orbits),
                   "status": label, "elapsed": elapsed}, f, indent=2)
    return status


if __name__ == "__main__":
    # budget workers seconds outdir [representative]
    solve(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]),
          sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else None)

#!/usr/bin/env python3
"""CP-SAT minimization for the sigma^6 quotient."""
import os
import sys
import threading
import time

from ortools.sat.python import cp_model

from cube_sigma_pos import digits, setup


class Progress(cp_model.CpSolverSolutionCallback):
    def __init__(self, x, orbits, outdir):
        super().__init__()
        self.x = x
        self.orbits = orbits
        self.outdir = outdir
        self.last = 0.0
        self.best = None
        self.bound = 1.0

    def on_solution_callback(self):
        now = self.WallTime()
        obj = self.ObjectiveValue()
        bound = self.BestObjectiveBound()
        self.bound = bound
        if self.best is None or obj < self.best:
            self.best = obj
            chosen = [j for j, v in enumerate(self.x) if self.Value(v)]
            with open(os.path.join(self.outdir, "incumbent_orbits.txt"), "w") as f:
                for j in chosen:
                    f.write(f"{j}\n")
            with open(os.path.join(self.outdir, "incumbent_code.txt"), "w") as f:
                for w in sorted(w for j in chosen for w in self.orbits[j]):
                    f.write("".join(map(str, digits(w))) + "\n")
        if now - self.last >= 30.0 or self.best == obj:
            print(f"PROGRESS seconds={now:.3f} objective={obj:.6f} "
                  f"best_bound={bound:.6f}", flush=True)
            self.last = now


def heartbeat(callback, stop, started):
    while not stop.wait(300.0):
        best = "inf" if callback.best is None else f"{callback.best:.6f}"
        print(f"HEARTBEAT t={time.monotonic() - started:.3f} best={best} "
                f"bound={callback.bound:.6f}", flush=True)


def main():
    outdir = sys.argv[1]
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 43200.0
    hint_path = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(outdir, exist_ok=True)
    orbits, _, qball, _ = setup(26)
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{j}") for j in range(len(orbits))]
    for cols in qball:
        model.Add(sum(x[j] for j in cols) >= 1)
    model.Add(x[0] == 1)
    model.Minimize(sum(x))
    if hint_path and os.path.exists(hint_path):
        chosen = {int(s) for s in open(hint_path) if s.strip()}
        for j, v in enumerate(x):
            model.AddHint(v, 1 if j in chosen else 0)
        print(f"HINT orbits={len(chosen)}", flush=True)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_search_workers = 8
    solver.parameters.log_search_progress = True
    callback = Progress(x, orbits, outdir)
    started = time.monotonic()
    names = {
        cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE", cp_model.UNKNOWN: "UNKNOWN",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
    }
    stop = threading.Event()
    thread = threading.Thread(
        target=heartbeat, args=(callback, stop, started), daemon=True)
    thread.start()
    status = None
    error = None
    try:
        status = solver.solve(model, callback)
    except Exception as exc:
        error = repr(exc)
        print(f"EXCEPTION {error}", flush=True)
    finally:
        stop.set()
        thread.join(timeout=2.0)
        elapsed = time.monotonic() - started
        if status is not None:
            label = names.get(status, status)
            objective = solver.ObjectiveValue()
            bound = solver.BestObjectiveBound()
        else:
            label = "EXCEPTION"
            objective = callback.best if callback.best is not None else float("inf")
            bound = callback.bound
        line = (f"FINAL status={label} elapsed={elapsed:.3f} "
                f"best={objective:.6f} bound={bound:.6f}")
        print(line, flush=True)
        with open(os.path.join(outdir, "result.txt"), "w") as f:
            f.write(line + "\n")


if __name__ == "__main__":
    main()

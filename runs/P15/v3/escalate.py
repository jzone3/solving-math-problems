#!/usr/bin/env python3
"""Escalation driver: for each m try candidate lcms N (from screen.py) with a time
budget; stop at first SAT per m; log everything."""
import json, time
from cover_sat import solve, check

TARGETS = [
    (5, [360, 720, 2520]),
    (6, [840, 720, 2520, 5040]),
    (7, [2520, 5040, 10080]),
    (8, [2520, 5040, 10080]),
    (9, [5040, 10080, 27720]),
    (10, [10080, 9240, 27720]),
    (11, [27720, 55440]),
    (12, [30240, 27720, 55440]),
    (13, [55440, 110880]),
    (14, [55440, 110880]),
    (15, [166320, 110880]),
    (16, [277200, 166320]),
    (17, [332640, 277200]),
    (18, [360360, 332640]),
    (19, [720720]),
    (20, [720720]),
]

if __name__ == "__main__":
    log = open("escalate.log", "a")
    for m, Ns in TARGETS:
        for N in Ns:
            t0 = time.time()
            budget = 900.0
            status, sol = solve(N, m, timeout=budget)
            line = f"m={m} N={N} status={status} wall={time.time()-t0:.0f}s"
            if sol:
                assert check(sol, N)
                line += f" size={len(sol)}"
                with open(f"cover_m{m}_N{N}.json", "w") as f:
                    json.dump({"N": N, "m": m, "cover": sol}, f)
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()
            if sol:
                break

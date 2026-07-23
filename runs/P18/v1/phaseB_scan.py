#!/usr/bin/env python3
"""
Exhaustive (full-branching) phase-B scan: for small smooth N, decide whether
Z/N can be covered with distinct moduli from (M \ {2}) cap divisors(N),
M = {m : 2m+1 prime}. "exhausted" here IS a definitive negative for the pool
(unlike the branch-capped big runs). Success -> witness json in m-space.
"""
import json
import sys
import time
from fractions import Fraction

from twophase import is_prime, divisors, m_admissible, search


def main():
    tl = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    Ns = [int(a) for a in sys.argv[2:]] or [
        360, 720, 1080, 1440, 2160, 2520, 3600, 4320, 5040, 7560, 10080,
        15120, 20160, 25200, 27720, 30240, 45360, 55440]
    for N in Ns:
        mods = m_admissible(N, banned=(2,))
        mass = sum(Fraction(1, d) for d in mods)
        if mass < 1:
            print("N=%-6d mass=%.4f infeasible" % (N, float(mass)), flush=True)
            continue
        t0 = time.time()
        res, msg = search(N, mods, time_limit=tl, branch=10 ** 9)
        print("N=%-6d mass=%.4f |mods|=%d %s" % (N, float(mass), len(mods), msg),
              flush=True)
        if res:
            fn = "phaseB_N%d.json" % N
            json.dump({"N": N, "family": [[a, m] for a, m in res]},
                      open(fn, "w"))
            print("PHASE-B SUCCESS N=%d congs=%d -> %s" % (N, len(res), fn),
                  flush=True)
            break


if __name__ == "__main__":
    main()

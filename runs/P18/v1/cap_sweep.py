#!/usr/bin/env python3
"""
Sweep caps B upward, deciding each with cap_project machinery.
Residual pools that repeat (or shrink below mass 1) are killed for free;
new residual pools are decided by the complete lookahead DFS.

Usage: cap_sweep.py B_start B_end [per_B_time_limit_s]
"""
import sys
from fractions import Fraction

from cap_project import decide, project
from twophase import is_prime


def main():
    b0, b1 = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 21600.0
    killed_pools = [tuple()]
    # B=256 residual already killed by the branch fleet (see NOTES):
    killed_pools.append((4, 6, 10, 12, 16, 18, 28, 30, 36, 40, 42, 60, 70,
                         72, 96, 100, 108, 112, 126, 150, 162, 180, 192,
                         196, 210, 240, 250, 256))
    for B in range(b0, b1 + 1):
        if not is_prime(B + 1):
            continue
        pool = [n for n in range(4, B + 1) if is_prime(n + 1)]
        S, residual = project(pool)
        key = tuple(residual)
        if any(set(key) <= set(k) for k in killed_pools):
            print("B=%d residual subset of killed pool -> KILLED (inherited)"
                  % B, flush=True)
            continue
        mass = sum(Fraction(1, n) for n in residual)
        if mass < 1:
            print("B=%d KILLED (residual mass %.6f < 1). Definitive."
                  % (B, float(mass)), flush=True)
            killed_pools.append(key)
            continue
        print("B=%d NEW residual pool (%d moduli, mass %.6f): %s"
              % (B, len(residual), float(mass), residual), flush=True)
        res = decide(residual, B, tl)
        if res == "killed":
            killed_pools.append(key)
        else:
            print("SWEEP STOPPED at B=%d (%s)" % (B, res), flush=True)
            return
    print("SWEEP COMPLETE through B=%d: all killed. Definitive." % b1,
          flush=True)


if __name__ == "__main__":
    main()

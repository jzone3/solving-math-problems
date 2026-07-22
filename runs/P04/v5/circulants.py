"""Probe 3a: all even-degree connected circulants, n=13..20, degree >= 6.

Literature note: circulants are widely conjectured (Alspach) and in many cases
proven Hamilton-decomposable, so these should all pass; this is a calibration
probe of the tight/structured corner plus a solver sanity sweep.
"""
import itertools
import math
import sys
from hajos import hajos_ok, is_eulerian, rlc_decompose

def circulant(n, S):
    edges = set()
    for d in S:
        for v in range(n):
            u, w = v, (v + d) % n
            edges.add((min(u, w), max(u, w)))
    return tuple(sorted(edges))

def main():
    for n in range(13, 21):
        half = n // 2
        ds = list(range(1, half + 1))
        cnt = 0
        for r in range(1, len(ds) + 1):
            for S in itertools.combinations(ds, r):
                edges = circulant(n, S)
                deg = 2 * len(edges) / n
                if deg < 6 or int(deg) % 2:
                    continue
                if not is_eulerian(n, edges):
                    continue
                if math.gcd(n, *S) != 1:
                    continue
                cnt += 1
                bound = (n - 1) // 2
                h = rlc_decompose(n, edges, tries=300)
                if h is not None and len(h) <= bound:
                    continue
                ok, cyc = hajos_ok(n, edges, time_limit=900)
                print(f"HARD-FOR-HEURISTIC n={n} S={S} cpSAT={ok}", flush=True)
                if ok is False:
                    print(f"*** COUNTEREXAMPLE n={n} S={S} edges={edges}", flush=True)
        print(f"n={n}: {cnt} circulants checked, all OK", flush=True)

if __name__ == "__main__":
    main()

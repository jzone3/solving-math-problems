#!/usr/bin/env python3
"""P16: dense integer scan of the k=3 'bipartite + gadget cell' quotient family.

Cells: X (size a), Y (size a), C (size c).
B = [[x_int, p,   q1 ],
     [p,   y_int, q2 ],
     [Q1,  Q2,  r  ]]  with Q1 = a*q1/c, Q2 = a*q2/c (must be integers <= a),
p <= a (cross X-Y), q1,q2 <= c, internal x_int,y_int <= a-1 (parity), r <= c-1 (parity).
Float screen; prints candidates with margin > 1e-7.
"""
import math
import sys
import numpy as np
import itertools

import search_quotient as sq


def scan(which, amax=120, cmax=40):
    best = (-1e18, None)
    for a in range(2, amax + 1):
        for c in range(1, min(a, cmax) + 1):
            for q1 in range(0, min(c, 12) + 1):
                if (a * q1) % c:
                    continue
                Q1 = a * q1 // c
                if Q1 > a:
                    continue
                for q2 in range(0, q1 + 1):  # wlog q2 <= q1
                    if (a * q2) % c:
                        continue
                    Q2 = a * q2 // c
                    if Q2 > a:
                        continue
                    if q1 == 0 and q2 == 0:
                        continue
                    for p in range(0, a + 1):
                        if p == 0 and (q1 == 0 or q2 == 0):
                            continue
                        for x_int in (0, 1, 2, a - 2, a - 1):
                            if x_int < 0 or x_int > a - 1 or (x_int % 2 and a % 2):
                                continue
                            for y_int in (0, x_int):
                                if y_int < 0 or y_int > a - 1 or (y_int % 2 and a % 2):
                                    continue
                                for r in (0, 1, 2, c - 1):
                                    if r < 0 or r > c - 1 or (r % 2 and c % 2):
                                        continue
                                    n = [a, a, c]
                                    B = [[x_int, p, q1], [p, y_int, q2], [Q1, Q2, r]]
                                    v = sq.margin(which, n, B)
                                    if v is not None and v > best[0]:
                                        best = (v, (n, [row[:] for row in B]))
                                        if v > 1e-7:
                                            print(f"[{which}] CANDIDATE margin={v:.9f} n={n} B={B}", flush=True)
        if a % 20 == 0:
            print(f"[{which}] a={a} done best={best[0]:.9f} {best[1]}", flush=True)
    print(f"[{which}] SCAN OVERALL best={best[0]:.9f} {best[1]}")


if __name__ == "__main__":
    scan(int(sys.argv[1]))

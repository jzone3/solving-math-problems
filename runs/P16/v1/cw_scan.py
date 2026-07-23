#!/usr/bin/env python3
"""P16: scan Collatz-Wielandt test-vector family x = a*d + b*m + c on the
signless Laplacian Q = D + A. For positive x: mu(L) <= rho(Q) <= max_u (Qx)_u/x_u.
Find (a,b,c) such that max_u (Qx)_u/x_u <= max-edge f44 (resp f46) for ALL
connected graphs up to N. Any surviving triple is a proof candidate.
Usage: cw_scan.py which nmax"""
import itertools
import subprocess
import sys

import numpy as np

sys.path.insert(0, ".")
from fast_exhaustive import g6_batch_to_adj

WHICH = int(sys.argv[1]) if len(sys.argv) > 1 else 44
NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 8

AS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
BS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
CS = [-2.0, -1.0, 0.0, 1.0, 2.0]
# linear family ('lin', a, b, c): x = a*d + b*m + c
CAND = [("lin", a, b, c) for a in AS for b in BS for c in CS if a + b > 0]
# power family ('pow', p, q, c): x = d^p * m^q + c
PS = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
CAND += [("pow", p, q, c) for p in PS for q in PS for c in [-1.0, 0.0, 1.0]
         if (p, q) != (0.0, 0.0)]
# sum-power family ('sp', p, 0, c): x = (d+m)^p + c
CAND += [("sp", p, 0.0, c) for p in PS if p != 0.0 for c in [-2.0, -1.0, 0.0, 1.0]]

BATCH = 4096


def main():
    alive = {t: True for t in CAND}
    for n in range(4, NMAX + 1):
        proc = subprocess.Popen(["nauty-geng", "-c", "-q", str(n)],
                                stdout=subprocess.PIPE, text=True, bufsize=1 << 22)
        buf = []
        def flush(buf):
            if not buf:
                return
            A = g6_batch_to_adj(buf, n)
            d = A.sum(axis=2)
            m = np.einsum('bij,bj->bi', A, d) / d
            di = d[:, :, None]; dj = d[:, None, :]
            mi = m[:, :, None]; mj = m[:, None, :]
            E = A > 0
            big = 1e18
            if WHICH == 44:
                inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
            else:
                inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
            f = np.where(E & (inner >= 0), 2 + np.sqrt(np.clip(inner, 0, None)), -big).max(axis=(1, 2))
            for t, ok in alive.items():
                if not ok:
                    continue
                kind, a, b, c = t
                if kind == "lin":
                    x = a * d + b * m + c
                elif kind == "pow":
                    x = d ** a * m ** b + c
                else:
                    x = (d + m) ** a + c
                if x.min() <= 1e-9:
                    alive[t] = False
                    continue
                qx = d * x + np.einsum('bij,bj->bi', A, x)
                r = (qx / x).max(axis=1)
                if (r > f + 1e-9).any():
                    alive[t] = False
        for line in proc.stdout:
            line = line.strip()
            if line:
                buf.append(line)
                if len(buf) >= BATCH:
                    flush(buf); buf = []
        flush(buf)
        nal = sum(alive.values())
        print(f"which={WHICH} after n={n}: {nal} candidates alive", flush=True)
        if nal == 0:
            break
    for t, ok in alive.items():
        if ok:
            print(f"SURVIVOR which={WHICH}: {t}", flush=True)


if __name__ == "__main__":
    main()

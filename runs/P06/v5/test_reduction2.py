"""Test the stronger AM-GM reduction chain for conjecture 129.

sqrt(dudv) <= (du+dv)/2  =>  sum_E sqrt(dudv) <= M1/2  =>  R >= 2m^2/M1.
Reduced conjecture D*:  4 n^2 m^4 >= M1^2 (n*M1 + 2mn - 4m^2)  (n,m,M1 only).

Also tests the de Caen composite: with M1max = m(2m/(n-1) + n - 2),
is 4 n^2 m^4 >= M1max^2 (n*M1max + 2mn - 4m^2) for all n, m?
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj


def dstar(n, m, M1):
    return 4 * n * n * m ** 4 - M1 ** 2 * (n * M1 + 2 * m * n - 4 * m * m)


def scan_graphs(n):
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    worst = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        A = g6_to_adj(line)
        d = A.sum(axis=1).astype(float)
        m = d.sum() / 2
        if m == 0:
            continue
        M1 = float(np.sum(d * d))
        worst.append((dstar(n, m, M1), line))
        if len(worst) > 10000:
            worst.sort()
            del worst[5:]
    worst.sort()
    print(f"n={n} worst D* (violation if <0):")
    for s, g in worst[:5]:
        print(f"  {s:+.6f}  {g}")


def decaen_grid(nmax):
    bad = 0
    worst = (1e18, None)
    for n in range(2, nmax + 1):
        for m in range(1, n * (n - 1) // 2 + 1):
            M1max = m * (2 * m / (n - 1) + n - 2)
            v = dstar(n, m, M1max)
            if v < worst[0]:
                worst = (v, (n, m))
            if v < -1e-6:
                bad += 1
    print(f"deCaen composite: worst={worst[0]:.4f} at (n,m)={worst[1]}, violations={bad}")


if __name__ == "__main__":
    if sys.argv[1] == "grid":
        decaen_grid(int(sys.argv[2]))
    else:
        scan_graphs(int(sys.argv[1]))

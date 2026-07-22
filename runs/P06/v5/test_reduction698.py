"""Reduction chain tests for conjecture 698A (s_minus <= Randic).

s_minus^2 = 2m - s_plus^2 <= 2m - lambda1^2          (always)
lambda1^2 >= M1/n                                     (Hofmeister)
E*: lambda1^2 + R^2 >= 2m        (implies 698A)
F*: R^2 >= 2m - M1/n             (implies E* via Hofmeister)

Scans all graphs of order n for violations of E* and F*.
Usage: python3 test_reduction698.py <n>
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj, randic_from_adj


def main():
    n = int(sys.argv[1])
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    worstE, worstF = [], []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        A = g6_to_adj(line)
        d = A.sum(axis=1).astype(float)
        m = d.sum() / 2
        if m == 0:
            continue
        R = randic_from_adj(A, d)
        M1 = float(np.sum(d * d))
        lam1 = float(np.linalg.eigvalsh(A.astype(float))[-1])
        e = lam1 * lam1 + R * R - 2 * m       # want >= 0
        f = R * R - (2 * m - M1 / n)          # want >= 0
        worstE.append((e, line))
        worstF.append((f, line))
        if len(worstE) > 10000:
            worstE.sort()
            del worstE[5:]
            worstF.sort()
            del worstF[5:]
    worstE.sort()
    worstF.sort()
    print(f"n={n} worst E* (lam1^2+R^2-2m, violation if <0):")
    for s, g in worstE[:5]:
        print(f"  {s:+.8f}  {g}")
    print(f"n={n} worst F* (R^2-2m+M1/n):")
    for s, g in worstF[:5]:
        print(f"  {s:+.8f}  {g}")


if __name__ == "__main__":
    main()

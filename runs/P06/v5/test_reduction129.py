"""Reduction chain for conjecture 129 (dev_L <= R), mirroring the 698A proof.

Chain:  R >= m/lambda1   (Rayleigh x=sqrt(d) + Cauchy-Schwarz, proved)
        so 129 follows from  G*: lambda1 * dev_L <= m.
        Hong: lambda1^2 <= 2m - n' + 1 (n' = non-isolated count, min degree >=1)
        so G* follows from  H*: (2m - n' + 1) * dev_L^2 <= m^2   (degrees only).

dev_L^2 = (M1 + 2m)/n - 4m^2/n^2   (n = all vertices, incl. isolated).

Both G*, H* are tight at stars and at K_k u (k-2)K_1.
Usage: python3 test_reduction129.py <n>
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj


def main():
    n = int(sys.argv[1])
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    worstG, worstH = [], []
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
        dev2 = (M1 + 2 * m) / n - 4 * m * m / n / n
        nprime = int(np.sum(d > 0))
        lam1 = float(np.linalg.eigvalsh(A.astype(float))[-1])
        g = m - lam1 * np.sqrt(dev2)                     # want >= 0
        h = m * m - (2 * m - nprime + 1) * dev2          # want >= 0
        worstG.append((g, line))
        worstH.append((h, line))
        if len(worstG) > 10000:
            worstG.sort()
            del worstG[5:]
            worstH.sort()
            del worstH[5:]
    worstG.sort()
    worstH.sort()
    print(f"n={n} worst G* (m - lam1*dev_L, violation if <0):")
    for s, g in worstG[:5]:
        print(f"  {s:+.8f}  {g}")
    print(f"n={n} worst H* (m^2 - (2m-n'+1)*dev2):")
    for s, g in worstH[:5]:
        print(f"  {s:+.8f}  {g}")


if __name__ == "__main__":
    main()

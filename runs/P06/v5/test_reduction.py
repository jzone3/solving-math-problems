"""Test the Cauchy-Schwarz reduction chain for conjecture 129.

R >= m^2 / sum_E sqrt(dudv)          (Cauchy-Schwarz)
(sum_E sqrt(dudv))^2 <= m * M2       (Cauchy-Schwarz),  M2 = sum_E dudv
=> R^2 >= m^3 / M2.

Reduced conjecture C*:  m^3 >= M2 * ( (M1 + 2m)/n - 4m^2/n^2 ),
with M1 = sum d^2 (first Zagreb), which implies 129 (std reading).

Scans all graphs of order n for violations of C* (and of the weaker
half-reduction m^4 >= (sum_E sqrt(dudv))^2 * dev2).
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj


def main():
    n = int(sys.argv[1])
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    worstC, worstH = [], []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        A = g6_to_adj(line)
        d = A.sum(axis=1).astype(float)
        m = d.sum() / 2
        if m == 0:
            continue
        i, j = np.nonzero(np.triu(A, 1))
        M2 = float(np.sum(d[i] * d[j]))
        S = float(np.sum(np.sqrt(d[i] * d[j])))
        M1 = float(np.sum(d * d))
        dev2 = (M1 + 2 * m) / n - 4 * m * m / n / n
        cstar = m ** 3 - M2 * dev2          # want >= 0
        half = m ** 4 - S * S * dev2        # want >= 0
        worstC.append((cstar, line))
        worstH.append((half, line))
        if len(worstC) > 10000:
            worstC.sort()
            del worstC[5:]
            worstH.sort()
            del worstH[5:]
    worstC.sort()
    worstH.sort()
    print(f"n={n} worst C* (m^3 - M2*dev2), violation if <0:")
    for s, g in worstC[:5]:
        print(f"  {s:+.8f}  {g}")
    print(f"n={n} worst half-reduction (m^4 - S^2*dev2):")
    for s, g in worstH[:5]:
        print(f"  {s:+.8f}  {g}")


if __name__ == "__main__":
    main()

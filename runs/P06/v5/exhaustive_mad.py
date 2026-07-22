"""Exhaustive scan for the alternate 'deviation = mean absolute deviation' reading
of conjecture 129: MAD(Laplacian eigenvalues) <= Randic index.

Usage: python3 exhaustive_mad.py <n>
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj, randic_from_adj


def main():
    n = int(sys.argv[1])
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    best = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        A = g6_to_adj(line)
        d = A.sum(axis=1).astype(float)
        if d.sum() == 0:
            continue
        R = randic_from_adj(A, d)
        lam = np.linalg.eigvalsh(np.diag(d) - A.astype(float))
        madv = float(np.mean(np.abs(lam - lam.mean())))
        best.append((madv - R, line))
        if len(best) > 10000:
            best.sort(reverse=True)
            del best[5:]
    best.sort(reverse=True)
    print(f"n={n} top MAD-reading (mad_L - R, violation if >0):")
    for s, g in best[:5]:
        print(f"  {s:+.8f}  {g}")


if __name__ == "__main__":
    main()

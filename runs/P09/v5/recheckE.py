"""Independent 50-digit recheck of ELW near-bound candidates from logsE/cand_*.txt.

ELW (Elphick-Linz-Wocjan, arXiv:2101.05229 Conj. 2): sum of squares of the
min(omega, #positive) largest eigenvalues <= 2m(1-1/omega). Prints PASS iff no
candidate has a positive score at 50-digit precision.
"""
import glob
import numpy as np
from mpmath import mp, mpf, matrix, eig
from core import max_clique

mp.dps = 50

def g6_to_adj(s):
    n = ord(s[0]) - 63
    bits = []
    for c in s[1:]:
        bits += [(ord(c) - 63) >> (5 - i) & 1 for i in range(6)]
    A = np.zeros((n, n), dtype=int)
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]
            k += 1
    return A

def main():
    g6s = []
    for f in sorted(glob.glob("logsE/cand_*.txt")):
        for line in open(f):
            if line.startswith("CAND "):
                g6s.append(line.split()[1])
    print(len(g6s), "candidates")
    viol = 0
    for g6 in g6s:
        A = g6_to_adj(g6)
        n = len(A)
        m = int(A.sum() // 2)
        w = max_clique(A.astype(float))
        M = matrix(n, n)
        for i in range(n):
            for j in range(n):
                M[i, j] = mpf(int(A[i, j]))
        ev = sorted([x.real for x in eig(M, left=False, right=False)], reverse=True)
        L = sum(l * l for l in ev[:w] if l > 0)
        s = L - 2 * m * (1 - mpf(1) / w)
        if s > mpf("1e-30"):
            viol += 1
            print("VIOLATION", g6, "n=%d m=%d w=%d score=%s" % (n, m, w, mp.nstr(s, 3)))
    print("PASS: no violations" if viol == 0 else "FAIL: %d violations" % viol)

if __name__ == "__main__":
    main()

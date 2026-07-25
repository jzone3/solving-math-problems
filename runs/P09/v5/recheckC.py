"""Independent 50-digit recheck of the dense-corner (complement sweep) candidates.

Reads logsC/cand_*.txt (graph6 of the SPARSE input graph; the scored graph is its
complement), recomputes omega exactly and lambda1^2+lambda2^2 - 2m(1-1/omega) with
mpmath at 50 digits. Prints PASS iff no positive score.
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
    for f in sorted(glob.glob("logsC/cand_*.txt")):
        for line in open(f):
            if line.startswith("CAND "):
                g6s.append(line.split()[1])
    print(len(g6s), "candidates")
    viol = 0
    for g6 in g6s:
        A = g6_to_adj(g6)
        n = len(A)
        C = 1 - A - np.eye(n, dtype=int)
        m = int(C.sum() // 2)
        w = max_clique(C.astype(float))
        M = matrix(n, n)
        for i in range(n):
            for j in range(n):
                M[i, j] = mpf(int(C[i, j]))
        ev = sorted([x.real for x in eig(M, left=False, right=False)])
        s = ev[-1] ** 2 + ev[-2] ** 2 - 2 * m * (1 - mpf(1) / w)
        print(g6, "n=%d m=%d w=%d score=%s" % (n, m, w, mp.nstr(s, 3)))
        if s > mpf("1e-30"):
            viol += 1
    print("PASS: no violations" if viol == 0 else "FAIL: %d violations" % viol)

if __name__ == "__main__":
    main()

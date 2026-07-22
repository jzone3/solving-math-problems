#!/usr/bin/env python3
"""Independent second verifier (methodology rule: differently-written checker).

Reads graph6 lines on stdin. NO pruning, NO t-range reduction: checks Brouwer's
inequality S_t <= m + t(t+1)/2 for EVERY t in 1..n with numpy eigvalsh.
Prints worst (margin, t, graph6) and a SUMMARY line. Used to cross-validate the
C pipeline (its GMB prune and complement-duality t-restriction) on n <= 9 fully
and on samples of larger runs.
"""
import sys
import numpy as np

def parse_g6(line):
    b = line.strip()
    n = ord(b[0]) - 63
    assert 0 < n <= 62
    bits = []
    for ch in b[1:]:
        v = ord(ch) - 63
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1
            idx += 1
    return n, A

def main():
    total = 0
    worst = (-1e18, None, None)
    viol = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, A = parse_g6(line)
        total += 1
        m = int(A.sum()) // 2
        L = np.diag(A.sum(axis=1)) - A
        ev = np.linalg.eigvalsh(L)[::-1]  # descending
        s = np.cumsum(ev)
        for t in range(1, n + 1):
            margin = s[t - 1] - m - t * (t + 1) / 2
            if margin > worst[0]:
                worst = (margin, t, line)
            if margin > 1e-6:
                viol += 1
                print("VIOL", margin, t, line)
    print(f"SUMMARY2 total={total} viol={viol} worstmargin={worst[0]:.9f} "
          f"at t={worst[1]} g6={worst[2]}")

if __name__ == "__main__":
    main()

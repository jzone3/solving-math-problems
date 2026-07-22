"""Exhaustive scan of all graphs of order n (nauty-geng) for conjectures 129 / 698A.

Uses the identity  sum(lap_eigs^2) = sum d_i(d_i+1), so
dev_L^2 = Var(deg) + mean(deg): no eigensolve needed for 129.
698A needs one adjacency eigensolve per graph.

Usage: python3 exhaustive.py <n> [--connected] [--top K] [--skip698]
"""

import subprocess
import sys
import numpy as np


def g6_to_adj(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        bits.extend((x >> s) & 1 for s in range(5, -1, -1))
    A = np.zeros((n, n), dtype=np.int8)
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]
            k += 1
    return A


def randic_from_adj(A, d):
    i, j = np.nonzero(np.triu(A, 1))
    return float(np.sum(1.0 / np.sqrt(d[i] * d[j])))


def main():
    n = int(sys.argv[1])
    connected = "--connected" in sys.argv
    skip698 = "--skip698" in sys.argv
    topk = 5
    if "--top" in sys.argv:
        topk = int(sys.argv[sys.argv.index("--top") + 1])

    args = ["nauty-geng", "-q", str(n)]
    if connected:
        args.insert(2, "-c")
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)

    best129, best698 = [], []
    cnt = 0
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        cnt += 1
        A = g6_to_adj(line)
        d = A.sum(axis=1).astype(float)
        m2 = d.sum()
        if m2 == 0:
            continue
        # isolated vertices break randic only if edges exist; randic ignores them
        R = randic_from_adj(A, d)
        dev2 = (np.sum(d * (d + 1))) / n - (m2 / n) ** 2
        s129 = float(np.sqrt(dev2)) - R
        best129.append((s129, line))
        if len(best129) > 10000:
            best129.sort(reverse=True)
            del best129[topk:]
        if not skip698:
            lam = np.linalg.eigvalsh(A.astype(float))
            sm = float(np.sqrt(np.sum(lam[lam < 0] ** 2)))
            best698.append((sm - R, line))
            if len(best698) > 10000:
                best698.sort(reverse=True)
                del best698[topk:]

    best129.sort(reverse=True)
    best698.sort(reverse=True)
    print(f"n={n} connected={connected} graphs={cnt}")
    print("top 129 (dev_L - R):")
    for s, g in best129[:topk]:
        print(f"  {s:+.8f}  {g}")
    if not skip698:
        print("top 698A (s_minus - R):")
        for s, g in best698[:topk]:
            print(f"  {s:+.8f}  {g}")


if __name__ == "__main__":
    main()

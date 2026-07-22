"""Exhaustive verification over all connected graphs of order n (nauty-geng -c),
checking dev(D) <= min(n+, n-) and the proof-chain
   dev <= diam/2 <= floor((diam+1)/2) = n+(P_{diam+1}) <= n+(G), n-(G).
Usage: python3 exhaustive_geng.py <n>
"""
import subprocess
import sys
import numpy as np


def g6_to_adj(line):
    b = line.strip().encode()
    data = [c - 63 for c in b]
    n = data[0]
    assert n < 63
    bits = []
    for c in data[1:]:
        bits.extend((c >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((n, n))
    t = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[t]
            t += 1
    return A


def bfs_dist(A):
    n = len(A)
    nbrs = [np.nonzero(A[i])[0] for i in range(n)]
    D = np.full((n, n), -1, dtype=int)
    for s in range(n):
        D[s, s] = 0
        q = [s]
        while q:
            nq = []
            for u in q:
                for v in nbrs[u]:
                    if D[s, v] < 0:
                        D[s, v] = D[s, u] + 1
                        nq.append(v)
            q = nq
    return D


def main(n):
    proc = subprocess.Popen(["nauty-geng", "-c", "-q", str(n)],
                            stdout=subprocess.PIPE, text=True)
    cnt = 0
    worst39 = worst40 = -1e18
    for line in proc.stdout:
        A = g6_to_adj(line)
        D = bfs_dist(A).astype(float)
        x = D.reshape(-1)
        dev = float(np.sqrt(np.mean((x - x.mean()) ** 2)))
        ev = np.linalg.eigvalsh(A)
        npos = int(np.sum(ev > 1e-8))
        nneg = int(np.sum(ev < -1e-8))
        d = int(D.max())
        m39 = dev - npos
        m40 = dev - nneg
        worst39 = max(worst39, m39)
        worst40 = max(worst40, m40)
        # proof chain
        assert dev <= d / 2 + 1e-9, (line, dev, d)
        assert npos >= (d + 1) // 2 and nneg >= (d + 1) // 2, (line, npos, nneg, d)
        if m39 > 0 or m40 > 0:
            print("COUNTEREXAMPLE", line.strip(), dev, npos, nneg)
        cnt += 1
        if cnt % 500000 == 0:
            print(f"...{cnt} done, worst m39={worst39:.4f} m40={worst40:.4f}",
                  flush=True)
    print(f"n={n}: {cnt} connected graphs, worst margin39={worst39:.6f}, "
          f"worst margin40={worst40:.6f}, proof chain held everywhere")


if __name__ == "__main__":
    main(int(sys.argv[1]))

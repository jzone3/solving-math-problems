"""Exhaustive Bollobas-Nikiforov check over geng output (graph6 on stdin).

Vectorized: decodes g6 lines in chunks, batched eigvalsh. With r = 2m - l1^2 - l2^2 >= 0,
   violation  <=>  omega * r < 2m  (omega SMALL helps violation).
Necessary condition (omega >= 2): r < m. Survivors are resolved by a greedy clique lower
bound (if greedy_size * r >= 2m the graph is safe) and exact max_clique otherwise.
Complete graphs K_n are excluded by the conjecture statement.

Usage: geng -q n | python3 exhaust.py n [tag]
Prints one summary line; any true violation (score > 1e-6) is printed loudly.
"""
import sys

import numpy as np

from bn_core import max_clique, evaluate

TOL = 1e-7


def greedy_clique(n, adj):
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    cand = (1 << n) - 1
    size = 0
    for v in order:
        if (cand >> v) & 1:
            size += 1
            cand &= adj[v]
    return size


def main():
    n = int(sys.argv[1])
    tag = sys.argv[2] if len(sys.argv) > 2 else ""
    nb = n * (n - 1) // 2
    nchars = (nb + 5) // 6
    linelen = 1 + nchars + 1  # header char + data + newline
    iu = np.triu_indices(n, 1)
    # bit order of graph6: column-major upper triangle (j from 1..n-1, i<j)
    cols = []
    for j in range(1, n):
        for i in range(j):
            cols.append((i, j))
    pad = nchars * 6 - nb
    total = 0
    checked = 0
    best = -1e18
    best_g6 = ""
    complete_seen = 0
    buf = sys.stdin.buffer
    while True:
        raw = buf.read(linelen * 20000)
        if not raw:
            break
        arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, linelen)
        k = arr.shape[0]
        total += k
        data = arr[:, 1:1 + nchars] - 63
        bits = np.unpackbits(data.astype(np.uint8), axis=1)
        # each char contributes bits 2..7 (6 low bits of the byte)
        bits = bits.reshape(k, nchars, 8)[:, :, 2:].reshape(k, nchars * 6)
        bits = bits[:, :nb] if pad == 0 else bits[:, :nb]
        A = np.zeros((k, n, n), dtype=np.float64)
        for idx, (i, j) in enumerate(cols):
            A[:, i, j] = bits[:, idx]
            A[:, j, i] = bits[:, idx]
        m2 = bits.sum(axis=1) * 2.0  # 2m
        w = np.linalg.eigvalsh(A)
        l1 = w[:, -1]
        l2 = w[:, -2]
        r = m2 - l1 * l1 - l2 * l2
        # violation iff omega * r < 2m; omega >= 2 whenever m > 0, so prune on 2r < 2m.
        surv = np.nonzero((2.0 * r < m2 + TOL) & (m2 > 0))[0]
        for s in surv:
            row = bits[s]
            adj = [0] * n
            for idx, (i, j) in enumerate(cols):
                if row[idx]:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
            g = greedy_clique(n, adj)
            if g * r[s] >= m2[s] - TOL:
                if g < n:
                    continue  # safe: omega >= g large enough
            om = max_clique(n, adj)
            if om >= n:
                complete_seen += 1
                continue
            if om * r[s] >= m2[s] - TOL:
                continue
            checked += 1
            score, ratio, *_ = evaluate(n, adj)
            if score > best:
                best = score
                best_g6 = arr[s, :1 + nchars].tobytes().decode()
            if score > 1e-6:
                print(f"VIOLATION n={n} g6={arr[s, :1+nchars].tobytes().decode()} "
                      f"score={score}", flush=True)
    print(f"[{tag}] n={n} total={total} clique_checked={checked} complete={complete_seen} "
          f"best_score={best:.6e} best_g6={best_g6}", flush=True)


if __name__ == "__main__":
    main()

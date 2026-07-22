"""Exhaustive check of BN over ALL graphs of order n via nauty geng.

Pipeline: geng -c n (connected only; disconnected reduce to Nikiforov, see NOTES §2)
-> parse graph6 in batches -> batched eigvalsh -> violation needs
omega >= k+1 where k = floor(2m / (2m - L)), L = lam1^2 + lam2^2 (L < 2m always
unless complete) -> exact clique only for candidates.

Usage: python3 exhaustive.py <n> [res] [mod]   (geng res/mod splitting)
Prints candidate graphs (should be none) and a final SUMMARY line.
"""
import sys, subprocess
import numpy as np
from core import max_clique

def g6_to_adj_batch(lines, n):
    B = len(lines)
    nb = n * (n - 1) // 2
    nbytes = (nb + 5) // 6
    arr = np.zeros((B, nbytes), dtype=np.uint8)
    for i, ln in enumerate(lines):
        arr[i] = np.frombuffer(ln[1:1 + nbytes], dtype=np.uint8) - 63
    bits = ((arr[:, :, None] >> np.arange(5, -1, -1)[None, None, :]) & 1).reshape(B, -1)[:, :nb]
    A = np.zeros((B, n, n), dtype=np.float64)
    iu = np.triu_indices(n, 1)
    # graph6 bit order: column-major upper triangle (x_{0,1}, x_{0,2}, x_{1,2}, x_{0,3}, ...)
    order = []
    for j in range(1, n):
        for i in range(j):
            order.append((i, j))
    oi = np.array([o[0] for o in order]); oj = np.array([o[1] for o in order])
    A[:, oi, oj] = bits
    A[:, oj, oi] = bits
    return A

def run(n, res=0, mod=1, batch=20000):
    cmd = ["nauty-geng", "-cq", str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    total = 0
    cand = 0
    worst = -1e9
    buf = []
    def process(buf):
        nonlocal total, cand, worst
        A = g6_to_adj_batch(buf, n)
        w = np.linalg.eigvalsh(A)
        L = w[:, -1] ** 2 + w[:, -2] ** 2
        m2 = A.sum(axis=(1, 2))  # = 2m
        # candidate if L > 2m(1-1/omega) possible for some omega<=n-? i.e. need
        # omega > 2m/(2m-L). Complete graph excluded by geng? K_n is connected & generated:
        # skip m2 == n(n-1).
        mask = m2 < n * (n - 1) - 0.5  # exclude K_n
        # Violation iff omega < thr where thr = 2m/(2m-L)  (note Σλ² = 2m so L <= 2m).
        thr = np.where(m2 - L > 1e-9, m2 / np.maximum(m2 - L, 1e-300), np.inf)
        # thr <= 2 -> would need omega < 2, impossible.
        # 2 < thr <= 3 -> would need omega = 2, i.e. triangle-free: proved (Lin-Ning-Wu),
        #   but we still check exactly (cheap enough) to be fully independent of literature.
        idxs = np.nonzero(mask & (thr > 2.0))[0]
        for idx in idxs:
            om = max_clique(A[idx])
            score = L[idx] - m2[idx] * (1 - 1 / om)
            if score > worst:
                worst = score
            if score > 1e-9:
                cand += 1
                print(f"VIOLATION?! n={n} g6={buf[idx].decode()} score={score}", flush=True)
        total += len(buf)
    for line in p.stdout:
        buf.append(line.strip())
        if len(buf) >= batch:
            process(buf); buf = []
            if total % 1000000 < batch:
                print(f"... n={n} part {res}/{mod}: {total} done, worst={worst:+.6f}", flush=True)
    if buf:
        process(buf)
    print(f"SUMMARY n={n} part {res}/{mod}: total={total} candidates={cand} worst_score={worst:+.6f}", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1])
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(n, res, mod)

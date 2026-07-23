#!/usr/bin/env python3
"""P16: vectorized exhaustive screen (batched eigvalsh) for bounds 44/46.
Decodes graph6 in bulk, batches Laplacian eigists, vectorized RHS.
Also tracks the permissive convention for bound 46 (ignore non-real edges).
Usage: fast_exhaustive.py n [res mod]"""
import math
import subprocess
import sys

import numpy as np

BATCH = 4096


def g6_batch_to_adj(lines, n):
    nb = (n * (n - 1) // 2 + 5) // 6
    arr = np.frombuffer(''.join(lines).encode(), dtype=np.uint8).reshape(len(lines), nb + 1) - 63
    bits = np.unpackbits(arr[:, 1:], axis=1, bitorder='big').reshape(len(lines), (nb) * 8)
    # each byte holds 6 bits (in positions 2..7 after unpack of value<64)
    b6 = bits.reshape(len(lines), nb, 8)[:, :, 2:].reshape(len(lines), nb * 6)
    iu = np.triu_indices(n, 1)
    # graph6 packs upper triangle column by column: order (i<j) sorted by j then i
    order = np.argsort(iu[1] * n + iu[0])
    A = np.zeros((len(lines), n, n), dtype=np.float64)
    vals = b6[:, :len(iu[0])]
    A[:, iu[0][order], iu[1][order]] = vals
    A = A + A.transpose(0, 2, 1)
    return A


def screen(A, which_report):
    B, n, _ = A.shape
    d = A.sum(axis=2)
    m = np.einsum('bij,bj->bi', A, d) / d
    L = -A.copy()
    idx = np.arange(n)
    L[:, idx, idx] = d
    mu = np.linalg.eigvalsh(L)[:, -1]
    di = d[:, :, None]
    dj = d[:, None, :]
    mi = m[:, :, None]
    mj = m[:, None, :]
    E = A > 0
    big = 1e18
    in44 = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    in46 = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    res = {}
    for which, inner in ((44, in44), (46, in46)):
        neg = E & (inner < 0)
        anyneg = neg.any(axis=(1, 2))
        val = np.where(E & (inner >= 0), 2 + np.sqrt(np.clip(inner, 0, None)), -big)
        rhs = val.max(axis=(1, 2))
        margin = mu - rhs
        # strict: graphs with any negative edge are 'not clean'
        res[which] = (margin, anyneg)
    return res


def main():
    args = [a for a in sys.argv[1:] if a != "-b"]
    bip = "-b" in sys.argv
    n = int(args[0])
    resmod = args[1] + "/" + args[2] if len(args) > 2 else None
    cmd = ["nauty-geng", "-c", "-q"] + (["-b"] if bip else []) + [str(n)] + ([resmod] if resmod else [])
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 22)
    best = {44: -1e18, 46: -1e18}
    bestperm46 = -1e18
    cnt = 0
    buf = []
    def flush(buf):
        nonlocal cnt, bestperm46
        if not buf:
            return
        A = g6_batch_to_adj(buf, n)
        r = screen(A, None)
        for w in (44, 46):
            margin, anyneg = r[w]
            mx = margin.max()
            if mx > best[w]:
                best[w] = mx
            hit = margin > 1e-9
            if hit.any():
                for t in np.nonzero(hit)[0]:
                    print(f"VIOLATION{w} g6={buf[t]} margin={margin[t]} anyneg={bool(anyneg[t])}", flush=True)
            if w == 46:
                pm = margin[anyneg]
                if pm.size and pm.max() > bestperm46:
                    bestperm46 = pm.max()
        cnt += len(buf)
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        buf.append(line)
        if len(buf) >= BATCH:
            flush(buf)
            buf = []
    flush(buf)
    print(f"DONE n={n} chunk={resmod} count={cnt} best44={best[44]:.9f} best46={best[46]:.9f} bestPermissive46={bestperm46:.9f}", flush=True)


if __name__ == "__main__":
    main()

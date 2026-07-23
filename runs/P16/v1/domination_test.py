#!/usr/bin/env python3
"""P16: test graphwise domination of known TRUE upper bounds by f44/f46 max-edge.
Known true bounds tested (per graph, max over edges/vertices):
  Das   : max_{uv} (d_u+d_v+sqrt((d_u-d_v)^2+4 m_u m_v))/2
  Merris: max_v (d_v+m_v)
  Guo   : max_{uv} (d_u(d_u+m_u)+d_v(d_v+m_v))/(d_u+d_v)
If maxF44 >= known-true-bound-value for every graph, bound 44 follows from that bound.
Usage: domination_test.py n [res mod]"""
import subprocess
import sys

import numpy as np

sys.path.insert(0, ".")
from fast_exhaustive import g6_batch_to_adj

BATCH = 4096


def stats(A):
    Bn, n, _ = A.shape
    d = A.sum(axis=2)
    m = np.einsum('bij,bj->bi', A, d) / d
    di = d[:, :, None]; dj = d[:, None, :]
    mi = m[:, :, None]; mj = m[:, None, :]
    E = A > 0
    big = 1e18
    in44 = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
    f44 = np.where(E & (in44 >= 0), 2 + np.sqrt(np.clip(in44, 0, None)), -big).max(axis=(1, 2))
    in46 = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
    f46 = np.where(E & (in46 >= 0), 2 + np.sqrt(np.clip(in46, 0, None)), -big).max(axis=(1, 2))
    das = np.where(E, (di + dj + np.sqrt((di - dj) ** 2 + 4 * mi * mj)) / 2, -big).max(axis=(1, 2))
    merris = (d + m).max(axis=1)
    guo = np.where(E, (di * (di + mi) + dj * (dj + mj)) / (di + dj), -big).max(axis=(1, 2))
    return f44, f46, das, merris, guo


def main():
    n = int(sys.argv[1])
    resmod = [sys.argv[2] + "/" + sys.argv[3]] if len(sys.argv) > 3 else []
    proc = subprocess.Popen(["nauty-geng", "-c", "-q", str(n)] + resmod,
                            stdout=subprocess.PIPE, text=True, bufsize=1 << 22)
    worst = {}
    for f in ("f44", "f46"):
        for k in ("das", "merris", "guo"):
            worst[(f, k)] = (1e18, None)  # min over graphs of (fXX - known)
    cnt = 0
    buf = []
    def flush(buf):
        nonlocal cnt
        if not buf:
            return
        A = g6_batch_to_adj(buf, n)
        f44, f46, das, merris, guo = stats(A)
        for fname, fv in (("f44", f44), ("f46", f46)):
            for kname, kv in (("das", das), ("merris", merris), ("guo", guo)):
                diff = fv - kv
                t = int(diff.argmin())
                if diff[t] < worst[(fname, kname)][0]:
                    worst[(fname, kname)] = (float(diff[t]), buf[t])
        cnt += len(buf)
    for line in proc.stdout:
        line = line.strip()
        if line:
            buf.append(line)
            if len(buf) >= BATCH:
                flush(buf); buf = []
    flush(buf)
    print(f"n={n} count={cnt}")
    for key, (v, g) in sorted(worst.items()):
        dom = "DOMINATES" if v >= -1e-9 else "fails"
        print(f"  {key[0]} vs {key[1]}: min diff = {v:.6f} ({dom}) worst g6={g}")


if __name__ == "__main__":
    main()

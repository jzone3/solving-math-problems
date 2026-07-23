#!/usr/bin/env python3
"""P16: fast tree screen via gentreeg | copyg -g, batched eigvalsh."""
import subprocess
import sys

sys.path.insert(0, ".")
from fast_exhaustive import g6_batch_to_adj, screen

import numpy as np

BATCH = 4096


def main():
    n = int(sys.argv[1])
    resmod = [sys.argv[2] + "/" + sys.argv[3]] if len(sys.argv) > 3 else []
    p1 = subprocess.Popen(["nauty-gentreeg", "-q", str(n)] + resmod, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["nauty-copyg", "-gq"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True, bufsize=1 << 22)
    best = {44: -1e18, 46: -1e18}
    bp = -1e18
    cnt = 0
    buf = []
    def flush(buf):
        nonlocal cnt, bp
        if not buf:
            return
        A = g6_batch_to_adj(buf, n)
        r = screen(A, None)
        for w in (44, 46):
            margin, anyneg = r[w]
            best[w] = max(best[w], margin.max())
            hit = margin > 1e-9
            for t in np.nonzero(hit)[0]:
                print(f"VIOLATION{w} g6={buf[t]} margin={margin[t]}", flush=True)
            if w == 46:
                pm = margin[anyneg]
                if pm.size:
                    bp = max(bp, pm.max())
        cnt += len(buf)
    for line in p2.stdout:
        line = line.strip()
        if not line:
            continue
        buf.append(line)
        if len(buf) >= BATCH:
            flush(buf); buf = []
    flush(buf)
    print(f"DONE trees n={n} chunk={resmod} count={cnt} best44={best[44]:.9f} best46={best[46]:.9f} bestPerm46={bp:.9f}", flush=True)


if __name__ == "__main__":
    main()

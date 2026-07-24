#!/usr/bin/env python3
"""Check all SRGs from Spence's catalogues (srg/data/) against P09.

Files are 0/1 adjacency matrices (n rows per graph) with text headers.
Threshold prefilter: skip if t=(l1^2+l2^2)/(2m) <= 2/3 (omega<=2 proved);
otherwise exact clique number + exact ratio.
Result (2026-07-24): 43,718 SRGs across 27 parameter sets up to n=64 —
0 violations, 0 equalities.
"""
import numpy as np, sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.setrecursionlimit(100000)
from search import has_clique


def clique_number(A):
    n = len(A)
    adj = [0] * n
    for i in range(n):
        for j in range(n):
            if A[i][j]:
                adj[i] |= 1 << j
    full = (1 << n) - 1
    k = 1
    while k < n and has_clique(adj, full, k + 1):
        k += 1
    return k


def main():
    d = os.path.join(os.path.dirname(__file__), "data")
    tot = viol = eq = 0
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".bz2"):
            continue
        txt = open(os.path.join(d, fn)).read()
        rows = [l.strip() for l in txt.splitlines()
                if re.fullmatch(r"[01]+", l.strip() or "x")]
        n = int(fn.split("-")[0])
        assert len(rows) % n == 0, (fn, len(rows), n)
        for b in range(len(rows) // n):
            M = np.array([[int(c) for c in rows[b * n + i]] for i in range(n)],
                         dtype=float)
            m = int(M.sum() / 2)
            ev = np.sort(np.linalg.eigvalsh(M))
            l1, l2 = ev[-1], ev[-2]
            t = (l1 * l1 + l2 * l2) / (2 * m)
            tot += 1
            if t <= 2 / 3 - 1e-9:
                continue
            w = clique_number(M.astype(int))
            r = (l1 * l1 + l2 * l2) / (2 * m * (1 - 1 / w))
            if r > 1 + 1e-9:
                viol += 1
                print("VIOLATION", fn, b, w, r)
            elif r > 1 - 1e-9:
                eq += 1
                print("equality", fn, b, w)
        print(fn, "done", flush=True)
    print("TOTAL", tot, "violations", viol, "equalities", eq)


if __name__ == "__main__":
    main()

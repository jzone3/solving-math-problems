"""Exhaustive Woodall check over ALL simple digraphs on 6 vertices, generated
non-isomorphically by nauty (geng -> directg). Reads digraph6 from stdin.

Pipeline:
  nauty-geng -c 6 | nauty-directg | python3 exhaustive6.py
(-c: connected underlying graphs suffice, weak connectivity is required
anyway; directg generates all orientations-with-2-cycles, i.e. all digraphs
whose underlying graph is the given one, up to isomorphism.)
"""

import sys
import time

from woodall import all_dicuts, max_packing, is_strongly_connected


def parse_d6(line):
    # digraph6: '&' + N(n) + bit matrix rows (n x n, row-major)
    assert line.startswith("&")
    s = line[1:]
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> (5 - i)) & 1 for i in range(6))
    arcs = []
    idx = 0
    for u in range(n):
        for v in range(n):
            if idx < len(bits) and bits[idx]:
                if u != v:
                    arcs.append((u, v))
            idx += 1
    return n, arcs


def main():
    t0 = time.time()
    stats = {"total": 0, "tau3+": 0, "gap>0": 0}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, arcs = parse_d6(line)
        stats["total"] += 1
        if is_strongly_connected(n, arcs):
            continue
        cuts = all_dicuts(n, arcs)
        tau = min(len(c) for c in cuts) if cuts else 0
        if tau < 3:
            continue
        stats["tau3+"] += 1
        _, nu = max_packing(n, arcs, tau=tau)
        if nu < tau:
            stats["gap>0"] += 1
            print("!!! GAP:", n, arcs, tau, nu, flush=True)
        if stats["tau3+"] % 2000 == 0:
            print(f"[{time.time()-t0:7.0f}s] {stats}", flush=True)
    print(f"DONE in {time.time()-t0:.0f}s: {stats}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stream digraph6 lines (from nauty-directg) on stdin, check Woodall packing.

Usage: nauty-geng -c N | nauty-directg | python3 exhaust_d6.py [MOD RES]
Optional MOD RES splits work: only lines with lineno % MOD == RES.
"""
import sys, time
from search import check


def parse_d6(line):
    # digraph6: '&' + N(n) + bit matrix rows (n*n bits, row-major)
    assert line[0] == '&'
    s = line[1:]
    n = ord(s[0]) - 63
    assert n <= 62
    bits = []
    for ch in s[1:]:
        x = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    arcs = [(i, j) for i in range(n) for j in range(n) if bits[i * n + j]]
    return n, arcs


def main():
    mod, res = 1, 0
    if len(sys.argv) >= 3:
        mod, res = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    cnt = 0; checked = 0; bytau = {}
    for lineno, line in enumerate(sys.stdin):
        if lineno % mod != res:
            continue
        line = line.strip()
        if not line or line[0] != '&':
            continue
        cnt += 1
        n, arcs = parse_d6(line)
        r = check(n, arcs)
        if r is None:
            continue
        tau, ok, _ = r
        checked += 1
        bytau[tau] = bytau.get(tau, 0) + 1
        if not ok:
            print("!!! COUNTEREXAMPLE:", line, n, sorted(arcs), tau, flush=True)
            with open("counterexample.txt", "a") as f:
                f.write(f"d6={line} n={n} tau={tau} arcs={sorted(arcs)}\n")
        if cnt % 200000 == 0:
            print(f"[d6 {mod}/{res}] seen={cnt} checked={checked} bytau={sorted(bytau.items())} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[d6 {mod}/{res}] DONE seen={cnt} checked={checked} bytau={sorted(bytau.items())} "
          f"t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

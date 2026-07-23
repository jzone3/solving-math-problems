#!/usr/bin/env python3
"""
Decode a kissat model for gen_cnf_m.py output into n-space congruences.

Usage: decode_m.py map_m_N{N}_c{cap}.json kissat_output witness_out.json
Family A (f=0) covers the evens (2b mod 2m), family B (f=1) the odds
((2b+1) mod 2m). Result must be re-checked with solutions/P18/verify.py.
"""
import json
import sys


def main():
    mp = json.load(open(sys.argv[1]))
    true_vars = set()
    for line in open(sys.argv[2]):
        if line.startswith("v"):
            for tok in line.split()[1:]:
                v = int(tok)
                if v > 0:
                    true_vars.add(v)
    congs = []
    for key, v in mp["vars"].items():
        if v in true_vars:
            m, a, f = map(int, key.split(","))
            n = 2 * m
            congs.append([(2 * a) % n if f == 0 else (2 * a + 1) % n, n])
    json.dump({"congruences": congs}, open(sys.argv[3], "w"))
    print("decoded %d congruences -> %s" % (len(congs), sys.argv[3]))


if __name__ == "__main__":
    main()

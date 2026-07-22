#!/usr/bin/env python3
"""Decode a kissat/cadical model into a block list for (v,6)-PMD."""
import sys

K = 6

def main():
    v = int(sys.argv[1])
    modelfile = sys.argv[2]
    b = v * (v - 1) // K
    true_lits = set()
    with open(modelfile) as f:
        for line in f:
            if line.startswith('v'):
                for tok in line.split()[1:]:
                    n = int(tok)
                    if n > 0:
                        true_lits.add(n)
    blocks = []
    for bl in range(b):
        row = []
        for p in range(K):
            for s in range(v):
                var = bl * K * v + p * v + s + 1
                if var in true_lits:
                    row.append(s)
                    break
        blocks.append(row)
    for row in blocks:
        print(' '.join(map(str, row)))

if __name__ == '__main__':
    main()

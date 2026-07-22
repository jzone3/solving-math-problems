#!/usr/bin/env python3
"""Convert HoG enquiry JSON (adjacencyList) to graph6 lines: id<TAB>g6."""
import json
import sys


def to_g6(n, adjlist):
    bits = []
    adjset = [set(a) for a in adjlist]
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adjset[i] else 0)
    out = [chr(n + 63)] if n < 63 else [chr(126), chr(63 + (n >> 12 & 63)), chr(63 + (n >> 6 & 63)), chr(63 + (n & 63))]
    for k in range(0, len(bits), 6):
        chunk = bits[k:k + 6] + [0] * (6 - len(bits[k:k + 6]))
        out.append(chr(63 + int(''.join(map(str, chunk)), 2)))
    return ''.join(out)


d = json.load(open(sys.argv[1]))
for g in d['_embedded']['graphSearchModelList']:
    al = g['adjacencyList']
    print(f"{g['graphId']}\t{to_g6(len(al), al)}")

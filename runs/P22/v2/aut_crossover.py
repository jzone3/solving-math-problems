#!/usr/bin/env python3
"""Automorphism-image crossover: take a record coloring X and its images
X^sigma under affine automorphisms sigma(x)=a*x+b (a in C) of G127 (and the
color-flipped images). Each image has the same mono count, giving structured
mid-distance parents. For each image, sort by Hamming distance to X and run
exact RC2 recombination over the difference set (bounded), keeping the rest
fixed to X. Usage: aut_crossover.py <record.txt> <out_prefix> [max_ham=700]
"""
import sys

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)
edges = sorted((0, c) for c in C) + sorted(
    (u, v) for u in range(1, p) for v in adj[u] if u < v)
NE = len(edges)
var = {e: i for i, e in enumerate(edges)}
tri_edges = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tri_edges.append((var[(u, v)], var[(u, w)], var[(v, w)]))
etris = [[] for _ in range(NE)]
for t, (a, b, c) in enumerate(tri_edges):
    etris[a].append(t); etris[b].append(t); etris[c].append(t)


def load(fn):
    toks = open(fn).read().split()
    bits = [t for t in toks if set(t) <= {"0", "1"} and len(t) == NE][0]
    return [int(b) for b in bits]


def mono_count(col):
    return sum(1 for (a, b, c) in tri_edges if col[a] == col[b] == col[c])


def image(col, a, b, flip):
    out = [0] * NE
    for i, (u, v) in enumerate(edges):
        uu, vv = (a * u + b) % p, (a * v + b) % p
        j = var[(min(uu, vv), max(uu, vv))]
        out[j] = col[i] ^ flip
    return out


def recombine(A, B):
    diff = [e for e in range(NE) if A[e] != B[e]]
    free = sorted(diff)
    fidx = {e: i + 1 for i, e in enumerate(free)}
    col = A[:]
    wcnf = WCNF()
    seen = set()
    for e in free:
        for t in etris[e]:
            if t in seen:
                continue
            seen.add(t)
            lits_pos, lits_neg, sat_pos, sat_neg = [], [], False, False
            for x in tri_edges[t]:
                if x in fidx:
                    lits_pos.append(fidx[x]); lits_neg.append(-fidx[x])
                else:
                    if col[x] == 1:
                        sat_pos = True
                    else:
                        sat_neg = True
            if not sat_pos:
                wcnf.append(lits_pos, weight=1)
            if not sat_neg:
                wcnf.append(lits_neg, weight=1)
    fixed = sum(1 for t, (a, b, c) in enumerate(tri_edges)
                if t not in seen and col[a] == col[b] == col[c])
    with RC2(wcnf) as rc2:
        model = rc2.compute()
        total = fixed + rc2.cost
    mset = {abs(l): l > 0 for l in model}
    for e in free:
        v = fidx[e]
        if v in mset:
            col[e] = 1 if mset[v] else 0
    return total, col


fn, out_prefix = sys.argv[1], sys.argv[2]
max_ham = int(sys.argv[3]) if len(sys.argv) > 3 else 700
X = load(fn)
cx = mono_count(X)
print(f"parent cost {cx}", flush=True)
cands = []
for a in C:
    for b in range(p):
        for flip in (0, 1):
            if a == 1 and b == 0 and flip == 0:
                continue
            Y = image(X, a, b, flip)
            h = sum(1 for e in range(NE) if X[e] != Y[e])
            if 0 < h <= max_ham:
                cands.append((h, a, b, flip))
cands.sort()
print(f"{len(cands)} images within hamming {max_ham}", flush=True)
best = cx
for h, a, b, flip in cands[:40]:
    Y = image(X, a, b, flip)
    total, col = recombine(X, Y)
    print(f"a={a} b={b} flip={flip} ham={h}: recombined {total}", flush=True)
    if total < best:
        best = total
        with open(f"{out_prefix}_best.txt", "w") as f:
            f.write(f"c nmono {best}\n")
            f.write("".join(map(str, col)) + "\n")
        print(f"IMPROVED {best} -> {out_prefix}_best.txt", flush=True)
print(f"done; best {best}", flush=True)

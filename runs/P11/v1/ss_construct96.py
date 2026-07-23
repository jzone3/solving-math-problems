#!/usr/bin/env python3
"""Explicit proper CW(96,36) via Schmidt-Smith (JCTA 2013), Theorem 6.8.

D = (1+g^8)B + (1-g^8)(c*A_i + d*C3) in Z[C_96], where g has order 16,
a has order 3,
  A1 = (1+g^2+g^6)(a-a^2),  A2 = (1-g^2-g^6)(a-a^2),
  B  = -1 + (1-g^4)(g+g^3) + (a+a^2)(1+g^4),  C3 = 1+a+a^2,
and (c,d) satisfying one of conditions (i)-(v).  Searches all c,d and both i,
checks ternary/weight/PAF/properness exactly, prints first witnesses.
"""
import json, sys
from itertools import product

N = 96
G = 6          # gamma: order 16 in Z_96
AL = 32        # alpha: order 3


def vec(*terms):
    """terms: (coef, position)"""
    v = [0] * N
    for c, p in terms:
        v[p % N] += c
    return v


def conv(u, w):
    r = [0] * N
    for i, a in enumerate(u):
        if a:
            for j, b in enumerate(w):
                if b:
                    r[(i + j) % N] += a * b
    return r


def add(u, w):
    return [a + b for a, b in zip(u, w)]


one = vec((1, 0))
g = lambda e: vec((1, (G * e) % N))
a_ = lambda e: vec((1, (AL * e) % N))

B = add(add(vec((-1, 0)), conv(add(one, vec((-1, G * 4))), add(g(1), g(3)))),
        conv(add(a_(1), a_(2)), add(one, g(4))))
A1 = conv(add(add(one, g(2)), g(6)), add(a_(1), vec((-1, AL * 2))))
A2 = conv(add(one, vec((-1, G * 2), (-1, G * 6))), add(a_(1), vec((-1, AL * 2))))
C3 = add(add(one, a_(1)), a_(2))

P = add(one, g(8))       # 1+g^8
Q = add(one, vec((-1, G * 8)))  # 1-g^8


def paf_ok(d):
    for s in range(1, N):
        if sum(d[i] * d[(i + s) % N] for i in range(N)) != 0:
            return False
    return True


def proper(d):
    sup = [i for i in range(N) if d[i]]
    for t in [2, 3]:  # prime divisors of 96
        m = N // t
        # support in a coset of subgroup of index t (subgroup = multiples of t)?
        if len({i % t for i in sup}) == 1:
            return False
    return True


hits = []
for i, Ai in ((1, A1), (2, A2)):
    for c, d in product(range(N), range(N)):
        shifted = add(conv(vec((1, c)), Ai), conv(vec((1, d)), C3))
        D = add(conv(P, B) if False else add(conv(P, B), [0]*N), conv(Q, shifted))
        if any(x not in (-1, 0, 1) for x in D):
            continue
        if sum(x * x for x in D) != 36:
            continue
        if not paf_ok(D):
            continue
        if not proper(D):
            continue
        hits.append((i, c, d, D))
        print(f"WITNESS i={i} c={c} d={d}")
        if len(hits) >= 3:
            break
    if hits:
        break

if hits:
    i, c, d, D = hits[0]
    json.dump({"n": N, "k": 36, "i": i, "c": c, "d": d, "row": D},
              open(sys.path[0] + "/witness_ss_96_36.json", "w"))
    print("row:", D)
else:
    print("no witness found")

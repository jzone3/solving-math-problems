#!/usr/bin/env python3
"""
P15 V4 phase 31: residue-level emission of Owens sec 3.11 (the prime 31).

Hole: modulus-36 congruence removed in the prime-3 work; restricted to
1 (mod 4) and 6 (mod 9), i.e. the cell 33 (mod 36).  Thirty-one sets:

  1..12 : 1, 2, 4, 8^, 3*1, 3*2, 3*4, 3*8^, 9*1, 9*2, 9*4, 9*8^
  13,14 : 27^(1,2), 27^(4,8^)
  15..17: three 5^ copies over sets 1-12, one being 5^(2,4,8^,1)
          (used in sec 3.16)
  18..20: three 7^ copies over sets 1-15 (only five entries needed on
          this branch; slot 6 = x)
  21    : C + 7^(5^(x,x,3*1,3*2),5^(x,x,3*4,3*8^),x,5^(x,x,9*1,9*2),
                 5^(x,x,9*4,9*8^),5^(x,x,27^(1,2),27^(4,8^))),
          C = 5^(27^(1,2),27^(4,8^),_,_)
  22..24: three 11^ copies (eight entries each; the two partial-5^
          entries of the text are under-determined -> placeholders)
  25,26 : two 13^ copies over sets 1-12 / 13-24
  27,28 : two 17^ copies, thirteen entries each, over sets 1-13/14-26
  29..31: one each of 19^ (sets 1-18), 23^ (sets 1-22), 29^ (sets 1-28)

Set 1 dropped (31 < 42); 31^ filled with sets 2..31.  "3*c" fixes the
mod-3 digit (hole is 0 mod 3), "9*c" the mod-9 cell (6,9); 27^ towers
over (6,9).
"""
import numpy as np
from canon import crt, ext

D2 = 6
E3 = 3
E5 = 2
E7 = 2
E1 = 1
E31 = 2

ONE = "ONE"
HOLE = (33, 36)
B9 = (6, 9)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    cells = [ext((1, 4), 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext((1, 4), 2, 0, D2)]


E8, E8T = e8up()

A1 = [(0, 1)]
A2 = [(1, 2)]
A4 = [(1, 4)]
T3 = lambda c: x2(c, 0, 3)
T9 = lambda c: x2(c, *B9)
S = {}
S[1], S[2], S[3], S[4] = A1, A2, A4, E8
S[5], S[6], S[7], S[8] = T3(A1), T3(A2), T3(A4), T3(E8)
S[9], S[10], S[11], S[12] = T9(A1), T9(A2), T9(A4), T9(E8)


def t27(c1, c2):
    """27^(a,b): tower over (6,9); level m modulus 27*3^(m-1)."""
    congs, tails = [], []
    for m in range(1, E3 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(B9, 3, t * 3 ** (m - 1), m)
            congs += [crt(c, mm, r, n) for (r, n) in inp
                      for (c, mm) in [cell]]
    tails.append(ext(B9, 3, 0, E3))
    return congs, tails


def tower(p, depth, contents, base=(0, 1), start=1):
    congs, tails = [], []
    for m in range(start, start + depth):
        for t, inp in enumerate(contents, start=1):
            cell = ext(base, p, t * p ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(base, p, 0, start + depth - 1))
    return congs, tails


def sets31():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("X1: 1", A1)
    add("X2: 2", A2)
    add("X3: 4", A4)
    add("X4: 8^", E8, E8T)
    for i, lab in ((5, "3*1"), (6, "3*2"), (7, "3*4")):
        add(f"X{i}: {lab}", S[i])
    add("X8: 3*8^", S[8], x2(E8T, 0, 3))
    for i, lab in ((9, "9*1"), (10, "9*2"), (11, "9*4")):
        add(f"X{i}: {lab}", S[i])
    add("X12: 9*8^", S[12], x2(E8T, *B9))
    c27a = t27(A1, A2)
    c27b = t27(A4, E8)
    add("X13: 27^(1,2)", *c27a)
    add("X14: 27^(4,8^)", *c27b)
    # X15-X17: three 5^ copies; X15 = 5^(2,4,8^,1) per Owens
    add("X15: 5^(2,4,8^,1)", *tower(5, E5, [S[2], S[3], S[4], S[1]]))
    add("X16: 5^(3*1,3*2,3*4,3*8^)",
        *tower(5, E5, [S[5], S[6], S[7], S[8]]))
    add("X17: 5^(9*1,9*2,9*4,9*8^)",
        *tower(5, E5, [S[9], S[10], S[11], S[12]]))
    sets = [s[1] for s in out]
    # X18-X20: three 7^ copies over sets 1-15 (slot 6 = x)
    for i in range(3):
        c7 = tower(7, E7, sets[5 * i:5 * i + 5] + [None])
        add(f"X{18 + i}: 7^(X{5*i+1}..X{5*i+5},x)", *c7)
    # X21: C + 7^(inner 5^ wrappers, slot 3 = x)
    C = tower(5, E5, [c27a[0], c27b[0], None, None])
    w = lambda a, b: tower(5, E5, [None, None, a, b])
    w1, w2 = w(S[5], S[6]), w(S[7], S[8])
    w3, w4 = w(S[9], S[10]), w(S[11], S[12])
    w5 = w(c27a[0], c27b[0])
    c7z = tower(7, E7, [w1[0], w2[0], None, w3[0], w4[0], w5[0]])
    add("X21: C+7^(5^(x,x,..) five ways)",
        C[0] + c7z[0],
        C[1] + c7z[1] + w1[1] + w2[1] + w3[1] + w4[1] + w5[1])
    sets = [s[1] for s in out]
    # X22-X24: three 11^ copies, eight entries, slots 9/10 x; copy 3's
    # partial-5^ entries under-determined -> placeholders
    add("X22: 11^(X1..X8,x,x)",
        *tower(11, E1, sets[:8] + [None, None]))
    add("X23: 11^(X9..X16,x,x)",
        *tower(11, E1, sets[8:16] + [None, None]))
    add("X24: 11^(X17..X21,x*5)",
        *tower(11, E1, sets[16:21] + [None] * 5))
    sets = [s[1] for s in out]
    # X25/X26: two 13^ copies
    add("X25: 13^(X1..X12)", *tower(13, E1, sets[:12]))
    add("X26: 13^(X13..X24)", *tower(13, E1, sets[12:24]))
    sets = [s[1] for s in out]
    # X27/X28: two 17^ copies, thirteen entries each
    add("X27: 17^(X1..X13,x*3)",
        *tower(17, E1, sets[:13] + [None] * 3))
    add("X28: 17^(X14..X26,x*3)",
        *tower(17, E1, sets[13:26] + [None] * 3))
    sets = [s[1] for s in out]
    # X29-X31: one each of 19^, 23^, 29^
    add("X29: 19^(X1..X18)", *tower(19, E1, sets[:18]))
    add("X30: 23^(X1..X22)", *tower(23, E1, sets[:22]))
    sets = [s[1] for s in out]
    add("X31: 29^(X1..X28)", *tower(29, E1, sets[:28]))
    return out


def emit311():
    """Sec 3.11: 31^ filled with sets X2..X31 (drop X1)."""
    congs, tails = [], []
    sets = sets31()[1:]
    assert len(sets) == 30
    for k in range(1, E31 + 1):
        for t in range(1, 31):
            cell = (t * 31 ** (k - 1) % 31 ** k, 31 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 31 ** E31))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310
    congs, tails = emit311()
    mods = [n for _, n in congs]
    print(f"sec3.11: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.11: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 7 * 31
    print("census window:", N)
    base = np.zeros(N, dtype=bool)
    for lab, cs in prevs:
        for r, n in cs:
            if N % n == 0:
                base[r % n::n] = True
    cov = base.copy()
    dropped = 0.0
    for r, n in congs + tails:
        if N % n == 0:
            cov[r % n::n] = True
        else:
            dropped += 1.0 / n
    idx = np.arange(N)
    B = idx % 36 == 33
    unc = idx[B & ~cov]
    print(f"36-hole uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 31:", sorted(Counter(unc % 31).items()))


if __name__ == "__main__":
    main()

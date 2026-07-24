#!/usr/bin/env python3
"""
P15 V4 phase 30: residue-level emission of Owens sec 3.10 (the prime 29).

Branch: 2 (mod 4), first input of a 3 (1 mod 3), second AND third
inputs of a 5 on the 4 hole -- two target cells (2,5) and (3,5).
Owens builds twenty-nine sets (dropping the bare 1, modulus 29 < 42)
and fills a 29^ with the twenty-eight:

  1..10 : 1, 2, 4, 8^, 3*1, 3*2, 3*4, 3*8^, 9^(1,2), 9^(4,8^)
  11..15: five 5-conjunction sets, each = 5*set(2i-1) on (2,5)
          u 5*set(2i) on (3,5)     [reconstruction: pairing in sequence]
  16    : 25^(1,2,4,8^)@(2,5) + 25^(3*1,3*2,3*4,3*8^)@(3,5)
  17    : 17^ over sets 1..16
  18..21: the four combined 7^ sets as written by Owens (slots 1,2
          bare = both 5-inputs; slot 3 = x; slots 4..6 5-scaled@(3,5));
          set 21 additionally carries 25^(9^(1,2),9^(4,8^),_,_)@(2,5)
  22..23: two 11^ copies over sets 1-10 / 11-20
  24    : 23^ over sets 1..21 (last slot x -- input count on this
          branch under-determined by the text)
  25..26: two 13^ copies over sets 1-12 / 13-24
  27..28: two 19^ copies, 13 inputs each (five apply to the whole
          4 hole per sec 3.8), over sets 1-13 / 14-26, slots 14-18 x
  29    : 7^(9^(1,2),9^(4,8^),x,5*9^(1,2),5*9^(4,8^),B),
          B = 17^ over the first sixteen sets

9^ towers anchor at the mod-3 cell (1,3); 8^ is the canonical chain
inside 2 (mod 4).
"""
import numpy as np
from canon import crt, ext

D2 = 6
E3 = 3
E5 = 2
E7 = 2
E9 = 3
E1 = 1
E29 = 2

ONE = "ONE"
BR2 = (2, 4)
B5A = (2, 5)          # second input of the 5
B5B = (3, 5)          # third input of the 5
B3 = (1, 3)           # first input of the 3


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    cells = [ext(BR2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(BR2, 2, 0, D2)]


E8, E8T = e8up()

A1 = [(0, 1)]
A2 = [(0, 2)]
A4 = [BR2]
T3 = lambda c: x2(c, *B3)
A3_1, A3_2, A3_4 = T3(A1), T3(A2), T3(A4)
A3_8 = T3(E8)


def nineup(c1, c2):
    """9^(a,b): tower over the mod-3 cell (1,3), level m mod 9*3^(m-1)."""
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(B3, 3, t * 3 ** (m - 1), m)
            congs += [crt(c, mm, r, n) for (r, n) in inp
                      for (c, mm) in [cell]]
    tails.append(ext(B3, 3, 0, E9))
    return congs, tails


N12, N12T = nineup(A1, A2)
N48, N48T = nineup(A4, E8)


def t25(contents, base, slots=None):
    """25^ tower anchored at 5-cell `base`; slots = digit positions
    (default 1..len)."""
    congs, tails = [], []
    if slots is None:
        slots = range(1, len(contents) + 1)
    for k in range(1, E5 + 1):
        for t, inp in zip(slots, contents):
            cell = ext(base, 5, t * 5 ** (k - 1), k)
            if inp is None:
                tails.append(cell)
            else:
                congs += [crt(c, m, r, n) for (r, n) in inp
                          for (c, m) in [cell]]
    tails.append(ext(base, 5, 0, E5))
    return congs, tails


def tower(p, depth, contents, base=(0, 1)):
    congs, tails = [], []
    for m in range(1, depth + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(base, p, t * p ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(base, p, 0, depth))
    return congs, tails


def sets29():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("W1: 1", A1)
    add("W2: 2", A2)
    add("W3: 4", A4)
    add("W4: 8^", E8, E8T)
    add("W5: 3*1", A3_1)
    add("W6: 3*2", A3_2)
    add("W7: 3*4", A3_4)
    add("W8: 3*8^", A3_8, x2(E8T, *B3))
    add("W9: 9^(1,2)", N12, N12T)
    add("W10: 9^(4,8^)", N48, N48T)
    ten = [(s[1], s[2]) for s in out]
    # W11-W15: 5-conjunctions, pairing the ten sets in sequence
    for i in range(5):
        ca, ta = ten[2 * i]
        cb, tb = ten[2 * i + 1]
        add(f"W{11 + i}: 5*set{2*i+1}@(2,5) u 5*set{2*i+2}@(3,5)",
            x2(ca, *B5A) + x2(cb, *B5B),
            x2(ta, *B5A) + x2(tb, *B5B))
    # W16: 25^(1,2,4,8^)@(2,5) + 25^(3*1,3*2,3*4,3*8^)@(3,5)
    p25a = t25([A1, A2, A4, E8], B5A)
    p25b = t25([A3_1, A3_2, A3_4, A3_8], B5B)
    add("W16: 25^(1,2,4,8^)@(2,5)+25^(3*...)@(3,5)",
        p25a[0] + p25b[0], p25a[1] + p25b[1])
    # W17: 17^ over sets 1..16
    add("W17: 17^(W1..W16)",
        *tower(17, E1, [s[1] for s in out[:16]]))
    # W18-W20: combined 7^ sets; slots 1,2 bare, slot 3 x,
    # slots 4-6 5-scaled at (3,5)
    F = lambda c: x2(c, *B5B)
    s18 = tower(7, E7, [A1, A2, None, F(A1), F(A2), F(A4)])
    add("W18: 7^(1,2,x,5*1,5*2,5*4)", *s18)
    s19 = tower(7, E7, [A4, E8, None, F(E8), F(A3_1), F(A3_2)])
    add("W19: 7^(4,8^,x,5*8^,5*3*1,5*3*2)", *s19)
    in25 = t25([A1, A2, A4, E8], B5B)
    s20 = tower(7, E7, [A3_1, A3_2, None, F(A3_4), F(A3_8), in25[0]])
    add("W20: 7^(3*1,3*2,x,5*3*4,5*3*8^,25^(1,2,4,8^)@(3,5))",
        s20[0], s20[1] + in25[1])
    # W21: 25^(9^(1,2),9^(4,8^),_,_)@(2,5)
    #      + 7^(3*4,3*8^,x,25^(x,x,3*1,3*2),25^(x,x,3*4,3*8^),
    #            25^(x,x,9^(1,2),9^(4,8^))) with inner 25^ @(3,5)
    r25 = t25([N12, N48, None, None], B5A)
    q1 = t25([None, None, A3_1, A3_2], B5B)
    q2 = t25([None, None, A3_4, A3_8], B5B)
    q3 = t25([None, None, N12, N48], B5B)
    s21 = tower(7, E7, [A3_4, A3_8, None, q1[0], q2[0], q3[0]])
    add("W21: 25^(9^,9^,_,_)@(2,5)+7^(3*4,3*8^,x,25^x3)",
        r25[0] + s21[0], r25[1] + s21[1] + q1[1] + q2[1] + q3[1])
    allsets = [s[1] for s in out]
    # W22/W23: two 11^ copies
    add("W22: 11^(W1..W10)", *tower(11, E1, allsets[:10]))
    add("W23: 11^(W11..W20)", *tower(11, E1, allsets[10:20]))
    # W24: 23^ over W1..W21, last slot x (under-determined input count)
    add("W24: 23^(W1..W21,x)",
        *tower(23, E1, allsets[:21] + [None]))
    allsets = [s[1] for s in out]
    # W25/W26: two 13^ copies
    add("W25: 13^(W1..W12)", *tower(13, E1, allsets[:12]))
    add("W26: 13^(W13..W24)", *tower(13, E1, allsets[12:24]))
    # W27/W28: two 19^ copies, 13 inputs each, slots 14-18 x (sec 3.8)
    allsets = [s[1] for s in out]
    add("W27: 19^(W1..W13,x*5)",
        *tower(19, E1, allsets[:13] + [None] * 5))
    add("W28: 19^(W14..W26,x*5)",
        *tower(19, E1, allsets[13:26] + [None] * 5))
    # W29: 7^(9^(1,2),9^(4,8^),x,5*9^(1,2),5*9^(4,8^),B)
    B17 = tower(17, E1, [s[1] for s in out[:16]])
    s29 = tower(7, E7, [N12, N48, None, F(N12), F(N48), B17[0]])
    add("W29: 7^(9^,9^,x,5*9^,5*9^,17^(W1..W16))",
        s29[0], s29[1] + B17[1])
    return out


def emit310():
    """Sec 3.10: 29^ filled with sets W2..W29 (drop W1)."""
    congs, tails = [], []
    sets = sets29()[1:]
    assert len(sets) == 28
    for k in range(1, E29 + 1):
        for t in range(1, 29):
            cell = (t * 29 ** (k - 1) % 29 ** k, 29 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 29 ** E29))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38, emit39
    congs, tails = emit310()
    mods = [n for _, n in congs]
    print(f"sec3.10: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.10: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 7 * 29
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
    B = (idx % 4 == 2) & (idx % 3 == 1) & ((idx % 5 == 2) | (idx % 5 == 3))
    unc = idx[B & ~cov]
    print(f"target cells uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 29:", sorted(Counter(unc % 29).items()))


if __name__ == "__main__":
    main()

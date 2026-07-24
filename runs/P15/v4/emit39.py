#!/usr/bin/env python3
"""
P15 V4 phase 29: residue-level emission of Owens sec 3.9 (the prime 23)
= Nielsen 4.9 on the 24-hole (coset 17 mod 24 reopened by removing the
modulus-24 congruence), with Owens's swap 5^(1,2,4,8) -> 5^(2,1,4,8).

Twenty-two inputs of 23^:
  1-16: 2, 4, 8, 16^, 3*1, 3*2, 3*4, 3*8, 3*16^, 9^(1,2), 9^(4,8),
        5^(2,1,4,8) [Owens swap], 5^(16^,3*1,3*2,3*4),
        5^(3*8,3*16^,9^(1,2),9^(4,8)), 7^(1,2,4,8,16^,3*1),
        7^(3*2,3*4,3*8,3*16^,5^(2,1,4,8),5^(16^,3*1,3*2,3*4))
  17  : 9^(16^,_) + 7^(9^(x,1),9^(x,2),9^(x,4),9^(x,8),9^(x,16^),
                        5^(9^(x,1),9^(x,2),9^(x,4),9^(x,8)))
  18-20: one each of 13^, 17^, 19^ over previous sets (with 1 as needed)
  21-22: two 11^ copies over the twenty 11-free sets.

Atoms are absolute cells containing the hole (17 mod 24: 1 mod 2/4/8,
2 mod 3); "8" is the single cell (1,8) and 16^ its chain; 9^ towers
anchor at the mod-3 cell (2,3).
"""
import numpy as np
from canon import crt, ext

D2 = 6
E3 = 3
E5 = 2
E7 = 2
E9 = 3
E11 = 1
EBIG = 1
E23 = 2

ONE = "ONE"
HOLE = (17, 24)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e16up():
    cells = [ext((1, 8), 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext((1, 8), 2, 0, D2)]


E16, E16T = e16up()

A1 = [(0, 1)]
A2 = [(1, 2)]
A4 = [(1, 4)]
A8 = [(1, 8)]
T3 = lambda c: x2(c, 2, 3)          # 3*c on the hole's 3-cell 2 (mod 3)
A3_1, A3_2, A3_4, A3_8 = T3(A1), T3(A2), T3(A4), T3(A8)
A3_16 = T3(E16)


def nineup(c1, c2, base=(2, 3)):
    # 9^ = tower over the hole's mod-3 cell (the hole 17 mod 24 fixes
    # only mod 3 = 2); level m has modulus 9*3^(m-1)
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(base, 3, t * 3 ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(base, 3, 0, E9))
    return congs, tails


N9_12, N9_12T = nineup(ONE, A2)
N9_48, N9_48T = nineup(A4, A8)


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


def five(contents):
    return tower(5, E5, contents)


def seven(contents):
    return tower(7, E7, contents)


def sets22():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("V1: 2", A2)
    add("V2: 4", A4)
    add("V3: 8", A8)
    add("V4: 16^", E16, E16T)
    add("V5: 3*1", A3_1)
    add("V6: 3*2", A3_2)
    add("V7: 3*4", A3_4)
    add("V8: 3*8", A3_8)
    add("V9: 3*16^", A3_16, x2(E16T, 2, 3))
    add("V10: 9^(1,2)", N9_12, N9_12T)
    add("V11: 9^(4,8)", N9_48, N9_48T)
    f12 = five([A2, A1, A4, A8])                       # Owens swap
    add("V12: 5^(2,1,4,8)", *f12)
    f13 = five([E16, A3_1, A3_2, A3_4])
    add("V13: 5^(16^,3*1,3*2,3*4)", f13[0], f13[1] + E16T)
    f14 = five([A3_8, A3_16, N9_12, N9_48])
    add("V14: 5^(3*8,3*16^,9^(1,2),9^(4,8))",
        f14[0], f14[1] + N9_12T + N9_48T)
    s7a = seven([A1, A2, A4, A8, E16, A3_1])
    add("V15: 7^(1,2,4,8,16^,3*1)", *s7a)
    s7b = seven([A3_2, A3_4, A3_8, A3_16, f12[0], f13[0]])
    add("V16: 7^(3*2,3*4,3*8,3*16^,5^a,5^b)", *s7b)
    # V17: reserve 9^(16^,_) + 7^(9^(x,c)... , 5^(9^(x,c)...))
    r9 = nineup(E16, None)
    n9x1 = nineup(None, A1)
    n9x2 = nineup(None, A2)
    n9x4 = nineup(None, A4)
    n9x8 = nineup(None, A8)
    n9x16 = nineup(None, E16)
    f17 = five([n9x1[0], n9x2[0], n9x4[0], n9x8[0]])
    s7c = seven([n9x1[0], n9x2[0], n9x4[0], n9x8[0], n9x16[0], f17[0]])
    add("V17: 9^(16^,_)+7^(9^(x,*)...,5^(9^(x,*)...))",
        r9[0] + s7c[0],
        r9[1] + s7c[1] + f17[1] + n9x1[1] + n9x2[1] + n9x4[1]
        + n9x8[1] + n9x16[1])
    prev = [s[1] for s in out]
    # V18-V20: 13^, 17^, 19^ over previous sets (with 1 as needed)
    add("V18: 13^(1,V1..V11)",
        *tower(13, EBIG, [A1] + prev[:11]))
    add("V19: 17^(1,V1..V15)",
        *tower(17, EBIG, [A1] + prev[:15]))
    add("V20: 19^(1,V1..V17)",
        *tower(19, EBIG, [A1] + prev[:17]))
    all20 = [s[1] for s in out]
    # V21/V22: two 11^ copies over the twenty 11-free sets
    add("V21: 11^(V1..V10)", *tower(11, E11, all20[:10]))
    add("V22: 11^(V11..V20)", *tower(11, E11, all20[10:20]))
    return out


def emit39():
    congs, tails = [], []
    sets = sets22()
    assert len(sets) == 22
    for k in range(1, E23 + 1):
        for t in range(1, 23):
            cell = (t * 23 ** (k - 1) % 23 ** k, 23 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 23 ** E23))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    congs, tails = emit39()
    mods = [n for _, n in congs]
    print(f"sec3.9: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.9: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 7 * 23
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
    B = idx % 24 == 17
    unc = idx[B & ~cov]
    print(f"24-hole uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 23:", sorted(Counter(unc % 23).items()))


if __name__ == "__main__":
    main()

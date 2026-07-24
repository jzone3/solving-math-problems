#!/usr/bin/env python3
"""
P15 V4 phase 37: residue-level emission of Owens sec 3.17 (the prime 59).

Hole: last (third) 3-input in the first 5-input on the 8 hole --
branch (4 mod 8) n (1 mod 5) n (0 mod 3).  Fifty-eight sets:

  1..5  : 1, 2, 4, 8, 16^
  6..10 : 3*set(1..5)                (mod-3 cell (0,3))
  11,12 : 9^(1,2), 9^(4,8)           (towers over (0,3))
  13..24: 5*set(1..12) @ (1,5)
  25    : 5*9^(16^,_) + 9^(_,16^)    (the half-filled reserve 9^)
  26..28: three 25^ over sets 1-4/5-8/9-12
  29    : 29^;  30: 23^
  31..40: ten 7^ copies at three inputs
  41    : 41^;  42..45: four 11^;  46: 43^;  47: 47^;  48: 37^
  49..51: three 17^;  52..55: four 13^;  56..58: three 19^ at thirteen

59^ filled with all fifty-eight.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
E59 = 2

ONE = "ONE"
B5 = (1, 5)
B3 = (0, 3)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e16up():
    cells = [ext((4, 8), 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext((4, 8), 2, 0, D2)]


E16, E16T = e16up()
A1, A2, A4, A8 = [(0, 1)], [(0, 2)], [(0, 4)], [(4, 8)]


def nineup(c1, c2):
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(B3, 3, t * 3 ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(B3, 3, 0, E9))
    return congs, tails


def t25(contents):
    congs, tails = [], []
    for k in range(1, E5 + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(B5, 5, t * 5 ** (k - 1), k)
            congs += [crt(c, m, r, n) for (r, n) in inp
                      for (c, m) in [cell]]
    tails.append(ext(B5, 5, 0, E5))
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


def sets59():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("T1: 1", A1)
    add("T2: 2", A2)
    add("T3: 4", A4)
    add("T4: 8", A8)
    add("T5: 16^", E16, E16T)
    five = [(s[1], s[2]) for s in out]
    for i, (cc, tt) in enumerate(five, start=1):
        add(f"T{5 + i}: 3*T{i}", x2(cc, *B3), x2(tt, *B3))
    add("T11: 9^(1,2)", *nineup(A1, A2))
    add("T12: 9^(4,8)", *nineup(A4, A8))
    twelve = [(s[1], s[2]) for s in out[:12]]
    for i, (cc, tt) in enumerate(twelve, start=1):
        add(f"T{12 + i}: 5*T{i}", x2(cc, *B5), x2(tt, *B5))
    ra = nineup(E16, None)
    rb = nineup(None, E16)
    add("T25: 5*9^(16^,_)+9^(_,16^)",
        x2(ra[0], *B5) + rb[0], x2(ra[1], *B5) + rb[1])
    sets = [s[1] for s in out]
    add("T26: 25^(T1..T4)", *t25(sets[:4]))
    add("T27: 25^(T5..T8)", *t25(sets[4:8]))
    add("T28: 25^(T9..T12)", *t25(sets[8:12]))
    sets = [s[1] for s in out]
    add("T29: 29^(T1..T28)", *tower(29, E1, sets[:28]))
    add("T30: 23^(T1..T22)", *tower(23, E1, sets[:22]))
    sets = [s[1] for s in out]
    for i in range(10):
        add(f"T{31 + i}: 7^(3 inputs,x*3)",
            *tower(7, E7, sets[3 * i:3 * i + 3] + [None] * 3))
    sets = [s[1] for s in out]
    add("T41: 41^(T1..T40)", *tower(41, E1, sets[:40]))
    sets = [s[1] for s in out]
    add("T42: 11^(T1..T10)", *tower(11, E1, sets[:10]))
    add("T43: 11^(T11..T20)", *tower(11, E1, sets[10:20]))
    add("T44: 11^(T21..T30)", *tower(11, E1, sets[20:30]))
    add("T45: 11^(T31..T40)", *tower(11, E1, sets[30:40]))
    sets = [s[1] for s in out]
    add("T46: 43^(T1..T42)", *tower(43, E1, sets[:42]))
    sets = [s[1] for s in out]
    add("T47: 47^(T1..T46)", *tower(47, E1, sets[:46]))
    sets = [s[1] for s in out]
    add("T48: 37^(T1..T36)", *tower(37, E1, sets[:36]))
    sets = [s[1] for s in out]
    add("T49: 17^(T1..T16)", *tower(17, E1, sets[:16]))
    add("T50: 17^(T17..T32)", *tower(17, E1, sets[16:32]))
    add("T51: 17^(T33..T48)", *tower(17, E1, sets[32:48]))
    sets = [s[1] for s in out]
    add("T52: 13^(T1..T12)", *tower(13, E1, sets[:12]))
    add("T53: 13^(T13..T24)", *tower(13, E1, sets[12:24]))
    add("T54: 13^(T25..T36)", *tower(13, E1, sets[24:36]))
    add("T55: 13^(T37..T48)", *tower(13, E1, sets[36:48]))
    sets = [s[1] for s in out]
    add("T56: 19^(T1..T13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("T57: 19^(T14..T26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    add("T58: 19^(T27..T39,x*5)", *tower(19, E1, sets[26:39] + [None] * 5))
    return out


def emit317():
    """Sec 3.17: 59^ filled with all fifty-eight sets."""
    congs, tails = [], []
    sets = sets59()
    assert len(sets) == 58
    for k in range(1, E59 + 1):
        for t in range(1, 59):
            cell = (t * 59 ** (k - 1) % 59 ** k, 59 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 59 ** E59))
    return congs, tails


def main():
    congs, tails = emit317()
    mods = [n for _, n in congs]
    print(f"sec3.17: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.17: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    import emit315, emit316
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0]),
             ("sec3.11", emit311.emit311()[0]),
             ("sec3.12", emit312.emit312()[0]),
             ("sec3.13", emit313.emit313()[0]),
             ("sec3.14", emit314.emit314()[0]),
             ("sec3.15", emit315.emit315()[0]),
             ("sec3.16", emit316.emit316()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 59
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
    B = (idx % 8 == 4) & (idx % 5 == 1) & (idx % 3 == 0)
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
P15 V4 phase 36: residue-level emission of Owens sec 3.16 (the prime 53).

Hole: the last (fifth) input of the 5 on the 4 hole -- branch
(2 mod 4) n (0 mod 5), one hole mod 25 (the text's "one hole mod
25*3^*4" is OCR-garbled; the 25-cell (5,25) with free 3-digit is the
reconstruction, marked as such).  Fifty-two sets:

  1..4  : 1, 2, 4, 8^
  5..8  : 3*set(1..4)
  9..16 : 5*set(1..8)  @ (0,5)
  17..24: 25*set(1..8) @ (5,25)
  25,26 : two 125^ copies over sets 1-4 / 5-8
  27,28 : two 19^ at thirteen inputs
  29    : 29^;  30: 31^ at twenty-nine inputs (sec 3.11 carryover:
          the reserved 5^(2,4,8^,1))
  31..36: six 7^ copies, five inputs (third input covered here)
  37..39: three 13^;  40: 37^;  41..44: four 11^;  45: 41^;  46: 43^
  47    : 47^;  48,49: two 23^;  50..52: three 17^

53^ filled with all fifty-two (53 >= 42, nothing dropped).
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E1 = 1
E53 = 2

ONE = "ONE"
B2 = (2, 4)
B5 = (0, 5)
B25 = (5, 25)
B3 = (0, 3)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    cells = [ext(B2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(B2, 2, 0, D2)]


E8, E8T = e8up()
A1, A2, A4 = [(0, 1)], [(0, 2)], [B2]


def t125(contents):
    """125^ tower over the 25-cell (5,25): level k modulus 125*5^(k-1)."""
    congs, tails = [], []
    for k in range(1, E5 + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(B25, 5, t * 5 ** (k - 1), k)
            congs += [crt(c, m, r, n) for (r, n) in inp
                      for (c, m) in [cell]]
    tails.append(ext(B25, 5, 0, E5))
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


def sets53():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("S1: 1", A1)
    add("S2: 2", A2)
    add("S3: 4", A4)
    add("S4: 8^", E8, E8T)
    four = [(s[1], s[2]) for s in out]
    for i, (cc, tt) in enumerate(four, start=1):
        add(f"S{4 + i}: 3*S{i}", x2(cc, *B3), x2(tt, *B3))
    eight = [(s[1], s[2]) for s in out[:8]]
    for i, (cc, tt) in enumerate(eight, start=1):
        add(f"S{8 + i}: 5*S{i}", x2(cc, *B5), x2(tt, *B5))
    for i, (cc, tt) in enumerate(eight, start=1):
        add(f"S{16 + i}: 25*S{i}", x2(cc, *B25), x2(tt, *B25))
    sets = [s[1] for s in out]
    add("S25: 125^(S1..S4)", *t125(sets[:4]))
    add("S26: 125^(S5..S8)", *t125(sets[4:8]))
    sets = [s[1] for s in out]
    add("S27: 19^(S1..S13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("S28: 19^(S14..S26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    sets = [s[1] for s in out]
    add("S29: 29^(S1..S28)", *tower(29, E1, sets[:28]))
    add("S30: 31^(S1..S29,x)", *tower(31, E1, sets[:29] + [None]))
    sets = [s[1] for s in out]
    for i in range(6):
        g = sets[5 * i:5 * i + 5]
        add(f"S{31 + i}: 7^(.,.,x,.,.,.)",
            *tower(7, E7, g[:2] + [None] + g[2:]))
    sets = [s[1] for s in out]
    add("S37: 13^(S1..S12)", *tower(13, E1, sets[:12]))
    add("S38: 13^(S13..S24)", *tower(13, E1, sets[12:24]))
    add("S39: 13^(S25..S36)", *tower(13, E1, sets[24:36]))
    sets = [s[1] for s in out]
    add("S40: 37^(S1..S36)", *tower(37, E1, sets[:36]))
    sets = [s[1] for s in out]
    add("S41: 11^(S1..S10)", *tower(11, E1, sets[:10]))
    add("S42: 11^(S11..S20)", *tower(11, E1, sets[10:20]))
    add("S43: 11^(S21..S30)", *tower(11, E1, sets[20:30]))
    add("S44: 11^(S31..S40)", *tower(11, E1, sets[30:40]))
    sets = [s[1] for s in out]
    add("S45: 41^(S1..S40)", *tower(41, E1, sets[:40]))
    sets = [s[1] for s in out]
    add("S46: 43^(S1..S42)", *tower(43, E1, sets[:42]))
    sets = [s[1] for s in out]
    add("S47: 47^(S1..S46)", *tower(47, E1, sets[:46]))
    sets = [s[1] for s in out]
    add("S48: 23^(S1..S22)", *tower(23, E1, sets[:22]))
    add("S49: 23^(S23..S44)", *tower(23, E1, sets[22:44]))
    sets = [s[1] for s in out]
    add("S50: 17^(S1..S16)", *tower(17, E1, sets[:16]))
    add("S51: 17^(S17..S32)", *tower(17, E1, sets[16:32]))
    add("S52: 17^(S33..S48)", *tower(17, E1, sets[32:48]))
    return out


def emit316():
    """Sec 3.16: 53^ filled with all fifty-two sets."""
    congs, tails = [], []
    sets = sets53()
    assert len(sets) == 52
    for k in range(1, E53 + 1):
        for t in range(1, 53):
            cell = (t * 53 ** (k - 1) % 53 ** k, 53 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 53 ** E53))
    return congs, tails


def main():
    congs, tails = emit316()
    mods = [n for _, n in congs]
    print(f"sec3.16: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.16: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314, emit315
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0]),
             ("sec3.11", emit311.emit311()[0]),
             ("sec3.12", emit312.emit312()[0]),
             ("sec3.13", emit313.emit313()[0]),
             ("sec3.14", emit314.emit314()[0]),
             ("sec3.15", emit315.emit315()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 3 * 53
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
    B = (idx % 4 == 2) & (idx % 25 == 5)
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()

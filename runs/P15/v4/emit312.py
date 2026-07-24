#!/usr/bin/env python3
"""
P15 V4 phase 32: residue-level emission of Owens sec 3.12 (the prime 37).

Hole: first input of the 5 on the 8 hole = (4 mod 8) n (1 mod 5)
= 36 (mod 40), restricted to the first two inputs of a 3 (the third
is filled in sec 3.16 with the prime 53).  Thirty-seven sets:

  1..5  : 1, 2, 4, 8, 16^        (8 = the single cell (4,8))
  6..9  : 3(1,2), 3(4,8), 3(3^(1,2),3^(4,8)), 3(16^,_)+5*3(_,16^)
  10..17: 5*set_i for the first eight sets
  18,19 : 25^(1,2,4,8), 25^(16^,3(1,2)...)  -> two 25^ copies over
          sets 1-4 / 5-8, anchored at (1,5)
  20..25: six 7^ copies, three inputs each (sec 3.4 covers the rest
          on this branch), over sets 1-18
  26,27 : two 13^ copies over sets 1-12 / 13-24
  28,29 : two 19^ copies, thirteen inputs each (sec 3.8)
  30    : 29^ over sets 1-28
  31    : 31^ over sets 1-30
  32..34: three 11^ copies over sets 1-10/11-20/21-30
  35,36 : two 17^ copies over sets 1-16/17-32
  37    : 23^ over sets 1-22

Set 1 dropped (37 < 42); 37^ filled with sets 2..37.  3(a,b) puts a
on the 3-cell (1,3) and b on (2,3); inner 3^ towers go deeper over
those cells.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E3 = 3
E5 = 2
E7 = 2
E1 = 1
E37 = 2

ONE = "ONE"
B5 = (1, 5)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e16up():
    cells = [ext((4, 8), 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext((4, 8), 2, 0, D2)]


E16, E16T = e16up()

A1 = [(0, 1)]
A2 = [(0, 2)]
A4 = [(0, 4)]
A8 = [(4, 8)]


def three(a, b):
    """3(a,b): a on the 3-cell (1,3), b on (2,3)."""
    congs, tails = [], []
    for cell, inp in (((1, 3), a), ((2, 3), b)):
        if inp is None:
            tails.append(cell)
        else:
            congs += [crt(c, m, *cell) for (c, m) in inp]
    return congs, tails


def t3up(base, c1, c2):
    """3^(a,b) over the 3-cell `base`: level m modulus 9*3^(m-1)."""
    congs, tails = [], []
    for m in range(1, E3 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(base, 3, t * 3 ** (m - 1), m)
            congs += [crt(c, mm, r, n) for (r, n) in inp
                      for (c, mm) in [cell]]
    tails.append(ext(base, 3, 0, E3))
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


def sets37():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("Y1: 1", A1)
    add("Y2: 2", A2)
    add("Y3: 4", A4)
    add("Y4: 8", A8)
    add("Y5: 16^", E16, E16T)
    add("Y6: 3(1,2)", *three(A1, A2))
    add("Y7: 3(4,8)", *three(A4, A8))
    i31 = t3up((1, 3), A1, A2)
    i32 = t3up((2, 3), A4, A8)
    add("Y8: 3(3^(1,2),3^(4,8))", i31[0] + i32[0], i31[1] + i32[1])
    n1 = three(E16, None)
    n2 = three(None, E16)
    add("Y9: 3(16^,_)+5*3(_,16^)",
        n1[0] + x2(n2[0], *B5),
        n1[1] + x2(E16T, 1, 3) + x2(n2[1], *B5)
        + x2(x2(E16T, 2, 3), *B5))
    first8 = [(s[1], s[2]) for s in out[:8]]
    for i, (cc, tt) in enumerate(first8, start=1):
        add(f"Y{9 + i}: 5*Y{i}", x2(cc, *B5), x2(tt, *B5))
    # Y18/Y19: two 25^ copies over sets 1-4 / 5-8, anchored (1,5)
    sets = [s[1] for s in out]

    def t25(contents):
        congs, tails = [], []
        for k in range(1, E5 + 1):
            for t, inp in enumerate(contents, start=1):
                cell = ext(B5, 5, t * 5 ** (k - 1), k)
                congs += [crt(c, m, r, n) for (r, n) in inp
                          for (c, m) in [cell]]
        tails.append(ext(B5, 5, 0, E5))
        return congs, tails

    add("Y18: 25^(Y1..Y4)", *t25(sets[:4]))
    add("Y19: 25^(Y5..Y8)", *t25(sets[4:8]))
    sets = [s[1] for s in out]
    # Y20-Y25: six 7^ copies, three inputs each (slots 4-6 covered by
    # sec 3.4 on this branch)
    for i in range(6):
        c7 = tower(7, E7, sets[3 * i:3 * i + 3] + [None] * 3)
        add(f"Y{20 + i}: 7^(Y{3*i+1}..Y{3*i+3},x,x,x)", *c7)
    sets = [s[1] for s in out]
    # Y26/Y27: two 13^ copies
    add("Y26: 13^(Y1..Y12)", *tower(13, E1, sets[:12]))
    add("Y27: 13^(Y13..Y24)", *tower(13, E1, sets[12:24]))
    sets = [s[1] for s in out]
    # Y28/Y29: two 19^ copies, thirteen inputs each
    add("Y28: 19^(Y1..Y13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("Y29: 19^(Y14..Y26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    sets = [s[1] for s in out]
    add("Y30: 29^(Y1..Y28)", *tower(29, E1, sets[:28]))
    sets = [s[1] for s in out]
    add("Y31: 31^(Y1..Y30)", *tower(31, E1, sets[:30]))
    sets = [s[1] for s in out]
    # Y32-Y34: three 11^ copies
    add("Y32: 11^(Y1..Y10)", *tower(11, E1, sets[:10]))
    add("Y33: 11^(Y11..Y20)", *tower(11, E1, sets[10:20]))
    add("Y34: 11^(Y21..Y30)", *tower(11, E1, sets[20:30]))
    sets = [s[1] for s in out]
    # Y35/Y36: two 17^ copies
    add("Y35: 17^(Y1..Y16)", *tower(17, E1, sets[:16]))
    add("Y36: 17^(Y17..Y32)", *tower(17, E1, sets[16:32]))
    sets = [s[1] for s in out]
    add("Y37: 23^(Y1..Y22)", *tower(23, E1, sets[:22]))
    return out


def emit312():
    """Sec 3.12: 37^ filled with sets Y2..Y37 (drop Y1)."""
    congs, tails = [], []
    sets = sets37()[1:]
    assert len(sets) == 36
    for k in range(1, E37 + 1):
        for t in range(1, 37):
            cell = (t * 37 ** (k - 1) % 37 ** k, 37 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 37 ** E37))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311
    congs, tails = emit312()
    mods = [n for _, n in congs]
    print(f"sec3.12: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.12: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0]),
             ("sec3.11", emit311.emit311()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 37
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
    B = ((idx % 8 == 4) & (idx % 5 == 1)
         & ((idx % 3 == 1) | (idx % 3 == 2)))
    unc = idx[B & ~cov]
    print(f"target cells uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 37:", sorted(Counter(unc % 37).items()))


if __name__ == "__main__":
    main()

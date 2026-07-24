#!/usr/bin/env python3
"""
P15 V4 phase 33: residue-level emission of Owens sec 3.13 (the prime 41).

Hole: second input of a 3 (2 mod 3) in the second input of a 5
(2 mod 5) on the 4 hole (2 mod 4) -- the fourth empty hole of Fig 3.9.

Sets per the text: 1,2,4,8^; with 3 and 9^ -> ten sets; an 11^ and a
13^ (eleven inputs on this branch); twelve 5*copies and three 25^
copies (27 sets); two 19^ at thirteen inputs; a 29^; six 7^ copies at
five inputs; a 31^; two 17^; a 37^; 23^ copies at nineteen inputs
(sec 3.9's 5^(2,1,4,8) swap).  Owens's count is forty-one sets; the
sequential reconstruction below yields forty-two, so the last 23^
copy is left unused when filling the forty 41^-slots (drop set 1,
41 < 42) -- noted as reconstruction slack.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
E41 = 2

ONE = "ONE"
B2 = (2, 4)
B5 = (2, 5)
B3 = (2, 3)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    cells = [ext(B2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(B2, 2, 0, D2)]


E8, E8T = e8up()
A1, A2, A4 = [(0, 1)], [(0, 2)], [B2]
T3 = lambda c: x2(c, *B3)


def nineup(c1, c2):
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(B3, 3, t * 3 ** (m - 1), m)
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


def sets41():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("Z1: 1", A1)
    add("Z2: 2", A2)
    add("Z3: 4", A4)
    add("Z4: 8^", E8, E8T)
    add("Z5: 3*1", T3(A1))
    add("Z6: 3*2", T3(A2))
    add("Z7: 3*4", T3(A4))
    add("Z8: 3*8^", T3(E8), x2(E8T, *B3))
    n12 = nineup(A1, A2)
    n48 = nineup(A4, E8)
    add("Z9: 9^(1,2)", *n12)
    add("Z10: 9^(4,8^)", *n48)
    sets = [s[1] for s in out]
    add("Z11: 11^(Z1..Z10)", *tower(11, E1, sets[:10]))
    sets = [s[1] for s in out]
    add("Z12: 13^(Z1..Z11,x*2)",
        *tower(13, E1, sets[:11] + [None] * 2))
    twelve = [(s[1], s[2]) for s in out[:12]]
    for i, (cc, tt) in enumerate(twelve, start=1):
        add(f"Z{12 + i}: 5*Z{i}", x2(cc, *B5), x2(tt, *B5))
    sets = [s[1] for s in out]
    add("Z25: 25^(Z1..Z4)", *t25(sets[:4]))
    add("Z26: 25^(Z5..Z8)", *t25(sets[4:8]))
    add("Z27: 25^(Z9..Z12)", *t25(sets[8:12]))
    sets = [s[1] for s in out]
    add("Z28: 19^(Z1..Z13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("Z29: 19^(Z14..Z26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    sets = [s[1] for s in out]
    add("Z30: 29^(Z1..Z28)", *tower(29, E1, sets[:28]))
    sets = [s[1] for s in out]
    for i in range(6):
        add(f"Z{31 + i}: 7^(Z{5*i+1}..Z{5*i+5},x)",
            *tower(7, E7, sets[5 * i:5 * i + 5] + [None]))
    sets = [s[1] for s in out]
    add("Z37: 31^(Z1..Z30)", *tower(31, E1, sets[:30]))
    sets = [s[1] for s in out]
    add("Z38: 17^(Z1..Z16)", *tower(17, E1, sets[:16]))
    add("Z39: 17^(Z17..Z32)", *tower(17, E1, sets[16:32]))
    sets = [s[1] for s in out]
    add("Z40: 37^(Z1..Z36)", *tower(37, E1, sets[:36]))
    sets = [s[1] for s in out]
    add("Z41: 23^(Z1..Z19,x*3)",
        *tower(23, E1, sets[:19] + [None] * 3))
    add("Z42: 23^(Z20..Z38,x*3)",
        *tower(23, E1, sets[19:38] + [None] * 3))
    return out


def emit313():
    """Sec 3.13: 41^ filled with sets Z2..Z41 (drop Z1; Z42 spare)."""
    congs, tails = [], []
    sets = sets41()[1:41]
    assert len(sets) == 40
    for k in range(1, E41 + 1):
        for t in range(1, 41):
            cell = (t * 41 ** (k - 1) % 41 ** k, 41 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 41 ** E41))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312
    congs, tails = emit313()
    mods = [n for _, n in congs]
    print(f"sec3.13: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.13: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0]),
             ("sec3.11", emit311.emit311()[0]),
             ("sec3.12", emit312.emit312()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 41
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
    B = (idx % 4 == 2) & (idx % 5 == 2) & (idx % 3 == 2)
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 41:", sorted(Counter(unc % 41).items())[:12])


if __name__ == "__main__":
    main()

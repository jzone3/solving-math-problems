#!/usr/bin/env python3
"""
P15 V4 phase 35: residue-level emission of Owens sec 3.15 (the prime 47).

Hole: FIRST 3-input (1 mod 3) of the fourth 5-input (4 mod 5) on the
4 hole (2 mod 4).  Per the text: same twenty-five sets as sec 3.14
(3/9^ now over 1 mod 3); 7^ needs four inputs here, one of which only
needs a 25 -- the 25^ breaks into five pieces (four level-1 25*c
congruences + the deeper tower) giving twenty-nine items to fill
seven 7^ copies (sets 26..32); then two 17^, a 29^, a 31^, three
13^, three 19^ at thirteen inputs, a 41^, a 43^, and two 23^ --
forty-six sets filling the 47^ (47 >= 42: nothing dropped).
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
E47 = 2

ONE = "ONE"
B2 = (2, 4)
B5 = (4, 5)
B3 = (1, 3)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    cells = [ext(B2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(B2, 2, 0, D2)]


E8, E8T = e8up()
A1, A2, A4 = [(0, 1)], [(0, 2)], [B2]


def nineup(c1, c2):
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext(B3, 3, t * 3 ** (m - 1), m)
            congs += [crt(c, mm, r, n) for (r, n) in inp
                      for (c, mm) in [cell]]
    tails.append(ext(B3, 3, 0, E9))
    return congs, tails


def t25_pieces(contents):
    """25^(c1..c4): level-1 pieces (25-cells) + the deeper tower."""
    pieces = []
    for t, inp in enumerate(contents, start=1):
        cell = ext(B5, 5, t, 1)
        pieces.append([crt(c, m, r, n) for (r, n) in inp
                       for (c, m) in [cell]])
    deep_c, deep_t = [], []
    for k in range(2, E5 + 2):
        for t, inp in enumerate(contents, start=1):
            cell = ext(B5, 5, t * 5 ** (k - 1), k)
            deep_c += [crt(c, m, r, n) for (r, n) in inp
                       for (c, m) in [cell]]
    deep_t.append(ext(B5, 5, 0, E5 + 1))
    return pieces, (deep_c, deep_t)


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


def sets47():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("R1: 1", A1)
    add("R2: 2", A2)
    add("R3: 4", A4)
    add("R4: 8^", E8, E8T)
    add("R5: 5*1", x2(A1, *B5))
    add("R6: 5*2", x2(A2, *B5))
    add("R7: 5*4", x2(A4, *B5))
    add("R8: 5*8^", x2(E8, *B5), x2(E8T, *B5))
    sets = [s[1] for s in out]
    pieces, deep = t25_pieces(sets[:4])
    add("R9: 25^(1,2,4,8^)",
        pieces[0] + pieces[1] + pieces[2] + pieces[3] + deep[0], deep[1])
    sets = [s[1] for s in out]
    add("R10: 11^(R1..R9,x)", *tower(11, E1, sets[:9] + [None]))
    ten = [(s[1], s[2]) for s in out[:10]]
    for i, (cc, tt) in enumerate(ten, start=1):
        add(f"R{10 + i}: 3*R{i}", x2(cc, *B3), x2(tt, *B3))
    sets = [s[1] for s in out]
    add("R21: 9^(1,2)", *nineup(sets[0], sets[1]))
    add("R22: 9^(4,8^)", *nineup(sets[2], sets[3]))
    add("R23: 9^(5*1,5*2)", *nineup(sets[4], sets[5]))
    add("R24: 9^(5*4,5*8^)", *nineup(sets[6], sets[7]))
    add("R25: 9^(25^,11^)", *nineup(sets[8], sets[9]))
    # seven 7^ copies at four inputs (slot 4 = the 25-only input);
    # pool = sets 1-8,10-24 plus the five 25^ pieces
    sets = [s[1] for s in out]
    pool = sets[:8] + sets[9:24]                       # 23 items
    p5 = pieces + [deep[0]]                            # 5 items
    alloc = [
        (pool[0], pool[1], pool[2], p5[0]),
        (pool[3], pool[4], pool[5], p5[1]),
        (pool[6], pool[7], pool[8], p5[2]),
        (pool[9], pool[10], pool[11], p5[3]),
        (pool[12], pool[13], pool[14], p5[4]),
        (pool[15], pool[16], pool[17], pool[18]),
        (pool[19], pool[20], pool[21], pool[22]),
    ]
    for i, (a, b, c, d) in enumerate(alloc):
        add(f"R{26 + i}: 7^(4 inputs,x,x)",
            *tower(7, E7, [a, b, c, d, None, None]))
    sets = [s[1] for s in out]
    add("R33: 17^(R1..R16)", *tower(17, E1, sets[:16]))
    add("R34: 17^(R17..R32)", *tower(17, E1, sets[16:32]))
    sets = [s[1] for s in out]
    add("R35: 29^(R1..R28)", *tower(29, E1, sets[:28]))
    add("R36: 31^(R1..R30)", *tower(31, E1, sets[:30]))
    sets = [s[1] for s in out]
    add("R37: 13^(R1..R12)", *tower(13, E1, sets[:12]))
    add("R38: 13^(R13..R24)", *tower(13, E1, sets[12:24]))
    add("R39: 13^(R25..R36)", *tower(13, E1, sets[24:36]))
    sets = [s[1] for s in out]
    add("R40: 19^(R1..R13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("R41: 19^(R14..R26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    add("R42: 19^(R27..R39,x*5)", *tower(19, E1, sets[26:39] + [None] * 5))
    sets = [s[1] for s in out]
    add("R43: 41^(R1..R40)", *tower(41, E1, sets[:40]))
    sets = [s[1] for s in out]
    add("R44: 43^(R1..R42)", *tower(43, E1, sets[:42]))
    sets = [s[1] for s in out]
    add("R45: 23^(R1..R22)", *tower(23, E1, sets[:22]))
    add("R46: 23^(R23..R44)", *tower(23, E1, sets[22:44]))
    return out


def emit315():
    """Sec 3.15: 47^ filled with all forty-six sets."""
    congs, tails = [], []
    sets = sets47()
    assert len(sets) == 46
    for k in range(1, E47 + 1):
        for t in range(1, 47):
            cell = (t * 47 ** (k - 1) % 47 ** k, 47 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 47 ** E47))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    congs, tails = emit315()
    mods = [n for _, n in congs]
    print(f"sec3.15: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.15: {dup}")
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
             ("sec3.12", emit312.emit312()[0]),
             ("sec3.13", emit313.emit313()[0]),
             ("sec3.14", emit314.emit314()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 47
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
    B = (idx % 4 == 2) & (idx % 5 == 4) & (idx % 3 == 1)
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()

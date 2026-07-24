#!/usr/bin/env python3
"""
P15 V4 phase 38: residue-level emission of Owens sec 3.18
(primes 61, 67 and 89).

Hole: third 3-input (0 mod 3) in the fourth 5-input (4 mod 5) on the
4 hole, split in half mod 8: 61^ fills (2 mod 8), 67^ fills (6 mod 8),
with two 67-entries supplied by depth-shifted 61^ towers (Nielsen's
prime-13 "doubling" device) and one by an 89^.

Each half builds sixty-three sets "in the same manner as the previous
section" (sec 3.17's twenty-eight base sets, on this branch):
atoms 1,2,4,8,16^; 3*copies; 9^(1,2), 9^(4,8); twelve 5*copies; the
reserve set 5*9^(16^,_)+9^(_,16^); three 25^; then 29^, 31^ at
twenty-nine inputs; nine 7^ copies of shape 7^(_,_,x,x,25(x,x,x,_,x),_)
-- the recurring bare-25 piece is under-determined at residue level
(identical pieces would repeat moduli), so copy 1 carries the bare
25-cell and copies 2-9 carry placeholders, documented; three 19^ at
thirteen; 37^, 41^, 43^, two 23^, 47^, three 17^, four 13^, 53^,
six 11^ at nine inputs, 59^.

The 61-entries inside the 67^ run at 61-levels 3-4 and 5-6 (the
doubling/depth-increase), avoiding the (2 mod 8)-half's levels 1-2.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
EBIGP = 2

ONE = "ONE"
B5 = (4, 5)
B3 = (0, 3)
C4 = ext(B5, 5, 4, 1)          # the needed 25-child (24 mod 25)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


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


def build63(b8):
    """The sixty-three sets on the mod-8 half `b8`."""
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    e16 = [ext(b8, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    e16t = [ext(b8, 2, 0, D2)]
    A1, A2, A4, A8 = [(0, 1)], [(0, 2)], [(b8[0] % 4, 4)], [b8]

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

    add("1", A1)
    add("2", A2)
    add("4", A4)
    add("8", A8)
    add("16^", e16, e16t)
    five = [(s[1], s[2]) for s in out]
    for i, (cc, tt) in enumerate(five, start=1):
        add(f"3*{i}", x2(cc, *B3), x2(tt, *B3))
    add("9^(1,2)", *nineup(A1, A2))
    add("9^(4,8)", *nineup(A4, A8))
    twelve = [(s[1], s[2]) for s in out[:12]]
    for i, (cc, tt) in enumerate(twelve, start=1):
        add(f"5*{i}", x2(cc, *B5), x2(tt, *B5))
    ra = nineup(e16, None)
    rb = nineup(None, e16)
    add("5*9^(16^,_)+9^(_,16^)",
        x2(ra[0], *B5) + rb[0], x2(ra[1], *B5) + rb[1])
    sets = [s[1] for s in out]
    add("25^(1..4)", *t25(sets[:4]))
    add("25^(5..8)", *t25(sets[4:8]))
    add("25^(9..12)", *t25(sets[8:12]))
    sets = [s[1] for s in out]
    add("29^", *tower(29, E1, sets[:28]))
    add("31^ (29 inputs)", *tower(31, E1, sets[:29] + [None]))
    sets = [s[1] for s in out]
    # nine 7^ copies: slots 1,2,6 = sets, slot 5 = the bare-25 piece.
    # OBSTRUCTION B: identical bare-25 pieces across copies would
    # repeat the modulus 7^k*25, and every smooth rescaling collides
    # with the 25^/5* set families -- Owens's residue-level resolution
    # is unstated, so all nine pieces are placeholders here (see NOTES).
    for i in range(9):
        g = sets[3 * i:3 * i + 3]
        add(f"7^#{i+1}", *tower(7, E7, [g[0], g[1], None, None,
                                        None, g[2]]))
    sets = [s[1] for s in out]
    add("19^a", *tower(19, E1, sets[:13] + [None] * 5))
    add("19^b", *tower(19, E1, sets[13:26] + [None] * 5))
    add("19^c", *tower(19, E1, sets[26:39] + [None] * 5))
    sets = [s[1] for s in out]
    add("37^", *tower(37, E1, sets[:36]))
    add("41^", *tower(41, E1, sets[:40]))
    sets = [s[1] for s in out]
    add("43^", *tower(43, E1, sets[:42]))
    sets = [s[1] for s in out]
    add("23^a", *tower(23, E1, sets[:22]))
    add("23^b", *tower(23, E1, sets[22:44]))
    sets = [s[1] for s in out]
    add("47^", *tower(47, E1, sets[:46]))
    sets = [s[1] for s in out]
    add("17^a", *tower(17, E1, sets[:16]))
    add("17^b", *tower(17, E1, sets[16:32]))
    add("17^c", *tower(17, E1, sets[32:48]))
    sets = [s[1] for s in out]
    add("13^a", *tower(13, E1, sets[:12]))
    add("13^b", *tower(13, E1, sets[12:24]))
    add("13^c", *tower(13, E1, sets[24:36]))
    add("13^d", *tower(13, E1, sets[36:48]))
    sets = [s[1] for s in out]
    add("53^", *tower(53, E1, sets[:52]))
    sets = [s[1] for s in out]
    for i in range(6):
        add(f"11^#{i+1} (9 inputs)",
            *tower(11, E1, sets[9 * i:9 * i + 9] + [None]))
    sets = [s[1] for s in out]
    add("59^", *tower(59, E1, sets[:58]))
    assert len(out) == 63
    return out


def emit318():
    congs, tails = [], []
    # half A: 61^ on (2 mod 8)
    setsA = build63((2, 8))
    for k in range(1, EBIGP + 1):
        for t in range(1, 61):
            cell = (t * 61 ** (k - 1) % 61 ** k, 61 ** k)
            name, cc, tt = setsA[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 61 ** EBIGP))
    # half B: 67^ on (6 mod 8); 66 inputs = 63 sets + two depth-shifted
    # 61^ towers + one 89^
    setsB = build63((6, 8))
    sB = [s[1] for s in setsB]
    e61a = tower(61, 2, sB[:60], start=3)
    e61b = tower(61, 2, sB[:60], start=5)
    e89 = tower(89, E1, sB[:63] + [None] * 25)
    extra = [("61^ lv3-4", e61a[0], e61a[1]),
             ("61^ lv5-6", e61b[0], e61b[1]),
             ("89^", e89[0], e89[1])]
    allB = setsB + extra
    for k in range(1, EBIGP + 1):
        for t in range(1, 67):
            cell = (t * 67 ** (k - 1) % 67 ** k, 67 ** k)
            name, cc, tt = allB[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 67 ** EBIGP))
    return congs, tails


def main():
    congs, tails = emit318()
    mods = [n for _, n in congs]
    print(f"sec3.18: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.18: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    import emit315, emit316, emit317
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
             ("sec3.16", emit316.emit316()[0]),
             ("sec3.17", emit317.emit317()[0])]
    ov = 0
    for lab, cs in prevs:
        ov += len(set(mods) & set(n for _, n in cs))
    print(f"overlap w/ all previous sections: {ov}")
    N = 2 ** 7 * 3 ** 4 * 5 ** 3 * 61
    print("census window (61-half):", N)
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
    B = (idx % 8 == 2) & (idx % 5 == 4) & (idx % 3 == 0)
    unc = idx[B & ~cov]
    print(f"61-half uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()

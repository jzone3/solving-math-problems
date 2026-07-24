#!/usr/bin/env python3
"""
P15 V4 phase 34: residue-level emission of Owens sec 3.14 (the prime 43).

Hole: middle input of a 3 (2 mod 3) in the fourth input of a 5
(4 mod 5) on the 4 hole (2 mod 4).  Forty-two sets per the text:

  1..4  : 1, 2, 4, 8^
  5..9  : 5*1, 5*2, 5*4, 5*8^, 25^(1,2,4,8^)   @ (4,5)
  10    : 11^ (one input already covered -> nine sets + x)
  11..20: 3*set(1..10)
  21..25: 9^(1,2), 9^(4,8^), 9^(5*1,5*2), 9^(5*4,5*8^), 9^(25^,11^)
  26..30: five 7^ copies at five inputs each
  31    : 31^; 32: 29^; 33,34: two 17^; 35: 23^;
  36    : 37^ (partially filled here per sec 3.12 -> one x)
  37..39: three 13^; 40..42: three 19^ at thirteen inputs.

43 >= 42, so NO set is dropped: the bare set 1 gives modulus 43 and
the 43^ takes all forty-two sets.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
E43 = 2

ONE = "ONE"
B2 = (2, 4)
B5 = (4, 5)
B3 = (2, 3)


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


def sets43():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("Q1: 1", A1)
    add("Q2: 2", A2)
    add("Q3: 4", A4)
    add("Q4: 8^", E8, E8T)
    add("Q5: 5*1", x2(A1, *B5))
    add("Q6: 5*2", x2(A2, *B5))
    add("Q7: 5*4", x2(A4, *B5))
    add("Q8: 5*8^", x2(E8, *B5), x2(E8T, *B5))
    sets = [s[1] for s in out]
    add("Q9: 25^(1,2,4,8^)", *t25(sets[:4]))
    sets = [s[1] for s in out]
    add("Q10: 11^(Q1..Q9,x)", *tower(11, E1, sets[:9] + [None]))
    ten = [(s[1], s[2]) for s in out[:10]]
    for i, (cc, tt) in enumerate(ten, start=1):
        add(f"Q{10 + i}: 3*Q{i}", x2(cc, *B3), x2(tt, *B3))
    sets = [s[1] for s in out]
    add("Q21: 9^(1,2)", *nineup(sets[0], sets[1]))
    add("Q22: 9^(4,8^)", *nineup(sets[2], sets[3]))
    add("Q23: 9^(5*1,5*2)", *nineup(sets[4], sets[5]))
    add("Q24: 9^(5*4,5*8^)", *nineup(sets[6], sets[7]))
    add("Q25: 9^(25^,11^)", *nineup(sets[8], sets[9]))
    sets = [s[1] for s in out]
    for i in range(5):
        add(f"Q{26 + i}: 7^(Q{5*i+1}..Q{5*i+5},x)",
            *tower(7, E7, sets[5 * i:5 * i + 5] + [None]))
    sets = [s[1] for s in out]
    add("Q31: 31^(Q1..Q30)", *tower(31, E1, sets[:30]))
    add("Q32: 29^(Q1..Q28)", *tower(29, E1, sets[:28]))
    sets = [s[1] for s in out]
    add("Q33: 17^(Q1..Q16)", *tower(17, E1, sets[:16]))
    add("Q34: 17^(Q17..Q32)", *tower(17, E1, sets[16:32]))
    sets = [s[1] for s in out]
    add("Q35: 23^(Q1..Q22)", *tower(23, E1, sets[:22]))
    sets = [s[1] for s in out]
    add("Q36: 37^(Q1..Q35,x)", *tower(37, E1, sets[:35] + [None]))
    sets = [s[1] for s in out]
    add("Q37: 13^(Q1..Q12)", *tower(13, E1, sets[:12]))
    add("Q38: 13^(Q13..Q24)", *tower(13, E1, sets[12:24]))
    add("Q39: 13^(Q25..Q36)", *tower(13, E1, sets[24:36]))
    sets = [s[1] for s in out]
    add("Q40: 19^(Q1..Q13,x*5)", *tower(19, E1, sets[:13] + [None] * 5))
    add("Q41: 19^(Q14..Q26,x*5)", *tower(19, E1, sets[13:26] + [None] * 5))
    add("Q42: 19^(Q27..Q39,x*5)", *tower(19, E1, sets[26:39] + [None] * 5))
    return out


def emit314():
    """Sec 3.14: 43^ filled with ALL forty-two sets (43 >= 42)."""
    congs, tails = [], []
    sets = sets43()
    assert len(sets) == 42
    for k in range(1, E43 + 1):
        for t in range(1, 43):
            cell = (t * 43 ** (k - 1) % 43 ** k, 43 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 43 ** E43))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313
    congs, tails = emit314()
    mods = [n for _, n in congs]
    print(f"sec3.14: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.14: {dup}")
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
             ("sec3.13", emit313.emit313()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 43
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
    B = (idx % 4 == 2) & (idx % 5 == 4) & (idx % 3 == 2)
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()

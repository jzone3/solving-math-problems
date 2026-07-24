#!/usr/bin/env python3
"""
P15 V4 phase 20: faithful residue-level emission of Owens sec. 3.4
(the prime 7) on top of the sec. 3.3 emission (emit33.py).

Target (thesis p.8-9): after the 7^ tower below, the diagram becomes
  Hole 4 : unchanged from sec 3.3;
  Hole 8 : 5( ,x,x,x,x)   -- only the first class mod 5 remains;
  Hole 16: 5(x,x,x,x,x)   -- completely covered;
  Hole 32: unchanged.

The 7^ tower (6 inputs per level, recursing on class 0):
  t=1: 8+16
  t=2: 3^(8,16^|8br) + 32^|16br
  t=3: 3(2,4,3^(1,2))            [4 = 0 (mod 4) here]
  t=4: 5( +x, 3(4,8+16,3^(x,4)), 3(1,x,x), 2,  125^.3^.4 )
  t=5: 5( +x, 8+16, 3(3^(1,2),x,x), 5^(1,2,3^(1,2),4), 125^.3^.8 )
  t=6: 5( +x, A, 3(2,x,x), 4, 125^.3^.16^ )
  A = 32^|16br + 3(3^(8, ), , 3^(x,16^|8br))
      + 5(8, 16^|8br, 3(3^(x,4),4,x), 3(3^(x,8),8,x), 3(3^(x,16^),16^,x))

The three 125^.3^.m sets target the residual sliver of the 8 hole in
class 4 (mod 5) (inner class 19 (mod 25), 3^ first slots).  Their
moduli need 5-exponent >= 5, beyond this window; they are relative
covering systems (verified separately by the emitgram compiler), so
the census injects them as verified cell covers (placeholders, marked,
excluded from the modulus-distinctness lists).

Checks: min modulus >= 42; all real moduli distinct within sec 3.4 and
against sec 3.3 + the 2/3 skeleton; residual census matches the target
diagram up to finite-depth tails and the dropped deep-modulus measure.
"""
import numpy as np
from canon import crt, ext, isect
from emit33 import emit as emit33_congs, HOLES

E2, E3, E5, E7 = 8, 3, 4, 2
N = 2 ** E2 * 3 ** E3 * 5 ** E5 * 7 ** E7      # 211,680,000

H8, H16 = HOLES["8"], HOLES["16"]


def tw(branch, k0):
    c, m = branch
    return [((c + 2 ** (k - 1)) % 2 ** k, 2 ** k) for k in range(k0, E2 + 1)]


UP16_8 = tw(H8, 4)         # 16^ restricted to the 8 branch
UP32_16 = tw(H16, 5)       # 32^ restricted to the 16 branch


def three_up(cell, a, b):
    """3^(a,b): canonical absolute 3-adic digits; slots are 'ONE',
    abs-list, or callables cell->congs."""
    out = []
    for k in range(1, E3 + 1):
        for t, inp in ((1, a), (2, b)):
            sub = ext(cell, 3, t * 3 ** (k - 1), k)
            if inp is None:
                continue
            if inp == "ONE":
                out.append(sub)
            elif callable(inp):
                out += inp(sub)
            else:
                out += isect(sub, inp)
    return out


def three_split(cell, s0, s1, s2):
    """3(s0,s1,s2): canonical slot->digit convention (phase 22): slots
    (1,2,3) sit on 3-adic digits (1,2,0)."""
    out = []
    for cls, inp in ((1, s0), (2, s1), (0, s2)):
        sub = ext(cell, 3, cls, 1)
        if inp is None:
            continue
        if inp == "ONE":
            out.append(sub)
        elif callable(inp):
            out += inp(sub)
        else:
            out += isect(sub, inp)
    return out


def set_A(cell):
    out = []
    out += isect(cell, UP32_16)
    out += three_split(cell,
                       lambda s: three_up(s, [H8], None),
                       None,
                       lambda s: three_up(s, None, UP16_8))
    for i, inp in enumerate((
            lambda s: isect(s, [H8]),
            lambda s: isect(s, UP16_8),
            lambda s: three_split(s, lambda u: three_up(u, None, [(0, 4)]),
                                  [(0, 4)], None),
            lambda s: three_split(s, lambda u: three_up(u, None, [H8]),
                                  [H8], None),
            lambda s: three_split(s, lambda u: three_up(u, None, UP16_8),
                                  UP16_8, None))):
        sub = ext(cell, 5, (i + 1) % 5, 1)   # slots (1..5) -> digits (1,2,3,4,0)
        out += inp(sub)
    return out


def five_up_t5(cell):
    """5^(1, 2, 3^(1,2), 4): canonical absolute 5-adic digits."""
    out = []
    for k in range(1, E5):
        for t, inp in ((1, "ONE"), (2, [(0, 2)]),
                       (3, lambda s: three_up(s, "ONE", [(0, 2)])),
                       (4, [(0, 4)])):
            sub = ext(cell, 5, t * 5 ** (k - 1), k)
            if inp == "ONE":
                out.append(sub)
            elif callable(inp):
                out += inp(sub)
            else:
                out += isect(sub, inp)
    return out


def sliver_cells(cell7):
    """Residual sliver of the 8 hole in cell7: hole8 & 20 (mod 25) &
    3^ first slots -- covered by the (relatively verified) 125^.3^.m."""
    cells = []
    base = crt(20, 25, cell7[0], cell7[1])
    for kk in range(1, E3 + 1):
        c2 = ext(base, 3, 3 ** (kk - 1), kk)
        cells.append(crt(H8[0], H8[1], c2[0], c2[1]))
    return cells


def emit34():
    congs, placeholders = [], []
    for k7 in range(1, E7 + 1):
        for t in range(1, 7):
            cell7 = ((t * 7 ** (k7 - 1)) % 7 ** k7, 7 ** k7)
            if t == 1:
                congs += isect(cell7, [H8, H16])
            elif t == 2:
                congs += three_up(cell7, [H8], UP16_8)
                congs += isect(cell7, UP32_16)
            elif t == 3:
                congs += three_split(cell7, [(0, 2)], [(0, 4)],
                                     lambda s: three_up(s, "ONE", [(0, 2)]))
            else:
                # 5-split slots (1..5) -> digits (1,2,3,4,0): slot 1 is
                # the "+x", slot 5 holds the 125^ sets (digit 0, below)
                for j in range(1, 5):
                    cj = crt(j, 5, cell7[0], cell7[1])
                    if j == 1:
                        continue                    # "+x" (slot 1)
                    if t == 4:
                        if j == 2:
                            congs += three_split(
                                cj, [(0, 4)], [H8, H16],
                                lambda s: three_up(s, None, [(0, 4)]))
                        elif j == 3:
                            congs += three_split(cj, "ONE", None, None)
                        elif j == 4:
                            congs += isect(cj, [(0, 2)])
                    elif t == 5:
                        if j == 2:
                            congs += isect(cj, [H8, H16])
                        elif j == 3:
                            congs += three_split(
                                cj, lambda s: three_up(s, "ONE", [(0, 2)]),
                                None, None)
                        elif j == 4:
                            congs += five_up_t5(cj)
                    elif t == 6:
                        if j == 2:
                            congs += set_A(cj)
                        elif j == 3:
                            congs += three_split(cj, [(0, 2)], None, None)
                        elif j == 4:
                            congs += isect(cj, [(0, 4)])
                if t in (4, 5, 6):
                    placeholders += sliver_cells(cell7)
    return congs, placeholders


def main():
    import emitcore
    skel = emitcore.emit()
    s33 = emit33_congs()
    s34, ph = emit34()

    def keep(cs):
        good = [(r, n) for r, n in cs if N % n == 0]
        dropped = sum(1 / n for r, n in cs if N % n)
        return good, dropped

    s33k, d33 = keep(s33)
    s34k, d34 = keep(s34)
    phk, dph = keep(ph)
    print(f"sec3.4: {len(s34)} congs ({len(s34k)} in window, dropped "
          f"measure {d34:.2e}); sec3.3 dropped {d33:.2e}; "
          f"placeholders {len(phk)} (dropped {dph:.2e})")
    m34 = [n for _, n in s34]
    print(f"min modulus sec3.4: {min(m34)} (require >= 42)")
    dup = len(m34) - len(set(m34))
    ov33 = set(m34) & set(n for _, n in s33)
    ovsk = set(m34) & set(n for _, n in skel)
    print(f"dups within sec3.4: {dup}; overlap w/ sec3.3: {len(ov33)}; "
          f"overlap w/ skeleton: {len(ovsk)}")

    cov = np.zeros(N, dtype=bool)
    for r, n in s33k + s34k + phk:
        cov[r % n::n] = True
    for name, (hr, hn) in HOLES.items():
        line = []
        tot5 = hn * 5
        for j in range(5):
            # x ≡ hr (mod hn) and x ≡ j (mod 5)
            r0, n0 = crt(hr, hn, j, 5)
            seg = cov[r0::n0]
            line.append(f"j={j}: {seg.size - int(seg.sum())}/{seg.size}")
        print(f"hole {name:>2}: " + "  ".join(line))


if __name__ == "__main__":
    main()

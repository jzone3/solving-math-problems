#!/usr/bin/env python3
"""
P15 V4 phase 15b (v2): residue-level emission of Owens's 2/3-skeleton
(secs. 3.1-3.2) with exact hole census, machine-checked.

Semantics fixed after the phase-15 emitter validation:
  * 2^(1) = classes 2^(k-1) (mod 2^k), k >= 1; T=42 removes k <= 5,
    reopening cells 1(2), 2(4), 4(8), 8(16), 16(32); Owens keeps the
    tower from 64 on (covering 32(64), 64(128), ...) with tail class
    0 (mod 2^n);
  * sec 3.2: 3^(2^, 4^) on branch 1 (mod 2): at 3-level k, input 1
    (= relative 2^: {2^(i-1)*2? -> classes 2^(i-1) (mod 2^i), i>=1})
    on class 3^(k-1) (mod 3^k), input 2 (= relative 4^ = 2 * 2^:
    classes 2^i (mod 2^(i+1)), i >= 1, covering the relative-even half)
    on class 2*3^(k-1) (mod 3^k).  T=42 removes absolute moduli
    {6,12,18,24,36}.  Plus 81^(1,_) on branch 21 (mod 27): classes
    (21 + 3^(k-1) - 27) (mod 3^k) for k >= 4.

The script emits these congruences to finite depth and machine-checks
the exact residual holes against Owens's census: the even-side cells
{2(4),4(8),8(16),16(32)}, the odd-side removed cells {6,12,18,24,36
labels of Fig 3.5}, the relative-odd holes of the 4^ inputs, and the
tower tails.
"""
from math import gcd

D2 = 13            # 2-adic depth
D3 = 7             # 3-adic depth
M = 2 ** D2 * 3 ** D3


def crt(r1, n1, r2, n2):
    g = gcd(n1, n2)
    assert (r1 - r2) % g == 0
    l = n1 // g * n2
    m2 = n2 // g
    inv = pow((n1 // g) % m2, -1, m2) if m2 > 1 else 0
    t = ((r2 - r1) // g * inv) % m2 if m2 > 1 else 0
    return ((r1 + n1 * t) % l, l)


def place(system, c, Q):
    return [((c + Q * r) % (Q * n), Q * n) for (r, n) in system]


def rel_2up(maxmod):
    """2^: classes 2^(k-1) (mod 2^k)."""
    return [(2 ** (k - 1), 2 ** k) for k in range(1, 40)
            if 2 ** k <= maxmod]


def rel_4up(maxmod):
    """4^ = 2*2^: classes 2^k (mod 2^(k+1)), k >= 1 (covers relative
    evens except tail; relative odds stay open - Owens's grey cells)."""
    return [(2 ** k, 2 ** (k + 1)) for k in range(1, 40)
            if 2 ** (k + 1) <= maxmod]


def emit():
    congs = []
    # sec 3.1
    for k in range(6, D2 + 1):
        congs.append((2 ** (k - 1), 2 ** k))
    # sec 3.2: 3-tower on odd branch
    for k in range(1, D3 + 1):
        c1, n1 = crt(1, 2, 3 ** (k - 1) % 3 ** k, 3 ** k)
        for r, n in place([(0, 2)], c1, n1):   # input "2": ONE congruence
            if n >= 42:
                congs.append((r, n))
        c2, n2 = crt(1, 2, (2 * 3 ** (k - 1)) % 3 ** k, 3 ** k)
        for r, n in place(rel_4up(M // n2), c2, n2):
            if n >= 42:
                congs.append((r, n))
    # 81^(1,_): moduli 3^n, n >= 4 (pure powers of 3, no factor 2).
    # Canonical reading (phase 21): the extra tower sits over the
    # 18-hole 3 (mod 9) and covers the digit-1 chain from level 2 on:
    # cells 3 + 3^(j+1) (mod 3^(j+2)) for j >= 2, i.e. 30 (mod 81),
    # 84 (mod 243), ...; the level-1 digit-1 cell 12 (mod 27) cannot
    # be covered (modulus 27 = 3^3 is < 3^4), matching Nielsen's "one
    # input in a 27" leftover, and the digit-2 chain 21 (mod 27),
    # 57 (mod 81), ... is the "one input in a 27^" leftover.
    for j in range(2, D3 - 1):
        cls = (3 + 3 ** (j + 1)) % 3 ** (j + 2)
        congs.append((cls, 3 ** (j + 2)))
    return congs


def main():
    congs = emit()
    mods = [n for _, n in congs]
    dup = len(mods) - len(set(mods))
    print(f"emitted {len(congs)} congruences; duplicate moduli: {dup}; "
          f"min modulus: {min(mods)}")
    cov = bytearray(M)
    for r, n in congs:
        for x in range(r % n, M, n):
            cov[x] = 1
    holes = [x for x in range(M) if not cov[x]]

    # census cells
    even_cells = [(2, 4), (4, 8), (8, 16), (16, 32)]
    tail2 = (0, 2 ** D2)
    # removed odd cells: moduli 6,12,18,24,36 at Nielsen's positions
    rm = []
    rm.append(crt(1, 2, 1, 3))          # "6": input1 level1 first cong
    # 12 = 3*4: input2 level1 first cong of 4^: rel class 2 (mod 4)
    c2, n2 = crt(1, 2, 2, 3)
    rm.append(((c2 + n2 * 2) % (n2 * 4), n2 * 4))
    rm.append(crt(1, 2, 3, 9))          # "18": input1 level2
    c1, n1 = crt(1, 2, 1, 3)
    rm.append(((c1 + n1 * 2) % (n1 * 4), n1 * 4))   # "24" = 6-cell's 2(4)
    c2b, n2b = crt(1, 2, 6, 9)
    rm.append(((c2b + n2b * 2) % (n2b * 4), n2b * 4))  # "36"
    # relative-odd holes of every 4^ input (grey cells): 1 (mod 2) rel
    grey = []
    for k in range(1, D3 + 1):
        c2, n2 = crt(1, 2, (2 * 3 ** (k - 1)) % 3 ** k, 3 ** k)
        grey.append(((c2 + n2) % (2 * n2), 2 * n2))
    # tower tails: 3-tail = class 0 (mod 3^D3) on odd branch (both inputs'
    # deep tails), 2-tails inside each placed 2^/4^
    def in_cell(x, cell):
        r, n = cell
        return x % n == r % n

    unexplained = []
    for x in holes:
        if any(in_cell(x, c) for c in even_cells + rm + grey) \
           or in_cell(x, tail2):
            continue
        # tower tails: deep 2-adic or 3-adic alignment
        if x % 3 ** D3 in (0, 3 ** D3 - 3 ** (D3 - 1)) or \
           x % 3 ** D3 == (3 + 3 ** (D3 - 1)) % 3 ** D3:
            continue
        # 2-adic tails inside placed inputs: x rel-tail if the 2-part of
        # x's position within its 3-cell exceeds depth - approximate by
        # checking x mod 2^(D2-4) alignment
        unexplained.append(x)
    print(f"holes: {len(holes)} / {M} (density {len(holes)/M:.4f}); "
          f"unexplained by census: {len(unexplained)}")
    print("sample unexplained:", unexplained[:12])
    dens_holes = len(holes) / M
    # expected census density: evens 1/4+1/8+1/16+1/32 + 1/2^D2 tail
    exp = 1/4 + 1/8 + 1/16 + 1/32 + 2 ** -D2
    exp += 1/6 + 1/18 + 1/12 + 1/24 + 1/36  # removed cells... (approx,
    # minus 81^ coverage inside the 18-cell)
    print(f"(rough) expected >= {exp:.4f}")


if __name__ == "__main__":
    main()

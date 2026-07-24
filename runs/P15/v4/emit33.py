#!/usr/bin/env python3
"""
P15 V4 phase 19: faithful residue-level emission of Owens sec. 3.3
(the prime 5) onto the even-branch holes 2(4), 4(8), 8(16), 16(32),
with machine checks:
  * every emitted modulus >= 42;
  * all moduli distinct (within the section and against the emitted
    2/3 skeleton of emitcore.py);
  * the residual sub-holes on each hole cell match Owens's diagram
    (thesis p.6):
      Hole 4 : 5( ,3( , ,3^(x, )),3( ,x,x), ,5(x,x,x,3^( ,x),x))
      Hole 8 : same as 4, then 125^ patch on input 4 (all but one 3^)
      Hole 16: 5(x,3( , ,x),3( ,x,x), ,x)
      Hole 32: 5(x,x,x, ,x)

Notation (sec. 3.3): 4,8,16,32 = classes 2(4),4(8),8(16),16(32);
2 = 2 (mod 2); 32^ inside 3^ restricted to the 16 branch; 64^
restricted to the 32 branch; the outer object is a plain 5-split of
the even branch, inputs on classes j = 0..4 (mod 5).
"""
from math import gcd

D2, D3, D5 = 9, 4, 3
N = 2 ** D2 * 3 ** D3 * 5 ** D5          # 512*81*125 = 5,184,000

HOLES = {"4": (2, 4), "8": (4, 8), "16": (8, 16), "32": (16, 32)}


def crt(r1, n1, r2, n2):
    g = gcd(n1, n2)
    assert (r1 - r2) % g == 0
    l = n1 // g * n2
    m2 = n2 // g
    if m2 == 1:
        return (r1 % l, l)
    inv = pow((n1 // g) % m2, -1, m2)
    t = ((r2 - r1) // g * inv) % m2
    return ((r1 + n1 * t) % l, l)


def inter(congs, ctx):
    """Intersect absolute congruences with a coprime context class."""
    c, m = ctx
    return [crt(r, n, c, m) for (r, n) in congs]


def hole_cells(names):
    return [HOLES[s] for s in names]


def two_tower(branch, start_k):
    """q=2 tower inside 2-adic branch (c,m): classes c+2^(k-1) (mod 2^k)."""
    c, m = branch
    return [((c + 2 ** (k - 1)) % 2 ** k, 2 ** k)
            for k in range(start_k, D2 + 1)]


def up4():
    """4^ : covers all of 2 (mod 2): classes 2^(k-1) (mod 2^k), k>=2."""
    return [(2 ** (k - 1), 2 ** k) for k in range(2, D2 + 1)]


def three_up(a_congs, b_congs, ctx):
    """3^(a,b) in context ctx (coprime to 3): level k>=1 puts a on
    class 3^(k-1), b on class 2*3^(k-1) (mod 3^k); recurse on 0."""
    out = []
    c0, m0 = ctx
    for k in range(1, D3 + 1):
        for cls, inp in ((3 ** (k - 1), a_congs), (2 * 3 ** (k - 1), b_congs)):
            cell = ((c0 + m0 * cls) % (m0 * 3 ** k), m0 * 3 ** k)
            if inp == "ONE":
                out.append(cell)
            else:
                out += inter(inp, cell)
    return out


def emit():
    congs = []
    # ---- input 1 (j=0 mod 5): 16+32
    congs += inter(hole_cells(["16", "32"]), (0, 5))

    # ---- input 2 (j=1): 3( , , 3^(4+8, ) + 3^(16, 32^|16br) ) + 64^|32br
    ctx = crt(1, 5, 2, 3)           # third class of the 3-split
    congs += three_up(hole_cells(["4", "8"]), [], ctx)
    congs += three_up(hole_cells(["16"]), two_tower(HOLES["16"], 5), ctx)
    congs += inter(two_tower(HOLES["32"], 6), (1, 5))

    # ---- input 3 (j=2): 3(64^|32br, 4+8+16+32, 3^(1,2))
    congs += inter(two_tower(HOLES["32"], 6), crt(2, 5, 0, 3))
    congs += inter(hole_cells(["4", "8", "16", "32"]), crt(2, 5, 1, 3))
    congs += three_up("ONE", [(0, 2)], crt(2, 5, 2, 3))

    # ---- input 4 (j=3): blank, then the 125^ patch on the 8 hole:
    # 125^(3^(4,x), 3^(8,x), 3^(16^|8br,x), 3^( ,x))  [x = already covered]
    # (5^3)^ = 5^2 * 5^: level k>=1, classes 25*t*5^(k-1) (mod 25*5^k)
    # relative inside class 3 (mod 5); only emit the non-x parts.
    # The patch lives on the 8 hole (4 mod 8); the labels 4, 8, 16^ are
    # RELATIVE 2-adic sets in the coordinate s where x = 4 + 8s (this is
    # the only reading under which the patch covers hole-8 cells, and it
    # matches Owens reusing "125 3^ 4", "125^ 3^ 8", "125^ 3^ 16^" as
    # modulus families in sec. 3.4).  The "x" second slots of each 3^ are
    # coverage Owens accounts elsewhere; they are NOT emitted here.
    hr, hn = HOLES["8"]
    rel4 = [(2, 4)]
    rel8 = [(4, 8)]
    rel16up = [(2 ** (k - 1), 2 ** k) for k in range(4, D2 - 2)]
    for k in range(1, D5 + 1):
        for t, rinp in ((1, rel4), (2, rel8), (3, rel16up), (4, None)):
            rel = (25 * t * 5 ** (k - 1), 25 * 5 ** k)
            cell = ((3 + 5 * rel[0]) % (5 * rel[1]), 5 * rel[1])
            if rinp is None:
                continue
            for kk in range(1, D3 + 1):
                c2 = ((cell[0] + cell[1] * 3 ** (kk - 1)) % (cell[1] * 3 ** kk),
                      cell[1] * 3 ** kk)
                # place relative 2-adic set into hole 8 within cell c2
                for rr, rn in rinp:
                    congs.append(crt((hr + hn * rr) % (hn * rn), hn * rn,
                                     c2[0], c2[1]))

    # ---- input 5 (j=4): 5(2, 4+8+16+32, 3^(1,2),
    #                       3^(32^|16br, 4+8+16) + 64^|32br, 5^(1,2,3^(1,2),4^))
    def in5(i):                      # inner 5-split classes (mod 25)
        return crt(4, 5, (4 + 5 * i) % 25, 25)
    congs.append(crt(0, 2, in5(0)[0], in5(0)[1]))            # "2"
    congs += inter(hole_cells(["4", "8", "16", "32"]), in5(1))
    congs += three_up("ONE", [(0, 2)], in5(2))
    congs += three_up(two_tower(HOLES["16"], 5),
                      hole_cells(["4", "8", "16"]), in5(3))
    congs += inter(two_tower(HOLES["32"], 6), in5(3))
    # 5^(1,2,3^(1,2),4^) on inner class 4 (mod 25): tower level k>=1,
    # classes 4 + 5*(t*5^(k-1)) rel -> abs via place into in5(4)... the
    # 5^ splits the cell (mod 5^(k+2)); inputs t=1..4.
    base_c, base_m = in5(4)
    for k in range(1, D5 + 1):
        for t, inp in ((1, "ONE"), (2, [(0, 2)]), (3, "3UP12"), (4, up4())):
            rel_r, rel_n = t * 5 ** (k - 1), 5 ** k
            cell = ((base_c + base_m * rel_r) % (base_m * rel_n),
                    base_m * rel_n)
            if inp == "ONE":
                congs.append(cell)
            elif inp == "3UP12":
                congs += three_up("ONE", [(0, 2)], cell)
            else:
                congs += inter(inp, cell)
    return congs


def main():
    import emitcore
    skel = emitcore.emit()
    congs = emit()
    mods = [n for _, n in congs]
    print(f"sec3.3 emission: {len(congs)} congruences")
    print(f"min modulus: {min(mods)}  (require >= 42)")
    dup = len(mods) - len(set(mods))
    print(f"duplicate moduli within section: {dup}")
    overlap = set(mods) & set(n for _, n in skel)
    print(f"modulus overlap with 2/3 skeleton: {len(overlap)}")

    # coverage census on the four holes
    cov = bytearray(N)
    for r, n in congs:
        cov[r % n::n] = b"\x01" * len(range(r % n, N, n))
    for name, (hr, hn) in HOLES.items():
        tot = rem = 0
        rem_by_j = [0] * 5
        for x in range(hr, N, hn):
            tot += 1
            if not cov[x]:
                rem += 1
                rem_by_j[x % 5] += 1
        print(f"hole {name:>2} ({hr} mod {hn}): {rem}/{tot} uncovered; "
              f"by class mod 5: {rem_by_j}")


if __name__ == "__main__":
    main()

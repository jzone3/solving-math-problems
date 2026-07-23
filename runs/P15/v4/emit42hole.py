"""P15 V4 phase 6: EXPLICIT, machine-verified cover of the 42-hole.

Emits a concrete finite list of congruences (a_i mod m_i) with
  * all m_i distinct,
  * all m_i >= 43,
  * union of the classes covering the target class  a* (mod 42),
  * every m_i avoiding the *identified* moduli of Owens's system
    (7-layer, 2-layer, 3-layer, 5-layer values from hole42.py), with a
    machine-produced CLEARANCE LIST of which m_i still require checking
    against Owens's full (unreconstructed) ledger.

Method: work in the hole coordinate k (x = a* + 42 k). A congruence
k = r (mod n) equals x = a* + 42 r (mod 42 n) and can be realized by any
modulus m = n*g, g | 42, gcd(n*g, 42) = g (then the congruence
x = a*+42r mod m covers a superset - fine). We build an exact inner cover
of Z with per-n multiplicity limited to the number of free realizations,
then map each inner class to a distinct free m.

Verification: exhaustive residue check over lcm of the inner moduli, plus
distinctness / bound checks on the m_i. Prints PASS/FAIL.
"""

from math import gcd
from hole42 import candidates, OWENS_SMALL_MODULI

A_STAR = 2  # representative of the deleted class mod 42 (any value works)


def free_ms(n):
    return [m for m in candidates(n) if m not in OWENS_SMALL_MODULI]


def build_inner_cover():
    """Greedy exact cover of Z by classes r mod n, each n used at most
    len(free_ms(n)) times. Small L window with exhaustive verification."""
    # multiplicities of the small inner moduli (from hole42.py free lists):
    # n=5: 3 free, n=7: 4 free, n=10: 3, n=14: 2, n=35/70: enough.
    # Hand-built exact cover (verified below):
    #   3 classes mod 5   : 0,1,2 (mod 5)
    #   4 classes mod 7   : 0,1,2,3 (mod 7)
    #   remaining: k = 3,4 (mod 5) AND k = 4,5,6 (mod 7)  -> 6 cells mod 35
    #   cover them with 6 classes mod 35 (n=35: free m count?)
    cover = [(0, 5), (1, 5), (2, 5),              # n=5 (3 free: 70,105,210)
             (3, 10), (8, 10), (4, 10),           # n=10 (3 free: 60,140,420)
             (0, 7), (1, 7), (2, 7), (3, 7)]      # n=7 (4 free)
    # remaining: 9 mod 10 AND 4,5,6 mod 7 -> 3 cells mod 70
    cells = [next(x for x in range(70) if x % 10 == 9 and x % 7 == b)
             for b in (4, 5, 6)]
    cover += [(cells[0], 70), (cells[1], 70)]     # n=70 (2 free: 980,2940)
    # last cell mod 70 split into 2 classes mod 140 (n=140: 2 free)
    cover += [(cells[2], 140), (cells[2] + 70, 140)]
    return cover


def main():
    inner = build_inner_cover()
    # verify inner covers Z over lcm
    L = 140 * 3
    ok = all(any(x % n == r % n for r, n in inner) for x in range(L))
    print(f"inner cover of Z (lcm window {L}): {'OK' if ok else 'FAIL'}")

    # multiplicity check + realization assignment
    used_ms = set()
    emitted = []
    clearance = []
    from collections import Counter
    cnt = Counter(n for _, n in inner)
    for n, c in sorted(cnt.items()):
        fm = free_ms(n)
        print(f"n={n}: need {c} realizations, free list {fm}")
        assert c <= len(fm), f"multiplicity overflow at n={n}"
    fm_iter = {n: iter(free_ms(n)) for n in cnt}
    for r, n in inner:
        m = next(fm_iter[n])
        assert m not in used_ms
        used_ms.add(m)
        a = (A_STAR + 42 * r) % m
        # sanity: the class a mod m contains all x = a* + 42k, k = r mod n
        g = gcd(m, 42)
        assert m // g == n and (A_STAR + 42 * r - a) % m == 0
        emitted.append((a, m))
        if not any(m % p == 0 for p in
                   (97, 101, 103, 107, 109, 113)):
            clearance.append(m)

    # final verification: every x in the class A_STAR mod 42 is covered,
    # exhaustively over lcm(42, all m)
    from math import lcm
    M = 42
    for _, m in emitted:
        M = lcm(M, m)
    bad = [x for x in range(A_STAR, M + A_STAR, 42)
           if not any(x % m == a for a, m in emitted)]
    dis = len({m for _, m in emitted}) == len(emitted)
    mn = min(m for _, m in emitted)
    verdict = (not bad) and dis and mn >= 43
    print()
    print(f"emitted {len(emitted)} congruences: {emitted}")
    print(f"covers class {A_STAR} mod 42 over lcm {M}: {not bad}")
    print(f"distinct moduli: {dis}; min modulus: {mn}")
    print()
    print(f"{'PASS' if verdict else 'FAIL'}: explicit 42-hole cover, "
          f"{len(emitted)} congruences, distinct moduli >= 43 "
          f"(internal checks only)")
    print()
    print("CLEARANCE vs faithful Owens 3.1-3.4 enumeration "
          "(owens_smooth.py):")
    from owens_smooth import used_smooth
    U = used_smooth(10**5)
    coll = sorted(m for _, m in emitted if m in U)
    print(f"COLLISIONS with Owens's own moduli: {coll}")
    if coll:
        print("=> this patch is INVALID as a T=43 completion: the hole42.py")
        print("   OWENS_SMALL_MODULI list was incomplete. The faithful")
        print("   enumeration shows the only free 7-smooth moduli are")
        print("   7^k * t, t in {1,2,3,4,5}, k >= 2 (density 0.6167 < 1).")
        print("   See patch43.py + NOTES section 15 for the corrected")
        print("   reduction.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Independent verifier for COMPRESSED covering-system witnesses (P15).

Witness format (JSON, produced by runs/P15/v4/cover3.py):
  { "T": int, "recipe": [ {"p": prime, "C_before": int,
      "congs": [[m, a], ...], "C_after": int,
      "kills": {"r": "count", ...}}, ... ] }

Semantics being verified (see proof sketch below):
- State after level l: M_l = product of the level primes so far; the set of
  UNCOVERED residues mod M_l ("holes") is tracked exactly as counts grouped
  by residue mod a window C_l, where C_l | M_l and v_p(C_l) = v_p(M_l) for
  the next level prime p (checked).
- Level with prime p: each hole r mod M splits into the p residues that,
  reduced mod C*p, equal r + C*s (s = 0..p-1); this is exact because
  v_p(C) = v_p(M) and gcd(M/C-part, p-part) issues cancel: the children of
  r + C*u (any lift) hit each class r + C*s mod C*p equally often, once, by
  CRT. Structured congruence (m, a) with m | C*p, m >= T covers exactly the
  child cells whose residue mod m equals a. Distinct moduli enforced.
- Kills: a hole r mod M_l can be covered entirely by the single congruence
  r mod d for ANY divisor d | M_l with d >= T (since r + M_l Z is contained
  in r + d Z). Only distinctness of moduli constrains this, so a valid
  assignment of kill-divisors exists iff Hall's condition holds; as the
  usable divisor sets are nested over levels (d | M_l => d | M_l'), Hall
  reduces to the prefix inequalities
      #structured(ALL levels) + #kills(levels <= l) <= #{d | M_l : d >= T}
  for every l (structured moduli all divide the final N; counting them all
  against every prefix is conservative and sufficient).
- PASS iff after the last level the exact hole count is 0 and all the above
  constraints hold. Then the (astronomically large but well-defined)
  congruence set {structured} u {kill congruences} covers Z with distinct
  moduli all >= T.
"""
import json, sys


def factorize(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def vp(n, p):
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def count_divisors_ge(fact, T):
    """#divisors >= T of the number with given factorization (exact)."""
    D = 1
    for e in fact.values():
        D *= e + 1
    primes = sorted(fact)
    below = 0
    def rec(i, prod):
        nonlocal below
        if i == len(primes):
            below += 1
            return
        p = primes[i]
        v = prod
        for _ in range(fact[p] + 1):
            if v >= T:
                break
            rec(i + 1, v)
            v *= p
    rec(0, 1)
    return D - below


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main(path):
    with open(path) as f:
        w = json.load(f)
    T = int(w["T"])
    recipe = w["recipe"]
    if T < 2 or not recipe:
        fail("degenerate witness")

    holes = {0: 1}          # residue mod C -> exact count
    C = 1
    Mfact = {}              # factorization of M_l
    used = set()            # structured modulus values
    n_structured_total = sum(len(lv["congs"]) for lv in recipe)
    kills_cum = 0

    for li, lv in enumerate(recipe):
        p = int(lv["p"])
        if int(lv["C_before"]) != C:
            fail(f"level {li}: C_before mismatch")
        # window invariant: v_p(C) must equal v_p(M) to split exactly
        eC = factorize(C).get(p, 0)
        if eC != Mfact.get(p, 0):
            fail(f"level {li}: window lost power of {p}")
        Cfull = C * p
        # split: children of class r are r + C*s mod Cfull, inheriting count
        cells = {}
        for r, n in holes.items():
            for s in range(p):
                cells[r + C * s] = cells.get(r + C * s, 0) + n
        # structured congruences
        for m, a in lv["congs"]:
            m, a = int(m), int(a)
            if m < T:
                fail(f"level {li}: modulus {m} < T")
            if Cfull % m != 0:
                fail(f"level {li}: modulus {m} does not divide C*p")
            if m in used:
                fail(f"level {li}: modulus {m} reused")
            used.add(m)
            for r in [x for x in cells if x % m == a % m]:
                del cells[r]
        Mfact[p] = Mfact.get(p, 0) + 1
        # kills (counts of holes wiped by pooled divisors of M_l)
        for r, k in lv.get("kills", {}).items():
            r, k = int(r), int(k)
            if k < 0 or r not in cells or k > cells[r]:
                fail(f"level {li}: bad kill ({r}, {k})")
            cells[r] -= k
            kills_cum += k
            if cells[r] == 0:
                del cells[r]
        pool = count_divisors_ge(Mfact, T)
        if n_structured_total + kills_cum > pool:
            fail(f"level {li}: Hall prefix violated "
                 f"({n_structured_total} + {kills_cum} > {pool})")
        # window merge
        C2 = int(lv["C_after"])
        if Cfull % C2 != 0:
            fail(f"level {li}: C_after does not divide C*p")
        merged = {}
        for r, n in cells.items():
            merged[r % C2] = merged.get(r % C2, 0) + n
        holes, C = merged, C2

    # structured moduli must all divide final N (m | C*p at its level, and
    # every prime power of C at that level is <= its final power in N) —
    # guaranteed by m | Cfull | M_l | N since C | M invariant was checked.
    Hf = sum(holes.values()) if holes else 0
    if Hf != 0:
        fail(f"holes remain: {Hf}")
    N_primes = "*".join(f"{p}^{e}" for p, e in sorted(Mfact.items()))
    print(f"PASS: compressed covering system, min modulus >= {T}, "
          f"N = {N_primes}, structured congruences = {n_structured_total}, "
          f"pool kills = {kills_cum}")


if __name__ == "__main__":
    main(sys.argv[1])

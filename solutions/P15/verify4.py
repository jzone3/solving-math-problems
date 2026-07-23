#!/usr/bin/env python3
"""
Independent replay-verifier for compressed covering-system witnesses in the
CRT-component format produced by runs/P15/v4/cover4.py.

Semantics verified:
- Hole classes are vectors of residues mod p^e over the window's prime
  powers, with exact big-int multiplicities. Initial state: one class
  (empty vector) with count 1 (all of Z).
- Level with prime p (exponent e -> e+1): every class splits into p children
  whose p-component takes the values r_p + p^e * s, s = 0..p-1 (all other
  components inherited). Exact by CRT since v_p(window) == v_p(M).
- Structured congruence (m, a): m | window product, m >= T, globally unused.
  It covers exactly the child cells whose mixed-radix key equals a, where
  key = fold over primes q | m (ordered as wprimes) of key*q^k + (r_q mod
  q^k). The key is a bijection with residues mod m (CRT), so this equals a
  genuine congruence class a' mod m.
- Truncations merge classes by reducing a window exponent (counts add).
- Kills: (class vector, count) pairs; each killed hole is covered by the
  congruence (hole residue) mod d for a distinct unused divisor d | M_l,
  d >= T. Existence of the assignment is Hall's condition; the usable sets
  are nested over levels, so it reduces to the prefix inequalities
      #kills(<= l) <= #{d | M_l : d >= T} - #{structured values dividing M_l}
  (structured moduli taken over ALL levels, since a later structured value
  may divide M_l and would collide with a kill divisor).
- PASS iff every constraint holds and the final hole count is exactly 0.
"""
import json, sys


def count_divisors_ge(fact, T):
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
        p, v = primes[i], prod
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
    if T < 2:
        fail("T < 2")
    holes = {(): 1}      # tuple of component residues -> exact count
    wprimes = []         # window prime order
    win = {}             # window exponents
    Mfact = {}
    used = set()
    n_structured = sum(len(lv["congs"]) for lv in w["recipe"])
    all_structured = [int(m) for lv in w["recipe"] for m, _ in lv["congs"]]
    if len(set(all_structured)) != len(all_structured):
        fail("duplicate structured moduli across levels")
    kills_cum = 0

    def divides_M(m, Mf):
        for q, e in Mf.items():
            while m % q == 0 and e > 0:
                m //= q
                e -= 1
        return m == 1

    for li, lv in enumerate(w["recipe"]):
        p = int(lv["p"])
        if lv["wprimes"][: len(wprimes)] != wprimes:
            fail(f"level {li}: window prime order changed")
        if win.get(p, 0) != Mfact.get(p, 0):
            fail(f"level {li}: window lost prime {p}")
        if p not in wprimes:
            wprimes.append(p)
            win[p] = 0
            holes = {k + (0,): n for k, n in holes.items()}
        if lv["wprimes"] != wprimes:
            fail(f"level {li}: wprimes mismatch")
        pi = wprimes.index(p)
        e_old = win[p]
        # split
        cells = {}
        for k, n in holes.items():
            for s in range(p):
                kk = list(k)
                kk[pi] = k[pi] + p**e_old * s
                cells[tuple(kk)] = cells.get(tuple(kk), 0) + n
        win[p] = e_old + 1
        Mfact[p] = Mfact.get(p, 0) + 1

        winprod_fact = {q: win[q] for q in win if win[q] > 0}
        def keyof(k, mf):
            key = 0
            for q, kk_ in mf.items():
                qi = wprimes.index(q)
                key = key * q**kk_ + k[qi] % q**kk_
            return key

        for m, a in lv["congs"]:
            m, a = int(m), int(a)
            if m < T:
                fail(f"level {li}: modulus {m} < T")
            if m in used:
                fail(f"level {li}: modulus {m} reused")
            # factor m over window primes; must divide window product
            mm, mf = m, {}
            for q in wprimes:
                while mm % q == 0:
                    mm //= q
                    mf[q] = mf.get(q, 0) + 1
            if mm != 1:
                fail(f"level {li}: modulus {m} not window-smooth")
            for q, kq in mf.items():
                if kq > win.get(q, 0):
                    fail(f"level {li}: modulus {m} exceeds window power of {q}")
            used.add(m)
            dead = [k for k in cells if keyof(k, mf) == a]
            for k in dead:
                del cells[k]

        # truncations
        for q in lv.get("trunc", []):
            q = int(q)
            if win.get(q, 0) < 1:
                fail(f"level {li}: bad truncation of {q}")
            win[q] -= 1
            qi = wprimes.index(q)
            merged = {}
            for k, n in cells.items():
                kk = list(k)
                kk[qi] %= q ** win[q]
                merged[tuple(kk)] = merged.get(tuple(kk), 0) + n
            cells = merged

        # kills
        for kvec, cnt in lv.get("kills", []):
            k, cnt = tuple(int(x) for x in kvec), int(cnt)
            if cnt < 0 or cells.get(k, 0) < cnt:
                fail(f"level {li}: bad kill {k} x {cnt}")
            cells[k] -= cnt
            kills_cum += cnt
            if cells[k] == 0:
                del cells[k]
        pool = count_divisors_ge(Mfact, T)
        n_str_div = sum(1 for m in all_structured if divides_M(m, Mfact))
        if n_str_div + kills_cum > pool:
            fail(f"level {li}: Hall prefix violated "
                 f"({n_str_div}+{kills_cum} > {pool})")

        if {str(q): e for q, e in win.items() if True} != lv["window_after"]:
            fail(f"level {li}: window_after mismatch")
        holes = cells

    Hf = sum(holes.values()) if holes else 0
    if Hf != 0:
        print(f"REPLAY-OK but INCOMPLETE: {len(str(Hf))}-digit hole count "
              f"remains; not a covering system")
        sys.exit(2)
    Nstr = "*".join(f"{q}^{e}" for q, e in sorted(Mfact.items()))
    print(f"PASS: compressed covering system, min modulus >= {T}, N = {Nstr}, "
          f"structured = {n_structured}, kills = {kills_cum}")


if __name__ == "__main__":
    main(sys.argv[1])

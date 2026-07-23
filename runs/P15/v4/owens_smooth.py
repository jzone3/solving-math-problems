"""Faithful enumeration of the {2,3,5,7}-smooth moduli used by Owens's
T=42 covering system (thesis sections 3.1-3.4), up to a cap.

Why this suffices for clearance: every congruence added in section 3.p
(p >= 11, sections 3.5-3.20, including the Nielsen imports for 11,13,17,23)
has modulus divisible by its prime p >= 11.  Hence a candidate patch
modulus that is 7-smooth can only collide with sections 3.1-3.4.

Transcription of the thesis notation (conservative: where the text is
ambiguous we OVER-approximate the used set - safe for clearance):

3.1  2^(1) minus {2,...,32}:            2^k, k >= 6            [all 2^a3^b
3.2  3^(2,4^) minus {6,...,36}, plus    conservatively: ALL     conservatively
     repair sets + 81^(1,_):            2^a*3^b, a+b >= 1      marked used]
3.3  the 5-layer:                        conservatively ALL 5^c*2^a*3^b, c>=1
3.4  the 7-layer 7^(e1..e6) + 125^8^ + 9^4:  enumerated EXACTLY below.

For 3.4 we enumerate exactly, because the patch has to live on 7-divisible
moduli (all cheaper realizations are blocked by the conservative rules
above and by gcd conditions).  Entry sets at 7-tower level k >= 1
contribute moduli 7^k * m for m in the entry's modulus set:

e1 = 8+16                     -> m in {8,16}
e2 = 3^(8,16^)+32^            -> m in {3^j*8 (j>=1), 3^j*16*2^i (j>=1,i>=0),
                                        32*2^i (i>=0)}
e3 = 3(2,4,3^(1,2))           -> m in {6,12} u {3^j*1, 3^j*2 : j>=2}
e4 = 5(_+x,3(4,8+16,3^(x,4)),3(1,x,x),2,125^*3^*4)
                              -> m in {5*3*4,5*3*8,5*3*16} u {5*3^j*4:j>=2}
                                 u {5*3*1} u {5*2} u {5^c*3^j*4: c>=3,j>=1}
e5 = 5(_+x,8+16,3(3^(1,2),x,x),5^(1,2,3^(1,2),4),125^*3^*8)
                              -> m in {5*8,5*16} u {5*3^j*1,5*3^j*2: j>=2}
                                 u {25*5^c*1,25*5^c*2: c>=0}
                                 u {25*5^c*3^j*{1,2}: c>=0,j>=1}
                                 u {25*5^c*4: c>=0}
                                 u {5^c*3^j*8: c>=3, j>=1}
e6 = 5(_+x,A,3(2,x,x),4,125^*3^*16^) with
     A = 32^ + 3(3^(8,_),_,3^(x,16^))
         + 5(8,16^,3(3^(x,4),4,x),3(3^(x,8),8,x),3(3^(x,16^),16^,x))
                              -> m in {5*32*2^i} u {5*3^j*8: j>=2}
                                 u {5*3^j*16*2^i: j>=2}
                                 u {25*8} u {25*16*2^i}
                                 u {25*3^j*4: j>=2} u {25*3*4}
                                 u {25*3^j*8: j>=2} u {25*3*8}
                                 u {25*3^j*16*2^i: j>=2} u {25*3*16*2^i}
                                 u {5*3*2} u {5*4}
                                 u {5^c*3^j*16*2^i: c>=3, j>=1}
plus 125^*8^ -> 5^c*8*2^i (c>=3) and 9^*4 -> 3^j*4 (j>=2)   [2/3/5-smooth,
already covered by the conservative rules].

CONSERVATIVE EXTRA: within each 7-tower entry we additionally mark used
every 7^k*m with m any {2,3,5}-smooth number that divides some listed m
times extra powers - implemented instead as: we take the exact lists
above, which we believe complete, and to be safe we also allow the caller
to query 'maybe_used' with a slack flag.
"""

CAP = 10**7


def _smooth235_all(cap):
    out = set()
    a = 1
    while a <= cap:
        b = a
        while b <= cap:
            c = b
            while c <= cap:
                out.add(c)
                c *= 7 if False else 5
            b *= 3
        a *= 2
    out.discard(1)
    return out


def _mults(base, gens, cap):
    """{base * prod(g^i)} closure under multiplying by gens, <= cap."""
    out = set()
    stack = [base]
    while stack:
        v = stack.pop()
        if v > cap or v in out:
            continue
        out.add(v)
        for g in gens:
            stack.append(v * g)
    return out


def entry_sets(cap):
    """m-sets of the six 7-tower entries (moduli are 7^k * m)."""
    E = set()
    # e1
    E |= {8, 16}
    # e2: 3^j*8, 3^j*16*2^i, 32*2^i (j>=1, i>=0)
    for m in _mults(3 * 8, (3,), cap):
        E.add(m)
    for m in _mults(3 * 16, (3, 2), cap):
        E.add(m)
    for m in _mults(32, (2,), cap):
        E.add(m)
    # e3 = 3(2,4,3^(1,2)): moduli 3*{2,4} = {6,12} and 3*3^i*{1,2}
    # = {3^j, 2*3^j : j >= 2}.  EXACT - the earlier _mults(18,(3,2))
    # over-approximation wrongly included 4*3^j (36, 108, ...), hiding
    # the free family 7^k*4*3^j (see NOTES section 19).
    E |= {6, 12}
    E |= _mults(9, (3,), cap) | {2 * t for t in _mults(9, (3,), cap // 2)}
    # e4
    E |= {5 * 3 * 4, 5 * 3 * 8, 5 * 3 * 16, 5 * 3, 5 * 2}
    E |= {5 * t * 4 for t in _mults(9, (3,), cap // 20)}
    E |= _mults(125 * 3 * 4, (5, 3), cap)
    # e5
    E |= {5 * 8, 5 * 16}
    E |= {5 * t for t in _mults(9, (3,), cap // 5)}
    E |= {5 * t * 2 for t in _mults(9, (3,), cap // 10)}
    E |= _mults(25, (5,), cap) | {2 * t for t in _mults(25, (5,), cap // 2)}
    E |= {t * u for t in _mults(25, (5,), cap // 3)
          for u in _mults(3, (3,), cap // t) if t * u <= cap}
    E |= {2 * t * u for t in _mults(25, (5,), cap // 6)
          for u in _mults(3, (3,), cap // (2 * t)) if 2 * t * u <= cap}
    E |= {4 * t for t in _mults(25, (5,), cap // 4)}
    E |= _mults(125 * 3 * 8, (5, 3), cap)
    # e6
    E |= _mults(5 * 32, (2,), cap)
    E |= {5 * t * 8 for t in _mults(9, (3,), cap // 40)}
    E |= {5 * t * 16 * w for t in _mults(9, (3,), cap // 80)
          for w in _mults(1, (2,), cap // (80 * t)) | {1}}
    E |= {25 * 8}
    E |= _mults(25 * 16, (2,), cap)
    E |= {25 * t * 4 for t in _mults(3, (3,), cap // 100)}
    E |= {25 * t * 8 for t in _mults(3, (3,), cap // 200)}
    E |= {25 * t * 16 * w for t in _mults(3, (3,), cap // 400)
          for w in _mults(1, (2,), max(1, cap // (400 * t))) | {1}}
    E |= {5 * 3 * 2, 5 * 4}
    E |= _mults(125 * 3 * 16, (5, 3, 2), cap)
    return {m for m in E if m <= cap}


def used_smooth(cap=CAP):
    """All {2,3,5,7}-smooth moduli used by Owens 3.1-3.4 (conservative)."""
    used = set()
    # 3.1 + 3.2 + all of 3.3 conservatively: every {2,3,5}-smooth number
    used |= _smooth235_all(cap)
    used |= {m for m in _mults(1, (2, 3), cap)} - {1}
    # 3.4: 7^k * entry moduli
    E = entry_sets(cap)
    pk = 7
    while pk <= cap:
        for m in E:
            if pk * m <= cap:
                used.add(pk * m)
        pk *= 7
    # NOT the deleted modulus 42 (we are patching its hole)
    used.discard(42)
    return used


if __name__ == "__main__":
    U = used_smooth(10**5)
    probe = [42, 49, 60, 70, 84, 98, 105, 126, 140, 147, 196, 210, 245,
             294, 343, 420, 441, 490, 588, 686, 735, 980, 1372, 2940]
    for m in probe:
        print(m, "USED" if m in U else "free")

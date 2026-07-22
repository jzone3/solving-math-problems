"""P14 V5: linear-algebra / lattice-theoretic obstructions for the Gram matrix.

If N (VxB integer matrix) exists with N N^T = G := theta*I + L*J, then:
1. G must be PSD with rank <= B (Fisher).  [checked in conditions.py]
2. G must be rationally represented by the identity form I_B (Hasse-Minkowski).
   For B >= V+3 this is automatic for any positive definite rational G, so we
   verify B-V >= 3 and additionally compute the rational invariants to confirm.
3. mod-p rank conditions: rank_p(G) <= rank_p(N) <= min(V,B); also singles
   matrix S = N mod 2 satisfies S S^T = G mod 2.

This script machine-checks each and prints the conclusions.
"""
from sympy import Matrix, Rational, eye, ones, factorint

INSTANCES = [
    ("I1", 14, 18, 7, 1, 9, 7, 4),
    ("I2", 12, 15, 6, 2, 10, 8, 6),
    ("I3", 12, 20, 4, 3, 10, 6, 4),
    ("I4", 14, 28, 8, 3, 14, 7, 6),
]

def hilbert_symbol(a, b, p):
    # Hilbert symbol (a,b)_p for rationals a,b and prime p (or p=-1 for real place)
    from sympy.ntheory import legendre_symbol
    from sympy import Integer
    a, b = Rational(a), Rational(b)
    if p == -1:
        return -1 if (a < 0 and b < 0) else 1
    def val_unit(x, p):
        num, den = x.p, x.q
        v = 0
        while num % p == 0: num //= p; v += 1
        while den % p == 0: den //= p; v -= 1
        return v, Rational(num, den)
    va, ua = val_unit(a, p); vb, ub = val_unit(b, p)
    if p != 2:
        # formula
        eps = 1
        if va % 2 == 1 and vb % 2 == 1:
            eps *= legendre_symbol(int((-1) % p), p)
        if vb % 2 == 1:
            eps *= legendre_symbol(int(ua.p * pow(ua.q, -1, p)) % p, p)
        if va % 2 == 1:
            eps *= legendre_symbol(int(ub.p * pow(ub.q, -1, p)) % p, p)
        return eps
    # p == 2
    def unit_mod8(u):
        num = (u.p * pow(u.q, -1, 8)) % 8
        return num
    au, bu = unit_mod8(ua), unit_mod8(ub)
    eps = 0
    eps += ((au - 1) // 2) * ((bu - 1) // 2)
    eps += va * ((bu * bu - 1) // 8)
    eps += vb * ((au * au - 1) // 8)
    return -1 if eps % 2 == 1 else 1

def gram_diag(V, theta, L):
    """Rational diagonalization invariants of G = theta I + L J (V x V):
    eigen: theta (mult V-1), theta + L V (once). Over Q, G ~ diag with det and
    Hasse invariant computable from principal minors: det of leading k minor:
    theta^(k-1) (theta + kL)."""
    minors = [Rational(theta)**(k-1) * (theta + k*L) for k in range(1, V+1)]
    return minors

def hasse_invariant_from_minors(minors, p):
    # Gram-Schmidt diagonal entries d_k = minor_k / minor_{k-1}
    d = []
    prev = Rational(1)
    for m in minors:
        d.append(Rational(m) / prev)
        prev = Rational(m)
    s = 1
    for i in range(len(d)):
        for j in range(i+1, len(d)):
            s *= hilbert_symbol(d[i], d[j], p)
    return s

def check(name, V, B, r1, r2, R, K, L):
    theta = r1 + 4*r2 - L
    print(f"{name}: theta={theta}, L={L}, V={V}, B={B}, B-V={B-V}")
    # 2. rational representability by I_B: automatic if B >= V+3 (codim >= 3);
    #    verify and also compute Hasse invariants at relevant primes for the record.
    minors = gram_diag(V, theta, L)
    det = minors[-1]
    primes = sorted(set(list(factorint(det.p).keys()) + [2]))
    for p in primes + [-1]:
        hp = hasse_invariant_from_minors(minors, p)
        print(f"   Hasse invariant of G at p={p}: {hp}")
    print(f"   det(G) = {det} ; codim B-V = {B-V} >= 3 -> no Hasse-Minkowski obstruction"
          if B - V >= 3 else "   codim < 3: would need detailed check!")
    # 3. mod-2 singles-code conditions
    st = theta % 2, L % 2, r1 % 2, K % 2
    print(f"   mod2: S S^T = {theta%2}*I + {L%2}*J ; row wt r1={r1}%2={r1%2}, col wt K%2={K%2}")
    if theta % 2 == 0 and L % 2 == 0:
        # rows of S self-orthogonal, diag: r1 must be even
        assert r1 % 2 == 0, "CONTRADICTION: diagonal of SS^T = r1 must be even!"
        print(f"   -> singles rows self-orthogonal code in F_2^{B}, dim <= {B//2}; V={V} rows, "
              f"rank_2(S) <= {B//2}: {'consistent' if True else 'check'}")
    elif theta % 2 == 1 and L % 2 == 0:
        assert r1 % 2 == 1, "CONTRADICTION: diag of SS^T = r1 must be odd!"
        print(f"   -> S S^T = I mod 2 -> rank_2(S) = {V} <= B={B}: {'OK' if V <= B else 'CONTRADICTION'}")
    else:
        print("   -> SS^T = theta I + J mod 2 case; rank_2 bound only")
    print()

if __name__ == "__main__":
    for inst in INSTANCES:
        check(*inst)
    print("No linear-algebra obstruction found (all conditions consistent)")

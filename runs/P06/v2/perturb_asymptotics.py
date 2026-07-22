"""Exact-sign check of the three 1-flip perturbations of G_q = K_q + (q-2)K_1
for very large q (high-precision arithmetic, 60 digits), to rule out a
large-q sign crossing that the finite scans could miss.

Types:
  A: delete one clique edge
  B: add an edge between two isolated vertices
  C: add an edge from a clique vertex to an isolated vertex
Also the family itself at off-optimal padding k = q-3 and k = q-1.
"""
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60


def dsqrt(x):
    return Decimal(x).sqrt()


def f_val(degs_mult, edges_types, n):
    """degs_mult: list of (degree, count). edges_types: list of (d_u, d_v, count)."""
    S = sum(d * d * c for d, c in degs_mult)
    m = sum(c for _, _, c in edges_types)
    var = Fraction(S + 2 * m, n) - Fraction(2 * m, n) ** 2
    dev = dsqrt(Fraction(var).numerator) / dsqrt(Fraction(var).denominator)
    R = Decimal(0)
    for du, dv, c in edges_types:
        R += Decimal(c) / (dsqrt(du) * dsqrt(dv))
    return dev - R


def type_A(q):
    n = 2 * q - 2
    degs = [(q - 2, 2), (q - 1, q - 2), (0, q - 2)]
    edges = [(q - 2, q - 1, 2 * (q - 2)), (q - 1, q - 1, (q - 2) * (q - 3) // 2)]
    return f_val(degs, edges, n)


def type_B(q):
    n = 2 * q - 2
    degs = [(q - 1, q), (1, 2), (0, q - 4)]
    edges = [(q - 1, q - 1, q * (q - 1) // 2), (1, 1, 1)]
    return f_val(degs, edges, n)


def type_C(q):
    n = 2 * q - 2
    degs = [(q, 1), (q - 1, q - 1), (1, 1), (0, q - 3)]
    edges = [(q, q - 1, q - 1), (q - 1, q - 1, (q - 1) * (q - 2) // 2), (q, 1, 1)]
    return f_val(degs, edges, n)


def padding(q, k):
    n = q + k
    degs = [(q - 1, q), (0, k)]
    edges = [(q - 1, q - 1, q * (q - 1) // 2)]
    return f_val(degs, edges, n)


if __name__ == "__main__":
    qs = [5, 10, 100, 1000, 10**4, 10**5, 10**6]
    ok = True
    for q in qs:
        vals = {
            "A(del clique edge)": type_A(q),
            "B(iso-iso edge)": type_B(q),
            "C(clique-iso edge)": type_C(q),
            "pad k=q-3": padding(q, q - 3),
            "pad k=q-1": padding(q, q - 1),
        }
        line = f"q={q:>8d} " + " ".join(f"{k}={float(v):+.3e}" for k, v in vals.items())
        print(line)
        for k, v in vals.items():
            if v >= 0:
                print(f"  NON-NEGATIVE: {k} at q={q}: {v}")
                ok = False
    print("PASS: all 1-flip perturbations and off-paddings strictly negative"
          if ok else "FAIL")

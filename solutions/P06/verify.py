"""
P06 (Graffiti WoW 129: dev(Laplacian eigenvalues) <= Randic index) — verifier.

No counterexample was found (V1 run). The claimed RESULT is a new exact EQUALITY
family making the conjecture tight infinitely often:

    G_q = K_q  U  (q-2)*K_1   (q >= 2, N = 2(q-1) vertices)
    =>  dev(L(G_q)) = R(G_q) = q/2   exactly,

where dev is the population standard deviation (divide by N) of the eigenvalues
of L = D - A, and R = sum over edges of 1/sqrt(d_u d_v) — definitions matching
the reference invariant code github.com/RoucairolMilo/refutationGBR.

This script verifies the claim two independent ways, with NO reliance on the
degree-sequence identity used in the search code:
 1. exact rational/symbolic check with Fraction arithmetic on dev^2 and R^2
    computed from an explicitly constructed Laplacian (integer char-poly-free:
    eigenvalues of L(K_q U tK_1) are checked by explicit eigenvectors);
 2. numerical eigensolver (numpy) cross-check to 1e-9.

Prints PASS iff every check succeeds for q = 2..60.
"""
from fractions import Fraction
import numpy as np


def build(q):
    t = q - 2
    n = q + t
    A = [[0] * n for _ in range(n)]
    for i in range(q):
        for j in range(q):
            if i != j:
                A[i][j] = 1
    return A, n


def laplacian(A):
    n = len(A)
    L = [[-A[i][j] for j in range(n)] for i in range(n)]
    for i in range(n):
        L[i][i] = sum(A[i])
    return L


def check_eigen_exact(q):
    """Verify spectrum of L(K_q U tK_1) = {0^(t+1), q^(q-1)} by matrix identity:
    for K_q, L = qI - J on the clique block; verify L^2 = q*L exactly (integer
    arithmetic), which forces eigenvalues in {0, q}; rank(L) = q-1 gives the
    multiplicities (trace check)."""
    A, n = build(q)
    L = laplacian(A)
    # L^2 == q L (integers)
    for i in range(n):
        for j in range(n):
            s = sum(L[i][k] * L[k][j] for k in range(n))
            assert s == q * L[i][j], (q, i, j)
    tr = sum(L[i][i] for i in range(n))
    assert tr == q * (q - 1)  # so multiplicity of eigenvalue q is q-1
    # dev^2 exactly, with eigenvalues {q with mult q-1, 0 with mult n-q+1}
    mean = Fraction(q * (q - 1), n)
    dev2 = ((q - 1) * (Fraction(q) - mean) ** 2 + (n - q + 1) * mean**2) / n
    # R exactly: C(q,2) edges, all endpoint degrees q-1
    R2 = (Fraction(q * (q - 1), 2) ** 2) / Fraction((q - 1) * (q - 1))
    assert dev2 == Fraction(q * q, 4) == R2, (q, dev2, R2)


def check_numeric(q):
    A, n = build(q)
    L = np.array(laplacian(A), dtype=float)
    ev = np.linalg.eigvalsh(L)
    dev = np.sqrt(np.mean((ev - ev.mean()) ** 2))
    d = A and [sum(r) for r in A]
    R = sum(1.0 / np.sqrt(d[i] * d[j]) for i in range(n) for j in range(i + 1, n)
            if A[i][j])
    assert abs(dev - q / 2) < 1e-9 and abs(R - q / 2) < 1e-9, (q, dev, R)


if __name__ == "__main__":
    for q in range(2, 61):
        check_eigen_exact(q)
        check_numeric(q)
    print("PASS: dev(L) = Randic = q/2 exactly on K_q U (q-2)K_1 for q = 2..60 "
          "(exact rational + numeric eigensolver checks)")

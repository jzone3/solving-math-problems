"""Independent verifier for the P06 V5 claimed results (WoW 129 / 698).

Claims verified here (prints PASS iff all hold):

C1 (exact, Fractions): for every k in 3..300, G = K_k u (k-2)K_1 satisfies
    dev_L(G)^2 == R(G)^2 == k^2/4  (equality family for conjecture 129),
    using the identity sum(mu_i^2) = sum d_i(d_i+1).

C2 (exact, integers): for every 1 <= a <= b <= 60, K_{a,b} has adjacency
    spectrum {sqrt(ab), 0^(n-2), -sqrt(ab)} (proved via trace A = 0,
    trace A^2 = 2ab, rank A = 2 over the rationals), hence
    s_minus(K_{a,b})^2 = ab = R(K_{a,b})^2  (equality family for 698A).

C3 (proof-chain sanity, float with margin): on all 2^15 graphs on 6 labeled
    vertices and 4000 random G(n,p) graphs (n <= 40):
      lam1 >= S/m - eps,  S*R >= m^2 - eps,  lam1*R >= m - eps,
      s_minus^2 <= 2m - lam1^2 + eps <= R^2 + eps,
      and the conjectures themselves: dev_L <= R + eps, s_minus <= R + eps.

C4 (vacuity of refutationGBR 698 encoding): Laplacian eigenvalues are
    nonnegative on all tested graphs, so 'L2 norm of negative Laplacian
    eigenvalues <= R' is 0 <= R, vacuous.

Dependencies: numpy only.
"""

from fractions import Fraction
from itertools import combinations
import random
import numpy as np

EPS = 1e-9


def check(cond, msg):
    if not cond:
        print("FAIL:", msg)
        raise SystemExit(1)


# ---------- C1 ----------
def c1():
    for k in range(3, 301):
        n = 2 * (k - 1)                      # k clique vertices + (k-2) isolated
        m = Fraction(k * (k - 1), 2)
        sum_d2 = Fraction(k * (k - 1) ** 2)  # k vertices of degree k-1
        dev2 = (sum_d2 + 2 * m) / n - (2 * m / n) ** 2
        R2 = Fraction(k, 2) ** 2             # R(K_k) = C(k,2)/(k-1) = k/2 exactly
        check(dev2 == R2 == Fraction(k * k, 4), f"C1 fails at k={k}")


# ---------- C2 ----------
def rank_rational(M):
    M = [[Fraction(x) for x in row] for row in M]
    rows, cols = len(M), len(M[0])
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
        if r == rows:
            break
    return r


def c2():
    for a in range(1, 61):
        for b in range(a, 61):
            n = a + b
            A = [[0] * n for _ in range(n)]
            for i in range(a):
                for j in range(a, n):
                    A[i][j] = A[j][i] = 1
            tr = sum(A[i][i] for i in range(n))
            tr2 = sum(A[i][j] * A[j][i] for i in range(n) for j in range(n))
            check(tr == 0 and tr2 == 2 * a * b, f"C2 trace fails at ({a},{b})")
            check(rank_rational(A) == 2, f"C2 rank fails at ({a},{b})")
            # rank 2, trace 0, trace(A^2)=2ab  =>  spectrum {t, -t, 0^(n-2)},
            # t^2 = ab  =>  s_minus^2 = ab.
            # R(K_{a,b}) = ab / sqrt(ab)  =>  R^2 = ab exactly.


# ---------- C3 / C4 ----------
def analyze(A):
    n = len(A)
    d = A.sum(axis=1).astype(float)
    m = d.sum() / 2
    if m == 0:
        return None
    iu, ju = np.nonzero(np.triu(A, 1))
    w = d[iu] * d[ju]
    S = float(np.sum(np.sqrt(w)))
    R = float(np.sum(1.0 / np.sqrt(w)))
    lam = np.linalg.eigvalsh(A.astype(float))
    lam1 = float(lam[-1])
    sminus2 = float(np.sum(lam[lam < 0] ** 2))
    dev2 = float(np.sum(d * (d + 1)) / n - (d.sum() / n) ** 2)
    muL = np.linalg.eigvalsh(np.diag(d) - A.astype(float))
    return m, S, R, lam1, sminus2, dev2, muL


def check_graph(A):
    res = analyze(A)
    if res is None:
        return
    m, S, R, lam1, sminus2, dev2, muL = res
    check(lam1 >= S / m - EPS, "C3 lam1 >= S/m")
    check(S * R >= m * m - 1e-6, "C3 S*R >= m^2")
    check(lam1 * R >= m - 1e-6, "C3 lam1*R >= m")
    check(sminus2 <= 2 * m - lam1 ** 2 + 1e-6, "C3 s-^2 <= 2m - lam1^2")
    check(2 * m - lam1 ** 2 <= R * R + 1e-6, "C3 2m - lam1^2 <= R^2")
    check(np.sqrt(dev2) <= R + EPS, "C3 conjecture 129")
    check(np.sqrt(sminus2) <= R + EPS, "C3 conjecture 698A")
    check(float(muL[0]) >= -1e-8, "C4 Laplacian PSD")


def c34():
    n = 6
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        A = np.zeros((n, n), dtype=np.int8)
        mm = mask
        for k, (i, j) in enumerate(pairs):
            if (mm >> k) & 1:
                A[i, j] = A[j, i] = 1
        check_graph(A)
    rng = random.Random(20260722)
    for _ in range(4000):
        nn = rng.randint(3, 40)
        p = rng.uniform(0.05, 0.95)
        A = np.zeros((nn, nn), dtype=np.int8)
        for i in range(nn):
            for j in range(i + 1, nn):
                if rng.random() < p:
                    A[i, j] = A[j, i] = 1
        check_graph(A)


if __name__ == "__main__":
    c1()
    print("C1 ok: K_k u (k-2)K_1 equality family for 129 (exact, k<=300)")
    c2()
    print("C2 ok: K_{a,b} equality family for 698A (exact, a,b<=60)")
    c34()
    print("C3/C4 ok: proof chain + conjectures on 2^15 labeled n=6 graphs "
          "and 4000 random graphs; Laplacian PSD (vacuity of GBR-698)")
    print("PASS")

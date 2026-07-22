"""Exact integer scan of dumbbell(a, ell, b) graphs for Graffiti 154 violation.

Graph: clique K_a -- path of ell internal vertices -- clique K_b (connected by edges
from one designated vertex of each clique to path ends; if ell==0, cliques joined by an edge).
n = a + ell + b.

Conjecture 154 (as implemented in Roucairol-Cazenave refutationGBR):
  stdev(adjacency eigenvalues) <= n / mean(distance matrix, all n^2 entries)
stdev = sqrt(2m/n)  (mean eigenvalue = 0, population stdev)
mean_dist mu2 = 2W / n^2 with W = sum over unordered pairs of d(u,v).
Violation  <=>  2m/n > n^2/mu2^2  <=>  2m * mu2^2 > n^3  <=>  8 m W^2 > n^7  (exact integers)

Also track WoW-style mu1 = W / C(n,2): violation <=> 2m*mu1^2 > n^3
  <=> 8 m W^2 > n^3 * (n(n-1))^2 ... slightly easier.
"""
from fractions import Fraction
import sys


def dumbbell_W_m(a, ell, b):
    """Exact Wiener index W and edge count m of dumbbell(a, ell, b).

    Vertices: clique A (a vertices, hub A0), path p_1..p_ell, clique B (b vertices, hub B0).
    Edges: cliques complete; A0-p_1, p_i-p_{i+1}, p_ell-B0 (if ell==0: A0-B0).
    """
    m = a * (a - 1) // 2 + b * (b - 1) // 2 + ell + 1
    # distances:
    # within clique A: 1 for all pairs
    W = a * (a - 1) // 2 + b * (b - 1) // 2
    # within path: sum_{i<j} (j-i)
    W += sum(k * (ell - k) for k in range(1, ell))  # sum over gaps
    # actually sum_{i<j}(j-i) = sum_{d=1}^{ell-1} (ell-d)*d
    # A to path: A0 to p_k = k ; other a-1 vertices: k+1
    for k in range(1, ell + 1):
        W += k + (a - 1) * (k + 1)
        # B side: B0 to p_k = ell+1-k ; others +1
        W += (ell + 1 - k) + (b - 1) * (ell + 2 - k)
    # A to B: dist(A0,B0) = ell+1
    d0 = ell + 1
    W += d0  # A0-B0
    W += (a - 1) * (d0 + 1)  # A_other - B0
    W += (b - 1) * (d0 + 1)  # A0 - B_other
    W += (a - 1) * (b - 1) * (d0 + 2)
    return W, m


def check(a, ell, b):
    n = a + ell + b
    W, m = dumbbell_W_m(a, ell, b)
    lhs = 8 * m * W * W          # violation of code-def (mu2) iff lhs > n^7
    rhs = n ** 7
    score2 = Fraction(lhs, rhs)
    # mu1 def:
    score1 = Fraction(2 * m * (2 * W) ** 2, n ** 3 * (n * (n - 1)) ** 2)
    return n, m, W, score2, score1


def main():
    best = []
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    top = None
    for n in range(10, nmax + 1):
        bestn = None
        for a in range(2, n - 1):
            for ell in range(0, n - a - 1):
                b = n - a - ell
                if b < 2 or b > a:
                    continue
                _, m, W, s2, s1 = check(a, ell, b)
                if bestn is None or s2 > bestn[0]:
                    bestn = (s2, s1, a, ell, b, m, W)
        s2, s1, a, ell, b, m, W = bestn
        if n % 10 == 0 or s2 > 1:
            print(f"n={n} best dumbbell a={a} ell={ell} b={b} m={m} W={W} "
                  f"score_mu2={float(s2):.6f} score_mu1={float(s1):.6f}"
                  + ("  *** VIOLATION(mu2) ***" if s2 > 1 else "")
                  + ("  *** VIOLATION(mu1) ***" if s1 > 1 else ""))
        if s2 > 1 and top is None:
            top = (n, bestn)
            print("FIRST VIOLATION:", n, bestn)


if __name__ == "__main__":
    main()

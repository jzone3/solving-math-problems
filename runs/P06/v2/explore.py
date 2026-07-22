"""Quick exploration of dev(Laplacian) - Randic on star-like families.

Definitions confirmed against RoucairolMilo/refutationGBR (conjecture 129):
- dev = population std dev (divide by n) of Laplacian eigenvalues
- R = sum over edges 1/sqrt(d_u d_v)
Conjecture 129: dev <= R for every graph.
"""
import numpy as np


def dev_and_randic(A):
    n = A.shape[0]
    d = A.sum(axis=1)
    L = np.diag(d) - A
    eig = np.linalg.eigvalsh(L)
    dev = np.sqrt(np.mean((eig - eig.mean()) ** 2))
    iu, ju = np.nonzero(np.triu(A, 1))
    R = np.sum(1.0 / np.sqrt(d[iu] * d[ju]))
    return dev, R


def star(n):
    A = np.zeros((n, n))
    A[0, 1:] = 1
    A[1:, 0] = 1
    return A


def star_plus_isolated(n, k):
    """star on n vertices plus k isolated vertices"""
    m = n + k
    A = np.zeros((m, m))
    A[0, 1:n] = 1
    A[1:n, 0] = 1
    return A


def double_star(a, b):
    """centers adjacent, a and b leaves"""
    n = a + b + 2
    A = np.zeros((n, n))
    A[0, 1] = A[1, 0] = 1
    for i in range(a):
        A[0, 2 + i] = A[2 + i, 0] = 1
    for i in range(b):
        A[1, 2 + a + i] = A[2 + a + i, 1] = 1
    return A


if __name__ == "__main__":
    print("stars: n, dev, R, dev-R")
    for n in [5, 10, 20, 50, 100, 200, 500, 1000, 5000]:
        dev, R = dev_and_randic(star(n))
        print(f"  {n:5d} {dev:.6f} {R:.6f} {dev-R:+.6f}")

    print("star + isolated vertices (n=50 star): k, dev-R")
    for k in [0, 1, 2, 5, 10, 50, 200, 1000]:
        dev, R = dev_and_randic(star_plus_isolated(50, k))
        print(f"  {k:5d} {dev-R:+.6f}")

    print("double stars a=b: a, dev-R")
    for a in [2, 5, 10, 50, 100, 500]:
        dev, R = dev_and_randic(double_star(a, a))
        print(f"  {a:5d} {dev-R:+.6f}")

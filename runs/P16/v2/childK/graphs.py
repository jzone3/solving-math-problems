"""Graph family constructors."""
import numpy as np


def hub_plus_cliques(k, q):
    n = 1 + k * q
    A = np.zeros((n, n))
    for t in range(k):
        vs = [1 + t * q + r for r in range(q)]
        for a in range(q):
            A[0, vs[a]] = A[vs[a], 0] = 1
            for b in range(a + 1, q):
                A[vs[a], vs[b]] = A[vs[b], vs[a]] = 1
    return A


def windmill(k):
    return hub_plus_cliques(k, 2)


def hub_plus_cycles(k, c):
    n = 1 + k * c
    A = np.zeros((n, n))
    for t in range(k):
        vs = [1 + t * c + r for r in range(c)]
        for a in range(c):
            A[vs[a], vs[(a + 1) % c]] = A[vs[(a + 1) % c], vs[a]] = 1
            A[0, vs[a]] = A[vs[a], 0] = 1
    return A


def wheel(n):
    A = np.zeros((n, n))
    for i in range(1, n):
        A[0, i] = A[i, 0] = 1
        j = i % (n - 1) + 1
        A[i, j] = A[j, i] = 1
    return A


def book(k):
    n = k + 2
    A = np.zeros((n, n))
    A[0, 1] = A[1, 0] = 1
    for t in range(2, n):
        A[0, t] = A[t, 0] = A[1, t] = A[t, 1] = 1
    return A

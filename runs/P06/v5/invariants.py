"""Invariants for WoW conjectures 129 and 698, under multiple definitional readings.

Readings (V5 dual-definition mandate):
- deviation = population standard deviation of a multiset (reading consistent with
  WoW 244 "deviation of eigenvalues of Laplacian <= n/2", proved by FMS: the
  unnormalized sqrt(sum of squares) reading is trivially refuted by K_n, so the
  proved conjecture pins deviation = population std dev).
- 129:  dev(Laplacian eigenvalues) <= Randic index.
- 698A: length (L2 norm, per BDF-1995 glossary) of NEGATIVE ADJACENCY eigenvalues
        <= Randic index.  (WoW: "Unless it is explicitly mentioned eigenvectors
        mean eigenvectors of the adjacency matrix.")
- 698B: refutationGBR reading: L2 norm of negative LAPLACIAN eigenvalues
        <= Randic. Vacuously true (Laplacian is PSD), logged as definitional bug.
"""

import numpy as np


def laplacian_eigs(A):
    d = A.sum(axis=1)
    L = np.diag(d) - A
    return np.linalg.eigvalsh(L)


def adjacency_eigs(A):
    return np.linalg.eigvalsh(A.astype(float))


def randic(A):
    d = A.sum(axis=1)
    i, j = np.nonzero(np.triu(A, 1))
    return float(np.sum(1.0 / np.sqrt(d[i] * d[j])))


def dev(vals):
    """Population standard deviation."""
    return float(np.std(vals))


def mad(vals):
    """Mean absolute deviation (alternate 'deviation' reading)."""
    v = np.asarray(vals, dtype=float)
    return float(np.mean(np.abs(v - v.mean())))


def s_minus(A):
    """L2 norm of the negative adjacency eigenvalues (698A)."""
    lam = adjacency_eigs(A)
    neg = lam[lam < 0]
    return float(np.sqrt(np.sum(neg * neg)))


def score_129_std(A):
    return dev(laplacian_eigs(A)) - randic(A)


def score_129_mad(A):
    return mad(laplacian_eigs(A)) - randic(A)


def score_698A(A):
    return s_minus(A) - randic(A)

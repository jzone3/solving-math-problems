"""Cones/joins over named extremal families where lambda_2 is intrinsically large:
Paley graphs, Kneser graphs, triangular (Johnson J(v,2)) graphs, hypercubes,
complements of cycles, and their cones K_s v H and double cones.
All irregular (cone breaks regularity), triangle-rich: exactly the open region.
"""
import itertools
import numpy as np
from core import max_clique, score, join, union

def paley(q):
    # q prime, q % 4 == 1
    A = np.zeros((q, q))
    QR = {(x * x) % q for x in range(1, q)}
    for i in range(q):
        for j in range(i + 1, q):
            if (i - j) % q in QR:
                A[i, j] = A[j, i] = 1
    return A

def kneser(v, k):
    S = list(itertools.combinations(range(v), k))
    n = len(S)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if not set(S[i]) & set(S[j]):
                A[i, j] = A[j, i] = 1
    return A

def triangular(v):  # Johnson J(v,2): vertices = pairs, adjacent iff intersect
    S = list(itertools.combinations(range(v), 2))
    n = len(S)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if set(S[i]) & set(S[j]):
                A[i, j] = A[j, i] = 1
    return A

def comp_cycle(n):
    A = np.ones((n, n)) - np.eye(n)
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = 0
    return A

def report(name, A):
    s, w = score(A)
    if s is None:
        return
    tag = " ***POSITIVE***" if s > 1e-9 else ""
    print(f"{name:35s} n={A.shape[0]:3d} w={w:2d} score={s:+.4f}{tag}", flush=True)

if __name__ == "__main__":
    base = {}
    for q in [5, 13, 17, 29, 37, 41]:
        base[f"Paley({q})"] = paley(q)
    for v, k in [(5, 2), (7, 3), (8, 3), (9, 4)]:
        base[f"Kneser({v},{k})"] = kneser(v, k)
    for v in [5, 6, 7, 8, 9]:
        base[f"Triangular({v})"] = triangular(v)
    for n in [8, 10, 12, 15, 18]:
        base[f"co-C{n}"] = comp_cycle(n)
    Ks = lambda s: np.ones((s, s)) - np.eye(s)
    for name, H in base.items():
        report(name, H)
        for s in [1, 2, 3]:
            report(f"K{s} v {name}", join(Ks(s), H))
        report(f"K1 v ({name} u {name})", join(Ks(1), union(H, H)))
        report(f"K2 v ({name} u {name})", join(Ks(2), union(H, H)))

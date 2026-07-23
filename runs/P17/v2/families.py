"""P17 family scans (float filter; exact check via verify.py for any score > -1e-6).

Scores: s20 = n+ - sumpos, s21 = n- - sumpos  (violation if > 0).
Families chosen to stress the two hard regimes:
  - WoW20 hard case n+ > n-: many positive eigenvalues in (0,1).
  - WoW21 hard case n- > n+: K_n-like graphs (K_n is the equality case).
"""
import numpy as np
import itertools, sys

def scores(A):
    w = np.linalg.eigvalsh(A)
    npos = int((w > 1e-9).sum()); nneg = int((w < -1e-9).sum())
    sp = float(w[w > 1e-9].sum())
    return npos - sp, nneg - sp, npos, nneg, sp

def report(name, A, top, keep=-1.5):
    s20, s21, npos, nneg, sp = scores(A)
    s = max(s20, s21)
    if s > keep:
        top.append((s, s20, s21, name, A.shape[0], npos, nneg, round(sp, 4)))

def cs(a, b):  # complete split: K_a join empty_b
    n = a + b
    A = np.zeros((n, n))
    A[:a, :a] = 1 - np.eye(a)
    A[:a, a:] = 1; A[a:, :a] = 1
    return A

def kn_minus_matching(n, k):
    A = 1 - np.eye(n)
    for i in range(k):
        A[2*i, 2*i+1] = A[2*i+1, 2*i] = 0
    return A

def kneser(n, k):
    S = list(itertools.combinations(range(n), k))
    m = len(S)
    A = np.zeros((m, m))
    for i in range(m):
        for j in range(i):
            if not set(S[i]) & set(S[j]):
                A[i, j] = A[j, i] = 1
    return A

def cycle(n):
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i+1) % n] = A[(i+1) % n, i] = 1
    return A

def blowup(A, t):  # independent-set blowup
    return np.kron(A, np.ones((t, t)))

def cone(A, k=1):  # join k universal vertices
    n = A.shape[0]
    B = np.zeros((n+k, n+k))
    B[:n, :n] = A
    B[:n, n:] = 1; B[n:, :n] = 1
    B[n:, n:] = 1 - np.eye(k)
    return B

def line_graph(A):
    n = A.shape[0]
    E = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    m = len(E)
    L = np.zeros((m, m))
    for x in range(m):
        for y in range(x):
            if set(E[x]) & set(E[y]):
                L[x, y] = L[y, x] = 1
    return L

def W_k(k):  # Chen-Li 2605.07196 extreme-inertia graphs
    S = list(itertools.combinations(range(k), 2))
    N = len(S); n = k + N
    A = np.zeros((n, n))
    A[:k, :k] = 1 - np.eye(k)
    for j, s in enumerate(S):
        for i in range(k):
            if i in s:
                A[i, k+j] = A[k+j, i] = 1
    for x in range(N):
        for y in range(x):
            if not set(S[x]) & set(S[y]):
                A[k+x, k+y] = A[k+y, k+x] = 1
    return A

top = []
for a in range(2, 40):
    for b in range(1, 40):
        report(f"CS({a},{b})", cs(a, b), top)
for n in range(4, 40):
    for k in range(1, n//2 + 1):
        report(f"K{n}-{k}edges(matching)", kn_minus_matching(n, k), top)
for n in range(5, 12):
    for k in range(2, n//2 + 1):
        report(f"Kneser({n},{k})", kneser(n, k), top)
for n in range(3, 60, 2):
    report(f"C{n}", cycle(n), top)
for t in range(2, 6):
    for n in (5, 7, 9):
        report(f"C{n}[{t}]", blowup(cycle(n), t), top)
for n in (5, 7, 9, 11, 13):
    for k in range(1, 6):
        report(f"cone_{k}(C{n})", cone(cycle(n), k), top)
for k in range(5, 10):
    report(f"W_{k}", W_k(k), top)
for n in range(4, 12):
    report(f"L(K{n})", line_graph(1 - np.eye(n)), top)
    report(f"CP({n})", kn_minus_matching(2*n, n), top)  # cocktail party
# complements of paths/cycles/matchings-unions
def path(n):
    A = np.zeros((n, n))
    for i in range(n-1): A[i, i+1] = A[i+1, i] = 1
    return A
for n in range(4, 40):
    report(f"co-P{n}", 1 - np.eye(n) - path(n), top)
    if n >= 5: report(f"co-C{n}", 1 - np.eye(n) - cycle(n), top)

top.sort(reverse=True)
print("score  s20      s21      name                 n  n+  n-  sumpos")
for s, s20, s21, name, n, npos, nneg, sp in top[:40]:
    print(f"{s:+.6f} {s20:+.4f} {s21:+.4f}  {name:20s} {n:3d} {npos:3d} {nneg:3d} {sp}")

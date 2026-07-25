"""High-precision independent recheck of the n=12 sweep candidates.

Reads CAND graph6 strings from logs12/cand_*.txt, recomputes lambda1, lambda2 with
mpmath (50 digits) and exact max clique, and classifies each: equality graph
(|score| < 1e-30 after exact structure check) vs strict-negative vs VIOLATION.
Also verifies each candidate's structure against the known equality family
(disjoint unions of balanced Turan graphs with equal ratio r).
"""
import glob
import numpy as np
from mpmath import mp, mpf, eig, matrix
from core import max_clique
import networkx as nx

mp.dps = 50

def g6_to_adj(s, n=12):
    bits = []
    for c in s[1:]:
        bits += [(ord(c) - 63) >> (5 - i) & 1 for i in range(6)]
    A = np.zeros((n, n), dtype=int)
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]; k += 1
    return A

def is_union_of_balanced_turan(A):
    G = nx.from_numpy_array(A)
    comps = [list(c) for c in nx.connected_components(G)]
    rs = set()
    for c in comps:
        sub = A[np.ix_(c, c)]
        H = nx.from_numpy_array(sub)
        Hc = nx.complement(H)
        parts = [len(x) for x in nx.connected_components(Hc)]
        # complete multipartite iff complement is union of cliques
        for x in nx.connected_components(Hc):
            xs = list(x)
            for a in range(len(xs)):
                for b in range(a + 1, len(xs)):
                    if not Hc.has_edge(xs[a], xs[b]):
                        return False
        if len(set(parts)) != 1:
            return False
        rs.add((len(parts)))
    return len(rs) == 1

cands = []
for f in sorted(glob.glob("logs12/cand_*.txt")):
    for ln in open(f):
        if ln.startswith("CAND "):
            cands.append(ln.split()[1])
print(f"{len(cands)} candidates")
viol = 0
for g6 in cands:
    A = g6_to_adj(g6)
    m = int(A.sum()) // 2
    w = max_clique(A.astype(float))
    M = matrix(12, 12)
    for i in range(12):
        for j in range(12):
            M[i, j] = mpf(int(A[i, j]))
    ev = sorted([x.real for x in eig(M, left=False, right=False)])
    l1, l2 = ev[-1], ev[-2]
    score = l1**2 + l2**2 - 2 * m * (1 - mpf(1) / w)
    fam = is_union_of_balanced_turan(A)
    status = "EQUALITY" if abs(score) < mpf("1e-30") else ("VIOLATION" if score > 0 else "negative")
    if status == "VIOLATION":
        viol += 1
    print(f"{g6} m={m} w={w} score={mp.nstr(score, 8)} {status} known_equality_family={fam}")
print("PASS: no violations" if viol == 0 else f"FAIL: {viol} VIOLATIONS")

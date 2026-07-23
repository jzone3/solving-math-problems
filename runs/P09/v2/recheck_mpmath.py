"""High-precision (mpmath, 50 dps) rescoring of the top near-equality configs
reported by the blow-up sweeps, to rule out float-masked tiny violations.
Parses 'score=' lines from blowup_k6.log / blowup_k7.log.
"""
import ast
import re
import sys
import mpmath as mp
from common import blowup_clique_number

mp.mp.dps = 50


def hp_score(F, wts, types):
    k = len(wts)
    Q = mp.zeros(k)
    m = 0
    for i in range(k):
        if types[i] == 'K':
            Q[i, i] = wts[i] - 1
            m += wts[i] * (wts[i] - 1) // 2
        for j in range(k):
            if i != j and F[i][j]:
                Q[i, j] = wts[j]
                if i < j:
                    m += wts[i] * wts[j]
    d = [mp.sqrt(wts[i]) for i in range(k)]
    S = mp.zeros(k)
    for i in range(k):
        for j in range(k):
            S[i, j] = Q[i, j] * d[i] / d[j]
    S = (S + S.T) / 2
    ev = sorted(mp.eigsy(S, eigvals_only=True), reverse=True)
    l1 = ev[0]
    l2 = ev[1] if k >= 2 else mp.mpf(-1)
    if any(t == 'K' and wt >= 2 for t, wt in zip(types, wts)) and l2 < -1:
        l2 = mp.mpf(-1)
    if any(t == 'I' and wt >= 2 for t, wt in zip(types, wts)) and l2 < 0:
        l2 = mp.mpf(0)
    w = blowup_clique_number(F, wts, types)
    return l1 ** 2 + l2 ** 2 - 2 * m * (1 - mp.mpf(1) / w), l1, l2, m, w


PAT = re.compile(r"score=([+-][\d.]+) k=(\d+) edges=(\[.*?\]) types=(\w+) wts=(\[[\d, ]*\])")

for fn in sys.argv[1:]:
    print(f"== {fn}")
    for line in open(fn):
        mo = PAT.search(line)
        if not mo:
            continue
        k = int(mo.group(2))
        edges = ast.literal_eval(mo.group(3))
        types = list(mo.group(4))
        wts = ast.literal_eval(mo.group(5))
        F = [[0] * k for _ in range(k)]
        for u, v in edges:
            F[u][v] = F[v][u] = 1
        s, l1, l2, m, w = hp_score(F, wts, types)
        verdict = "VIOLATION!!" if s > mp.mpf(10) ** -30 else ("EXACT-0" if abs(s) < mp.mpf(10) ** -30 else "negative")
        print(f"{verdict}  score={mp.nstr(s, 8)}  k={k} types={''.join(types)} wts={wts} omega={w}")

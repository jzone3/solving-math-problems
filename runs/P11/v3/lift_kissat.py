#!/usr/bin/env python3
"""ICW-lift search for CW(n,k) via kissat CNF (see lift_sat.py for the math).

Usage: python3 lift_kissat.py n m k icw_index [timeout_s]
"""
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "../../../solutions/P11")
from icw_enum import enum_fixed
from verify import check, is_proper
from cnf_cw import Builder, ternary, product_lits

MULT = {(35, 36): 4, (13, 36): 3, (7, 36): 2}


def build(n, m, k, w):
    b = Builder()
    T = b.var("TRUE")
    b.add(T)
    tv = [ternary(b, i) for i in range(n)]
    # fiber sums
    for j in range(m):
        idx = list(range(j, n, m))
        pos = [(1, tv[i][0]) for i in idx]
        neg = [(1, tv[i][1]) for i in idx]
        if w[j] >= 0:
            b.eq_sums(pos, neg + [(w[j], T)] if w[j] else neg)
        else:
            b.eq_sums(pos + [(-w[j], T)], neg)
    # weight
    nz = {}
    for i in range(n):
        nz[i] = b.or2(tv[i][0], tv[i][1])
    b.eq_sums([(1, nz[i]) for i in range(n)], [(k, T)])
    # row sum = +s or -s (wlog handled by w's sum; skip)
    # PACF
    pp, pn = {}, {}
    for t in range(1, n // 2 + 1):
        pos_terms, neg_terms = [], []
        cnt = {}
        for i in range(n):
            key = tuple(sorted((i, (i + t) % n)))
            cnt[key] = cnt.get(key, 0) + 1
        for key, c in cnt.items():
            if key not in pp:
                i, j = key
                pp[key], pn[key] = product_lits(b, *tv[i], *tv[j])
            pos_terms.append((c, pp[key]))
            neg_terms.append((c, pn[key]))
        b.eq_sums(pos_terms, neg_terms)
    return b, tv


if __name__ == "__main__":
    n, m, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    idx = int(sys.argv[4]) if len(sys.argv) > 4 else -1
    tmo = int(sys.argv[5]) if len(sys.argv) > 5 else 3600
    t = MULT[(m, k)]
    _, sols = enum_fixed(m, n // m, k, t)
    print(f"{len(sols)} <{t}>-fixed ICW_{n//m}({m},{k}) contractions", flush=True)
    todo = list(enumerate(sols)) if idx < 0 else [(idx, sols[idx])]
    for wi, w in todo:
        b, tv = build(n, m, k, list(w))
        print(f"ICW #{wi}: CNF {b.cnf.nv} vars {len(b.cnf.clauses)} clauses",
              flush=True)
        res, model = b.solve(timeout=tmo)
        if res == "SAT":
            a = [0] * n
            for i in range(n):
                a[i] = 1 if tv[i][0] in model else (-1 if tv[i][1] in model else 0)
            P = [i for i, x in enumerate(a) if x == 1]
            N = [i for i, x in enumerate(a) if x == -1]
            check(n, k, P, N, proper=False)
            print(f"ICW #{wi}: WITNESS FOUND proper={is_proper(n,P,N)}",
                  flush=True)
            print("P =", P)
            print("N =", N)
            break
        print(f"ICW #{wi}: {res}", flush=True)

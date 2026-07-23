#!/usr/bin/env python3
"""Exhaustive validation of both CNF encoders (mine + the reviewed one)
against brute force on tiny BTD instances, plus a duplicate-literal
seqcounter soundness test."""
import sys, itertools
from pysat.solvers import Minisat22
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, CNF

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_encode as my_encode


def valid(M, V, B, p1, p2, R, K, L):
    for row in M:
        if sum(row) != R or row.count(1) != p1 or row.count(2) != p2:
            return False
    for j in range(B):
        if sum(M[i][j] for i in range(V)) != K:
            return False
    for i in range(V):
        for k in range(i + 1, V):
            if sum(M[i][j] * M[k][j] for j in range(B)) != L:
                return False
    return True


def brute(V, B, p1, p2, R, K, L):
    all_valid, lex_inc, lex_dec = 0, 0, 0
    for flat in itertools.product((0, 1, 2), repeat=V * B):
        M = [list(flat[i * B:(i + 1) * B]) for i in range(V)]
        if not valid(M, V, B, p1, p2, R, K, L):
            continue
        all_valid += 1
        rows = [tuple(r) for r in M]
        cols = [tuple(M[i][j] for i in range(V)) for j in range(B)]
        if rows == sorted(rows) and cols == sorted(cols):
            lex_inc += 1
        if rows == sorted(rows, reverse=True) and cols == sorted(cols, reverse=True):
            lex_dec += 1
    return all_valid, lex_inc, lex_dec


def count_models(cnf, proj):
    n = 0
    with Minisat22(bootstrap_with=cnf.clauses) as s:
        while s.solve():
            m = s.get_model()
            n += 1
            s.add_clause([-l for l in m if abs(l) in proj])
    return n


def count_mine(V, B, p1, p2, R, K, L, lex):
    cnf, pool, T1, T2 = my_encode.build(V, B, p1, p2, R, K, L, lex)
    proj = {v for row in T1 for v in row} | {v for row in T2 for v in row}
    return count_models(cnf, proj)


def count_theirs(V, B, p1, p2, R, K, L):
    # replicate encode_sat.py by running it and reading CNF; projection on x1/x2
    import subprocess, tempfile, os
    f = tempfile.NamedTemporaryFile(suffix=".cnf", delete=False)
    subprocess.run(["python3",
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "encode_sat.py"),
                    *map(str, (V, B, p1, p2, R, K, L)), f.name], check=True,
                   capture_output=True)
    cnf = CNF(from_file=f.name)
    os.unlink(f.name)
    proj = set(range(1, 2 * V * B + 1))  # x1,x2 are allocated first (2VB vars)
    return count_models(cnf, proj)


def dup_literal_test():
    """seqcounter equals with duplicated literals vs brute force."""
    import random
    random.seed(0)
    bad = 0
    for trial in range(200):
        n = random.randint(2, 6)
        w = [random.randint(1, 3) for _ in range(n)]
        b = random.randint(0, sum(w))
        pool = IDPool()
        xs = [pool.id(("x", i)) for i in range(n)]
        lits = []
        for x, wt in zip(xs, w):
            lits += [x] * wt
        enc = CardEnc.equals(lits=lits, bound=b, vpool=pool,
                             encoding=EncType.seqcounter)
        cnt = count_models(CNF(from_clauses=enc.clauses), set(xs))
        exp = sum(1 for a in itertools.product((0, 1), repeat=n)
                  if sum(ai * wi for ai, wi in zip(a, w)) == b)
        if cnt != exp:
            bad += 1
            print("MISMATCH", n, w, b, cnt, exp)
    print("dup-literal seqcounter test:", "FAIL" if bad else "PASS (200 trials)")


if __name__ == "__main__":
    dup_literal_test()
    for inst in [(3, 3, 1, 1, 3, 3, 2), (3, 4, 2, 1, 4, 3, 3), (4, 4, 0, 2, 4, 4, 4)]:
        V, B, p1, p2, R, K, L = inst
        av, li, ld = brute(*inst)
        mn = count_mine(*inst, lex=True)
        mn_nolex = count_mine(*inst, lex=False)
        th = count_theirs(*inst)
        ok = (mn == ld and th == ld and mn_nolex == av)
        print(f"{inst}: brute all={av} lexinc={li} lexdec={ld} | "
              f"reviewenc(lex)={mn} reviewenc(nolex)={mn_nolex} encode_sat(lex)={th} "
              f"=> {'PASS' if ok else 'FAIL'}")

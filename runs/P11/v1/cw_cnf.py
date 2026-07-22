#!/usr/bin/env python3
"""V1 direct SAT encoding of CW(n,k) existence -> CNF for kissat.

Encoding:
  p_i / m_i booleans per position (entry +1 / -1), not both.
  #p = (k+s)/2, #m = (k-s)/2  (s = sqrt(k); WLOG by negation symmetry).
  p_0 = 1 (WLOG by cyclic shift symmetry).
  For each shift t in 1..n//2 and each unordered pair {i, i+t mod n}:
    P-pair bool <-> (p_i&p_j)|(m_i&m_j) ; M-pair bool <-> (p_i&m_j)|(m_i&p_j)
  PAF_t = 0  <=>  count(P-pairs at t) == count(M-pairs at t)
    enforced by two totalizers with linked outputs, counts capped at k//2.

Usage:
  python3 cw_cnf.py encode n k out.cnf [--fixzero i,j,...] [--fixpos ...] [--fixneg ...]
  python3 cw_cnf.py decode n k out.cnf model_file   # kissat "v ..." lines
"""
import math, sys
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType


def pairs_for_shift(n, t):
    seen = set()
    out = []
    for i in range(n):
        j = (i + t) % n
        key = (min(i, j), max(i, j))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def tot_outputs(cnf, pool, lits, ubound, tag):
    """Build a totalizer over lits; return output vars o[0..ubound-1],
    o[j] <=> (sum >= j+1), with full (two-sided) clauses."""
    def build(lo, hi):
        if hi - lo == 1:
            return [lits[lo]]
        mid = (lo + hi) // 2
        L = build(lo, mid)
        R = build(mid, hi)
        m_ = min(len(L) + len(R), ubound)
        out = [pool.id((tag, lo, hi, j)) for j in range(m_)]
        # sum >= j+1 iff exists a+b = j+1, a of L true-count, b of R
        # standard totalizer clauses (both directions):
        for a in range(len(L) + 1):
            for b in range(len(R) + 1):
                if a + b == 0:
                    continue
                cl = []
                if a > 0:
                    cl.append(-L[a - 1])
                if b > 0:
                    cl.append(-R[b - 1])
                cl.append(out[min(a + b, m_) - 1])
                cnf.append(cl)  # L>=a & R>=b -> out >= min(a+b, m_)
        for a in range(len(L) + 1):
            for b in range(len(R) + 1):
                if a + b >= m_ + 1:
                    continue
                # L<=a & R<=b -> out <= a+b  i.e. (L>=a+1 or R>=b+1 or -out[a+b])
                if a + b >= m_:
                    continue
                cl = []
                if a < len(L):
                    cl.append(L[a])
                if b < len(R):
                    cl.append(R[b])
                cl.append(-out[a + b])
                cnf.append(cl)
        return out
    return build(0, len(lits))


def link_offset(cnf, pool, alits, blits, c, tag):
    """Enforce count(alits) - count(blits) = c (c may be negative)."""
    if c < 0:
        alits, blits, c = blits, alits, -c
    oa = tot_outputs(cnf, pool, alits, len(alits), tag + "a")
    ob = tot_outputs(cnf, pool, blits, len(blits), tag + "b")
    if c > 0:
        cnf.append([oa[c - 1]])  # countA >= c
    # countA >= j+c  <->  countB >= j   for j >= 1
    for j in range(1, len(ob) + 1):
        ia = j + c - 1
        if ia < len(oa):
            cnf.append([-ob[j - 1], oa[ia]])
            cnf.append([-oa[ia], ob[j - 1]])
        else:
            cnf.append([-ob[j - 1]])  # countB can't reach j
    # cap countA <= len(blits) + c
    if len(blits) + c < len(oa):
        cnf.append([-oa[len(blits) + c]])


def encode2(n, k, fixzero=(), fixpos=(), fixneg=(), classsum=None, proper=True,
            liftsum=None, fix0=True):
    s = math.isqrt(k)
    assert s * s == k
    npos, nneg = (k + s) // 2, (k - s) // 2
    pool = IDPool()
    cnf = CNF()
    P = [pool.id(("p", i)) for i in range(n)]
    M = [pool.id(("m", i)) for i in range(n)]
    for i in range(n):
        cnf.append([-P[i], -M[i]])
    if fix0:
        cnf.append([P[0]])
    for i in fixzero:
        cnf.append([-P[i]]); cnf.append([-M[i]])
    for i in fixpos:
        cnf.append([P[i]])
    for i in fixneg:
        cnf.append([M[i]])
    cnf.extend(CardEnc.equals(lits=P, bound=npos, vpool=pool, encoding=EncType.totalizer))
    cnf.extend(CardEnc.equals(lits=M, bound=nneg, vpool=pool, encoding=EncType.totalizer))
    if proper:
        # proper CWM: support must not lie in a single residue class mod any
        # prime p | n; with a_0 != 0 fixed, that class would be 0 mod p
        pr = set()
        nn = n
        for f in range(2, n + 1):
            while nn % f == 0:
                pr.add(f); nn //= f
        for pnum in sorted(pr):
            residues = [0] if fix0 else range(pnum)
            for r in residues:
                cl = []
                for i in range(n):
                    if i % pnum != r:
                        cl.append(P[i]); cl.append(M[i])
                cnf.append(cl)
    if liftsum:
        d, bs = liftsum
        assert n % d == 0 and len(bs) == d
        c = n // d
        assert c <= 3, "blocking-clause lift encoding only for class size <= 3"
        import itertools
        for j in range(d):
            idxs = [j + t * d for t in range(c)]
            for vals in itertools.product((-1, 0, 1), repeat=c):
                if sum(vals) == bs[j]:
                    continue
                cl = []
                for pos, v in zip(idxs, vals):
                    if v == 1:
                        cl.append(-P[pos])
                    elif v == -1:
                        cl.append(-M[pos])
                    else:
                        cl.append(P[pos]); cl.append(M[pos])
                cnf.append(cl)
    if classsum:
        d, cs = classsum
        assert n % d == 0 and len(cs) == d and sum(cs) == s
        for j in range(d):
            alits = [P[i] for i in range(j, n, d)]
            blits = [M[i] for i in range(j, n, d)]
            link_offset(cnf, pool, alits, blits, cs[j], f"CS{d}_{j}")
    cap = k // 2
    prodvar = {}
    for t in range(1, n // 2 + 1):
        plits, mlits = [], []
        for (i, j) in pairs_for_shift(n, t):
            if (i, j) not in prodvar:
                a = pool.id(("A", i, j)); b = pool.id(("B", i, j))
                c = pool.id(("C", i, j)); d = pool.id(("D", i, j))
                for (v, x, y) in ((a, P[i], P[j]), (b, M[i], M[j]),
                                  (c, P[i], M[j]), (d, M[i], P[j])):
                    cnf.append([-v, x]); cnf.append([-v, y]); cnf.append([v, -x, -y])
                pp = pool.id(("PP", i, j)); mm = pool.id(("MM", i, j))
                cnf.append([-a, pp]); cnf.append([-b, pp]); cnf.append([-pp, a, b])
                cnf.append([-c, mm]); cnf.append([-d, mm]); cnf.append([-mm, c, d])
                prodvar[(i, j)] = (pp, mm)
            pp, mm = prodvar[(i, j)]
            plits.append(pp); mlits.append(mm)
        op = tot_outputs(cnf, pool, plits, cap + 1, f"TP{t}")
        om = tot_outputs(cnf, pool, mlits, cap + 1, f"TM{t}")
        # cap counts
        if len(op) > cap:
            cnf.append([-op[cap]])
        if len(om) > cap:
            cnf.append([-om[cap]])
        # equality of counts
        for j in range(min(len(op), len(om), cap)):
            cnf.append([-op[j], om[j]])
            cnf.append([-om[j], op[j]])
    return cnf, pool, P, M


def main():
    cmd = sys.argv[1]
    n, k = int(sys.argv[2]), int(sys.argv[3])
    path = sys.argv[4]
    fixzero = fixpos = fixneg = ()
    classsum = None
    liftsum = None
    proper = True
    fix0 = True
    for arg in sys.argv[5:]:
        if arg.startswith("--fixzero="):
            fixzero = tuple(int(v) for v in arg.split("=")[1].split(",") if v)
        if arg.startswith("--fixpos="):
            fixpos = tuple(int(v) for v in arg.split("=")[1].split(",") if v)
        if arg.startswith("--fixneg="):
            fixneg = tuple(int(v) for v in arg.split("=")[1].split(",") if v)
        if arg.startswith("--classsum="):
            spec = arg.split("=")[1]
            d, cs = spec.split(":")
            classsum = (int(d), [int(v) for v in cs.split(",")])
        if arg.startswith("--liftsum="):
            spec = arg.split("=")[1]
            d, bs = spec.split(":")
            liftsum = (int(d), [int(v) for v in bs.split(",")])
        if arg == "--improper-ok":
            proper = False
        if arg == "--nofix0":
            fix0 = False
    if cmd == "encode":
        cnf, pool, P, M = encode2(n, k, fixzero, fixpos, fixneg, classsum, proper,
                                  liftsum, fix0)
        cnf.to_file(path)
        print(f"wrote {path}: {cnf.nv} vars, {len(cnf.clauses)} clauses")
    elif cmd == "decode":
        model_file = sys.argv[5]
        cnf, pool, P, M = encode2(n, k)
        vals = set()
        for line in open(model_file):
            if line.startswith("v"):
                for tok in line.split()[1:]:
                    v = int(tok)
                    if v > 0:
                        vals.add(v)
        row = []
        for i in range(n):
            if P[i] in vals:
                row.append(1)
            elif M[i] in vals:
                row.append(-1)
            else:
                row.append(0)
        print("ROW", row)
        # self-check
        w = sum(v * v for v in row)
        ok = w == k and all(
            sum(row[i] * row[(i + t) % n] for i in range(n)) == 0 for t in range(1, n))
        print("SELFCHECK", "PASS" if ok else "FAIL", "weight", w)


if __name__ == "__main__":
    main()

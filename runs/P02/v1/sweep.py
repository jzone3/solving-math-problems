#!/usr/bin/env python3
"""
P02 V1 exhaustive sweep.

For each n, generate all triangle-free graphs with min degree >= ceil(n/3)
(nauty-geng -t -d<k>), filter to MAXIMAL triangle-free (every non-adjacent
pair has a common neighbor), and for each such G test whether G admits a
regular triangle-free supergraph via vertex multiplications.

Key reduction (logged in NOTES.md): a vertex-multiplication supergraph with
multiplicities x_v >= 1 (integers) is regular of degree d iff
    sum_{u in N(v)} x_u = d  for all v.
Integer feasibility for SOME positive integer d  <=>  rational feasibility of
    { x_v >= 1, (Ax) constant }
because any rational solution can be scaled by a common denominator (scaling
preserves x >= 1 direction after normalizing min x to 1: if x > 0 rational with
Ax = c*1, then t*x for suitable t in Q gives x >= 1 and Ax = (tc)*1; multiply
by denominators to reach integers).  So the per-graph test is an exact LP:
    maximize t  s.t.  Ax - lambda*1 = 0,  x_v - t >= 0,  t <= 1
feasible with optimum t > 0  <=>  regular multiplication supergraph exists.

Fast path: scipy linprog (highs).  Any graph whose LP optimum is < 0.5 (i.e.
not clearly strictly feasible) is re-checked with an exact Fraction-based
simplex (exactlp.py).  A graph exactly infeasible is a COUNTEREXAMPLE.
"""
import sys, subprocess, math, time
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from exactlp import exact_max_t


def graph6_to_adj(line):
    data = line.strip()
    b = [ord(c) - 63 for c in data]
    n = b[0]
    assert n < 63
    bits = []
    for x in b[1:]:
        for i in range(5, -1, -1):
            bits.append((x >> i) & 1)
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def is_maximal_tf(n, adj):
    full = (1 << n) - 1
    for u in range(n):
        nonadj = full & ~adj[u] & ~(1 << u)
        v = 0
        while nonadj:
            lsb = nonadj & -nonadj
            v = lsb.bit_length() - 1
            if not (adj[u] & adj[v]):
                return False
            nonadj ^= lsb
    return True


def lp_max_t(n, adj):
    """maximize t s.t. Ax = lam*1, x >= t, t <= 1, x <= n (bounding box).
    Returns HiGHS optimum of t (or -1 if infeasible)."""
    # vars: x_0..x_{n-1}, lam, t   -> minimize -t
    nv = n + 2
    c = np.zeros(nv); c[-1] = -1.0
    A_eq = np.zeros((n, nv))
    for v in range(n):
        for u in range(n):
            if adj[v] >> u & 1:
                A_eq[v, u] = 1.0
        A_eq[v, n] = -1.0
    # x_v - t >= 0  ->  -x_v + t <= 0
    A_ub = np.zeros((n, nv))
    for v in range(n):
        A_ub[v, v] = -1.0
        A_ub[v, -1] = 1.0
    bounds = [(0, float(n))] * n + [(0, None), (None, 1.0)]
    res = linprog(c, A_ub=A_ub, b_ub=np.zeros(n), A_eq=A_eq,
                  b_eq=np.zeros(n), bounds=bounds, method='highs')
    if not res.success:
        return -1.0
    return -res.fun


def exact_check(n, adj):
    """Exact rational LP: returns Fraction optimum of t (>0 means feasible)."""
    return exact_max_t(n, adj)


def main():
    n = int(sys.argv[1])
    mind = math.ceil(n / 3)
    cmd = ['nauty-geng', '-t', '-d%d' % mind, str(n)]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, bufsize=1 << 20)
    total = 0
    maximal = 0
    suspicious = []
    counterexamples = []
    min_t = 2.0
    for line in proc.stdout:
        total += 1
        nn, adj = graph6_to_adj(line)
        if not is_maximal_tf(nn, adj):
            continue
        maximal += 1
        t = lp_max_t(nn, adj)
        if t < min_t:
            min_t = t
        if t < 0.5:
            te = exact_check(nn, adj)
            suspicious.append((line.strip(), t, str(te)))
            if te <= 0:
                counterexamples.append(line.strip())
                print('COUNTEREXAMPLE', line.strip(), flush=True)
    proc.wait()
    el = time.time() - t0
    print(f'n={n} mind={mind} tf_graphs={total} maximal={maximal} '
          f'min_lp_t={min_t if maximal else None} suspicious={len(suspicious)} '
          f'counterexamples={len(counterexamples)} time={el:.1f}s', flush=True)
    for s in suspicious:
        print('  SUSP', s, flush=True)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
P02 V1 main sweep driver.

Reads maximal triangle-free graphs either from an MTF generator file
(multi_code2_s_old) or graph6 lines on stdin, and tests both forms of
Brandt's conjecture:

  Track A (Conjecture 4.1): if delta(G) > n/3 (STRICT, the original class G),
     the multiplication system {x>0, Ax = c*1} must be feasible.
  Track B (Conjecture 5.1, equivalent LP form): if d_f(G) < 3
     (d_f = min{1'x : x>=0, Ax>=1}), the same system must be feasible.
  Also logged: boundary failures delta >= n/3 (West's paraphrase, known FALSE,
     smallest witness n=9 found by this run).

Fast path per graph: solve Ax = 1 by LU (A is nonsingular for almost all G);
if the solution is strictly one-signed, the multiplication system is feasible
and (since a positive solution of Ax=c*1 scaled gives Ax'=1, 1'x' >= ... ) we
only compute d_f when needed. Singular / infeasible / near-zero cases fall
back to scipy LP, and anything still suspicious is decided EXACTLY with
runs/P02/v1/exactlp.py (rational simplex).

Output: one summary line per n + candidate lines (graph6) to stdout.
"""
import sys, math, time
import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from exactlp import exact_max_t, exact_df


def read_m2so(path):
    data = open(path, 'rb').read()
    pos = 0
    prev = []
    while pos < len(data):
        d = data[pos]; pos += 1
        rec = list(prev[:d])
        n = rec[0] if d >= 1 else data[pos]
        # read until we have n-1 zero-terminators beyond position 0
        need_zeros = n - 1
        zeros = sum(1 for b in rec[1:] if b == 0)
        while zeros < need_zeros:
            b = data[pos]; pos += 1
            rec.append(b)
            if b == 0:
                zeros += 1
        prev = rec
        n = rec[0]
        adj = [0] * n
        i = 0
        for b in rec[1:]:
            if b == 0:
                i += 1
            else:
                j = b - 1
                adj[i] |= 1 << j
                adj[j] |= 1 << i
        yield n, adj


def graph6_to_adj(line):
    b = [ord(c) - 63 for c in line.strip()]
    n = b[0]
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


def adj_to_graph6(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6:
        bits.append(0)
    s = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for bit in bits[k:k + 6]:
            v = v * 2 + bit
        s += chr(v + 63)
    return s


def lp_max_t(n, A):
    nv = n + 2
    c = np.zeros(nv); c[-1] = -1.0
    A_eq = np.zeros((n, nv)); A_eq[:, :n] = A; A_eq[:, n] = -1.0
    A_ub = np.zeros((n, nv))
    A_ub[np.arange(n), np.arange(n)] = -1.0
    A_ub[:, -1] = 1.0
    bounds = [(0, float(n))] * n + [(0, None), (None, 1.0)]
    res = linprog(c, A_ub=A_ub, b_ub=np.zeros(n), A_eq=A_eq, b_eq=np.zeros(n),
                  bounds=bounds, method='highs')
    return -res.fun if res.success else -1.0


def lp_df(n, A):
    res = linprog(np.ones(n), A_ub=-A, b_ub=-np.ones(n),
                  bounds=[(0, None)] * n, method='highs')
    return res.fun if res.success else float('inf')


def handle_graph(n, adj, stats, out):
    """Process one maximal triangle-free graph; append report lines to out."""
    st = stats.setdefault(n, dict(total=0, ge=0, gt=0, ge_infeas=0,
                                  gt_infeas=0, df3=0, cand=0, singular=0))
    st['total'] += 1
    degs = [bin(a).count('1') for a in adj]
    mind = min(degs)
    ge = mind * 3 >= n
    gt = mind * 3 > n
    if ge:
        st['ge'] += 1
    if gt:
        st['gt'] += 1
    # collapse to core: feasibility and d_f depend only on the quotient
    # by the 'similar vertices' relation N(v)=N(u) (see NOTES.md)
    classes = {}
    for v in range(n):
        classes.setdefault(adj[v], []).append(v)
    reps = sorted(classes, key=lambda m: classes[m][0])
    m = len(reps)
    idx = {r: i for i, r in enumerate(reps)}
    cadj = [0] * m
    for i, r in enumerate(reps):
        for j, r2 in enumerate(reps):
            if r >> classes[r2][0] & 1:
                cadj[i] |= 1 << j
    A = np.array([[(cadj[v] >> u) & 1 for u in range(m)]
                  for v in range(m)], dtype=float)
    feasible = None
    try:
        x = np.linalg.solve(A, np.ones(m))
        if np.min(x) > 1e-9 or np.max(x) < -1e-9:
            feasible = True
        elif np.max(np.abs(A @ x - 1)) > 1e-6:
            pass  # numerically bad, fall through to LP
        elif np.min(np.abs(x)) > 1e-9:
            feasible = False  # unique solution, mixed signs / zeros clear
    except np.linalg.LinAlgError:
        st['singular'] += 1
    if feasible is None:
        t = lp_max_t(m, A)
        feasible = t > 1e-6
    if feasible:
        return
    # float-level infeasible; exact verification only where it matters
    # (Track A class, boundary class, or potential df<3), else just count
    df = lp_df(m, A)
    if not ge and df > 3 - 1e-7:
        st['df3'] += 1
        return
    if exact_max_t(m, cadj) > 0:
        return  # float was wrong; actually feasible
    n_, adj_ = n, adj
    n, adj, A = m, cadj, A  # report/df on the core
    g6full = adj_to_graph6(n_, adj_)
    # multiplication system infeasible (exactly verified)
    g6 = g6full
    if ge:
        st['ge_infeas'] += 1
    if gt:
        st['gt_infeas'] += 1
        out.append(f'TRACKA-COUNTEREXAMPLE n={n_} {g6}')
    if df < 3 - 1e-7:
        dfe = exact_df(n, adj)
        if dfe < 3:
            st['cand'] += 1
            out.append(f'TRACKB-COUNTEREXAMPLE n={n} {g6} df={dfe}')
    else:
        st['df3'] += 1
    if ge:
        out.append(f'BOUNDARY-INFEAS n={n_} {g6} df={df:.6f}')
    n, adj = n_, adj_


def _worker(batch):
    stats = {}
    out = []
    for n, adj in batch:
        handle_graph(n, adj, stats, out)
    return stats, out


def _merge(tot, stats):
    for n, st in stats.items():
        t = tot.setdefault(n, dict(total=0, ge=0, gt=0, ge_infeas=0,
                                   gt_infeas=0, df3=0, cand=0, singular=0))
        for k, v in st.items():
            t[k] += v


def main():
    import multiprocessing as mp
    from itertools import islice
    src = sys.argv[1]
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    reader = read_m2so(src) if src.endswith('.m2so') else \
        (graph6_to_adj(l) for l in sys.stdin)
    t0 = time.time()
    tot = {}
    if procs == 1:
        out = []
        for n, adj in reader:
            handle_graph(n, adj, tot, out)
            if out:
                for l in out:
                    print(l, flush=True)
                out = []
    else:
        def batches():
            while True:
                b = list(islice(reader, 2000))
                if not b:
                    return
                yield b
        with mp.Pool(procs) as pool:
            for stats, out in pool.imap_unordered(_worker, batches()):
                _merge(tot, stats)
                for l in out:
                    print(l, flush=True)
    for n in sorted(tot):
        st = tot[n]
        print(f"SUMMARY n={n} total={st['total']} ge={st['ge']} gt={st['gt']} "
              f"ge_infeas={st['ge_infeas']} gt_infeas={st['gt_infeas']} "
              f"df3={st['df3']} trackB_cand={st['cand']} "
              f"singular={st['singular']} time={time.time()-t0:.1f}s",
              flush=True)


if __name__ == '__main__':
    main()

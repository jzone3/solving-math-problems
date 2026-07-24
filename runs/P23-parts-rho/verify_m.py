#!/usr/bin/env python3
"""Independent verifier for a 5-chromatic unit-distance graph over an arbitrary
multi-quadratic field Q(sqrt p1,...,sqrt pk).

Checks, all in EXACT arithmetic:
  1. all vertex coords parse exactly into the field (no floats); all distinct;
  2. every claimed edge is EXACTLY unit distance;
  3. no unclaimed pair is unit distance (edge list complete);
  4. the graph is NOT 4-colorable (kissat UNSAT; --drat also runs drat-trim).

Usage:
  python3 verify_m.py graph.vtx --primes 2,3,5,11 [--edges e.txt] [--drat]

Input .vtx: one point per line as a Python-repr pair of field elements, OR a
pickle (points,edges) via --pkl.
"""
import sys, os, argparse, subprocess, tempfile, pickle, shutil
from mfield import MField
import numpy as np

KISSAT = os.environ.get('KISSAT') or shutil.which('kissat') or os.path.expanduser('~/p23/kissat/build/kissat')
DRATTRIM = os.environ.get('DRATTRIM') or shutil.which('drat-trim') or os.path.expanduser('~/p23/drat-trim/drat-trim')


def exact_edges(K, pts):
    Af = np.array([(K.to_float(p[0]), K.to_float(p[1])) for p in pts])
    n = len(pts); E = set(); CH = 800
    for s in range(0, n, CH):
        d2 = ((Af[s:s+CH, None, :] - Af[None, :, :]) ** 2).sum(-1)
        ii, jj = np.nonzero(np.abs(d2 - 1.0) < 1e-6)
        for a, b in zip(ii, jj):
            ga, gb = s + int(a), int(b)
            if ga < gb and K.norm2(pts[ga], pts[gb]) == K.ONE:
                E.add((ga, gb))
    return E


def color_cnf(n, edges, k=4):
    cls = []
    for v in range(n):
        cls.append([v*k+c+1 for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1+1, k):
                cls.append([-(v*k+c1+1), -(v*k+c2+1)])
    for (u, v) in edges:
        for c in range(k):
            cls.append([-(u*k+c+1), -(v*k+c+1)])
    return n*k, cls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pkl', required=True, help='pickle of (points, edges) in field coords')
    ap.add_argument('--primes', required=True)
    ap.add_argument('--drat', action='store_true')
    args = ap.parse_args()
    primes = tuple(int(x) for x in args.primes.split(','))
    K = MField(primes)
    pts, claimed_edges = pickle.load(open(args.pkl, 'rb'))
    # ensure field dimensionality matches
    assert all(len(p[0]) == K.N and len(p[1]) == K.N for p in pts), 'coord dim != field N'
    n = len(pts); ok = True
    print(f'[1] parsed {n} vertices exactly (field Q{primes}) ... PASS')
    if len(set(pts)) != n:
        print('[1b] duplicate vertices ... FAIL'); ok = False
    else:
        print('[1b] all vertices distinct ... PASS')
    E = exact_edges(K, pts)
    claimed = set((min(a,b),max(a,b)) for a,b in claimed_edges)
    print(f'[2/3] recomputed exact unit-distance edges: {len(E)} (claimed {len(claimed)})')
    if claimed == E:
        print('[3] claimed edge list matches exact recomputation ... PASS')
    else:
        print(f'[3] MISMATCH only-claimed={len(claimed-E)} only-exact={len(E-claimed)} ... FAIL'); ok = False
    nvars, cls = color_cnf(n, sorted(E), 4)
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, 'g.cnf'); drat = os.path.join(d, 'g.drat')
        with open(cnf, 'w') as f:
            f.write(f'p cnf {nvars} {len(cls)}\n')
            for c in cls:
                f.write(' '.join(map(str, c)) + ' 0\n')
        cmd = [KISSAT, '-q', cnf] + ([drat] if args.drat else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            print('[4] SAT solver: 4-coloring UNSAT => chi>=5 ... PASS')
        elif 's SATISFIABLE' in r.stdout:
            print('[4] 4-colorable => chi<=4 ... FAIL'); ok = False
        else:
            print('[4] UNKNOWN ... FAIL'); ok = False
        if args.drat and ok:
            r2 = subprocess.run([DRATTRIM, cnf, drat], capture_output=True, text=True)
            if 's VERIFIED' in r2.stdout:
                print('[4b] drat-trim VERIFIED UNSAT proof ... PASS')
            else:
                print('[4b] drat-trim FAILED ... FAIL'); ok = False
    print('\nOVERALL:', 'PASS (5-chromatic unit-distance graph)' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

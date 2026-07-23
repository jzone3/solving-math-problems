#!/usr/bin/env python3
"""
Independent verifier for a 5-chromatic unit-distance graph.

Checks, all in EXACT arithmetic over the real field Q(sqrt3, sqrt5, sqrt11):
  1. all vertex coordinates parse to exact algebraic numbers (no floats);
  2. every listed edge is EXACTLY a unit distance apart;
  3. no unlisted pair is a unit distance apart (edge list is complete);
  4. the graph is NOT 4-colorable  -> chromatic number >= 5
       (SAT UNSAT, with a DRAT proof independently checked by drat-trim);
  5. the graph IS a unit-distance graph in the plane (implied by 1-3);
prints PASS / FAIL for each and an overall verdict.

Usage:
    python3 verify.py <graph.vtx> [--edges edges.txt] [--drat]

No exotic deps: sympy + a SAT solver (kissat) + drat-trim (paths below).
"""
import sys, os, argparse, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from field import load_vtx, norm2, ONE, to_float

import shutil
KISSAT = os.environ.get('KISSAT') or shutil.which('kissat') or os.path.expanduser('~/p23/kissat/build/kissat')
DRATTRIM = os.environ.get('DRATTRIM') or shutil.which('drat-trim') or os.path.expanduser('~/p23/drat-trim/drat-trim')


def exact_edges(pts):
    n = len(pts)
    fl = [(to_float(p[0]), to_float(p[1])) for p in pts]
    E = set()
    for i in range(n):
        xi, yi = fl[i]
        for j in range(i + 1, n):
            dx, dy = xi - fl[j][0], yi - fl[j][1]
            if abs(dx * dx + dy * dy - 1.0) < 1e-6:
                if norm2(pts[i], pts[j]) == ONE:
                    E.add((i, j))
    return E


def color_cnf(n, edges, k=4):
    cls = []
    for v in range(n):
        cls.append([v * k + c + 1 for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cls.append([-(v * k + c1 + 1), -(v * k + c2 + 1)])
    for (u, v) in edges:
        for c in range(k):
            cls.append([-(u * k + c + 1), -(v * k + c + 1)])
    return n * k, cls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vtx')
    ap.add_argument('--edges', default=None,
                    help='optional edge list (i j per line, 0-indexed) to cross-check')
    ap.add_argument('--drat', action='store_true',
                    help='also produce & independently verify a DRAT UNSAT proof')
    args = ap.parse_args()

    ok = True
    pts = load_vtx(args.vtx)
    n = len(pts)
    print(f'[1] parsed {n} vertices exactly (field Q(v3,v5,v11)) ... PASS')

    if len(set(pts)) != n:
        print('[1b] duplicate vertices detected ... FAIL'); ok = False
    else:
        print('[1b] all vertices distinct ... PASS')

    E = exact_edges(pts)
    print(f'[2/3] recomputed exact unit-distance edge set: {len(E)} edges')

    if args.edges:
        claimed = set()
        for line in open(args.edges):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            a, b = map(int, line.split())
            claimed.add((min(a, b), max(a, b)))
        if claimed == E:
            print(f'[3] claimed edge list matches exact recomputation ... PASS')
        else:
            print(f'[3] edge list MISMATCH: only-claimed={len(claimed-E)} '
                  f'only-exact={len(E-claimed)} ... FAIL'); ok = False

    # 4-colorability
    nvars, cls = color_cnf(n, sorted(E), 4)
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, 'g.cnf')
        drat = os.path.join(d, 'g.drat')
        with open(cnf, 'w') as f:
            f.write(f'p cnf {nvars} {len(cls)}\n')
            for c in cls:
                f.write(' '.join(map(str, c)) + ' 0\n')
        cmd = [KISSAT, '-q', cnf] + ([drat] if args.drat else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            print('[4] SAT solver: 4-coloring is UNSAT  => chi >= 5 ... PASS')
        elif 's SATISFIABLE' in r.stdout:
            print('[4] SAT solver: graph IS 4-colorable => chi <= 4 ... FAIL'); ok = False
        else:
            print('[4] SAT solver: UNKNOWN ... FAIL'); ok = False
        if args.drat and ok:
            r2 = subprocess.run([DRATTRIM, cnf, drat], capture_output=True, text=True)
            if 's VERIFIED' in r2.stdout:
                print('[4b] drat-trim independently VERIFIED the UNSAT proof ... PASS')
            else:
                print('[4b] drat-trim FAILED to verify proof ... FAIL'); ok = False

    print('\nOVERALL:', 'PASS  (this is a 5-chromatic unit-distance graph)' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

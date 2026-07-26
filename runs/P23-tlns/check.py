"""Non-4-colorability check for a vertex subset of a universe pickle.

Usage: python3 check.py UNIVERSE.pkl [SUBSET.pkl]
Prints SAT / UNSAT and the size.  Exact edges are taken from the universe (which
is itself exactly built and re-verifiable with verify_universe-style code).
"""
import os
import pickle
import subprocess
import sys

from sat import color_cnf, write_cnf, KISSAT


def load(path):
    rec = pickle.load(open(path, 'rb'))
    return rec[0], rec[1]


def sub_edges(E, S):
    remap = {v: i for i, v in enumerate(sorted(S))}
    return len(remap), [(remap[u], remap[v]) for u, v in E
                        if u in remap and v in remap]


def is_colorable(n, E, tag='chk'):
    nv, cls = color_cnf(n, E, 4)
    cnf = f'/tmp/{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    try:
        r = subprocess.run([KISSAT, '-q', cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return False
        if 's SATISFIABLE' in r.stdout:
            return True
        raise RuntimeError('kissat gave no verdict')
    finally:
        os.unlink(cnf)


if __name__ == '__main__':
    pts, E = load(sys.argv[1])
    S = (pickle.load(open(sys.argv[2], 'rb')) if len(sys.argv) > 2
         else list(range(len(pts))))
    n, E2 = sub_edges(E, set(S))
    print(f'{n} vertices, {len(E2)} edges ->',
          'SAT (4-colorable)' if is_colorable(n, E2) else 'UNSAT', flush=True)

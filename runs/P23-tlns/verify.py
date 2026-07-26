"""Standalone verifier for a claimed 5-chromatic unit-distance graph.

No dependency on any other file in this directory: the witness pickle carries
its own exact coordinates, and everything (field arithmetic, unit distances,
non-4-colorability) is recomputed here from scratch.

A witness file is a pickle {'points': [...], 'edges': [...], 'primes': [...]},
where each point is a pair (x, y) of field elements and a field element is a
tuple of `2**len(primes)` Fractions: the coefficient of the square root of the
product of the primes selected by the bit mask of the index.  For primes
(3, 5, 11) index 5 = 1 + 4 means the coefficient of sqrt(3*11) = sqrt(33).

Checks, in order:

1. every coordinate is a field element of the right shape;
2. the edge list is *exactly* the set of pairs at distance one: for every pair
   of points, dx^2 + dy^2 is computed in the field and compared with 1 (floats
   are used only to skip pairs that are far apart, and the skip radius is
   generous, so no exact unit pair can be missed);
3. the graph is not 4-colorable: kissat is run on the direct colouring
   encoding, and its DRAT proof is checked by drat-trim (s VERIFIED);
4. the graph *is* 5-colorable (so the chromatic number is exactly 5) -- this is
   informational and skipped with SKIP5=1.

Usage: python3 verify.py WITNESS.pkl
"""
import itertools
import os
import pickle
import subprocess
import sys
from fractions import Fraction

KISSAT = os.environ.get('KISSAT', os.path.expanduser('~/p23/kissat/build/kissat'))
DRATTRIM = os.environ.get('DRATTRIM',
                          os.path.expanduser('~/p23/drat-trim/drat-trim'))


class Field:
    """Q(sqrt p1, sqrt p2, ...) as tuples of Fractions indexed by bit masks."""

    def __init__(self, primes):
        self.primes = tuple(primes)
        self.n = 1 << len(self.primes)
        self.zero = (Fraction(0),) * self.n
        self.one = (Fraction(1),) + (Fraction(0),) * (self.n - 1)
        self.sq = [1] * self.n
        for m in range(self.n):
            v = 1
            for i, p in enumerate(self.primes):
                if m >> i & 1:
                    v *= p
            self.sq[m] = v
        # (sqrt A)(sqrt B) = gcd-part * sqrt(A xor B)
        self.coef = [[1] * self.n for _ in range(self.n)]
        for a in range(self.n):
            for b in range(self.n):
                c = 1
                for i, p in enumerate(self.primes):
                    if (a >> i & 1) and (b >> i & 1):
                        c *= p
                self.coef[a][b] = c

    def add(self, x, y):
        return tuple(a + b for a, b in zip(x, y))

    def sub(self, x, y):
        return tuple(a - b for a, b in zip(x, y))

    def mul(self, x, y):
        out = [Fraction(0)] * self.n
        for a, xa in enumerate(x):
            if not xa:
                continue
            for b, yb in enumerate(y):
                if not yb:
                    continue
                out[a ^ b] += xa * yb * self.coef[a][b]
        return tuple(out)

    def to_float(self, x):
        return float(sum(c * self.sq[m] ** 0.5 for m, c in enumerate(x)))


def exact_edges(field, points):
    """The exact unit-distance graph on `points` (floats only prune)."""
    xy = [(field.to_float(x), field.to_float(y)) for x, y in points]
    edges = set()
    for i, j in itertools.combinations(range(len(points)), 2):
        dxf = xy[i][0] - xy[j][0]
        dyf = xy[i][1] - xy[j][1]
        if abs(dxf * dxf + dyf * dyf - 1.0) > 1e-4:      # generous prefilter
            continue
        dx = field.sub(points[i][0], points[j][0])
        dy = field.sub(points[i][1], points[j][1])
        if field.add(field.mul(dx, dx), field.mul(dy, dy)) == field.one:
            edges.add((i, j))
    return edges


def color_cnf(n, edges, k):
    cls = []
    for v in range(n):
        cls.append([v * k + c + 1 for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cls.append([-(v * k + c1 + 1), -(v * k + c2 + 1)])
    for u, v in edges:
        for c in range(k):
            cls.append([-(u * k + c + 1), -(v * k + c + 1)])
    return n * k, cls


def write_cnf(path, nvars, cls):
    with open(path, 'w') as f:
        f.write(f'p cnf {nvars} {len(cls)}\n')
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')


def not_k_colorable(n, edges, k, proof=True):
    nvars, cls = color_cnf(n, edges, k)
    cnf = f'/tmp/vfy_{os.getpid()}_{k}.cnf'
    drat = f'/tmp/vfy_{os.getpid()}_{k}.drat'
    write_cnf(cnf, nvars, cls)
    try:
        cmd = [KISSAT, '-q', cnf] + ([drat] if proof else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if 's SATISFIABLE' in r.stdout:
            return False, None
        if 's UNSATISFIABLE' not in r.stdout:
            raise RuntimeError('kissat gave no verdict')
        if not proof:
            return True, None
        d = subprocess.run([DRATTRIM, cnf, drat], capture_output=True,
                           text=True)
        return True, ('s VERIFIED' in d.stdout)
    finally:
        for p in (cnf, drat):
            if os.path.exists(p):
                os.unlink(p)


def main(path):
    rec = pickle.load(open(path, 'rb'))
    points, claimed, primes = rec['points'], rec['edges'], rec['primes']
    field = Field(primes)
    n = len(points)
    for x, y in points:
        assert len(x) == field.n and len(y) == field.n, 'bad field element'
        assert all(isinstance(c, Fraction) for c in x + y), 'non-exact entry'
    print(f'{n} vertices with exact coordinates in '
          f'Q({", ".join("sqrt%d" % p for p in primes)})')

    exact = exact_edges(field, points)
    claimed = {tuple(sorted(e)) for e in claimed}
    assert exact == claimed, (f'edge mismatch: claimed {len(claimed)}, '
                              f'exact {len(exact)}, '
                              f'symmetric difference {len(exact ^ claimed)}')
    print(f'{len(exact)} unit edges, each with dx^2 + dy^2 = 1 exactly, and no '
          f'unit pair missing')

    un4, ok = not_k_colorable(n, sorted(exact), 4)
    assert un4, 'the graph IS 4-colorable'
    assert ok, 'drat-trim did not verify the UNSAT proof'
    print('not 4-colorable: kissat UNSAT, drat-trim s VERIFIED')

    if os.environ.get('SKIP5') != '1':
        un5, _ = not_k_colorable(n, sorted(exact), 5, proof=False)
        assert not un5, 'the graph is not 5-colorable either'
        print('5-colorable: chromatic number is exactly 5')

    print(f'PASS: {n}-vertex 5-chromatic unit-distance graph')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'witness.pkl')

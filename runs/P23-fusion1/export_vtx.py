"""Export a (points, edges) pkl (field coords over given primes) to a readable
.vtx (Mathematica-style exact coordinates, reparseable by mfield.load_vtx) +
.edges file."""
import pickle, sys
from fractions import Fraction as F
from mfield import MField


def elem_to_mathematica(K, x):
    parts = []
    for m, c in enumerate(x):
        if not c:
            continue
        rv = K._radval[m]
        cs = str(c.numerator) if c.denominator == 1 else f'{c.numerator}/{c.denominator}'
        if m == 0:
            parts.append(cs)
        else:
            parts.append(f'({cs})*Sqrt[{rv}]')
    if not parts:
        return '0'
    return ' + '.join(parts)


def main():
    pkl, primes_s, out = sys.argv[1], sys.argv[2], sys.argv[3]
    primes = tuple(int(x) for x in primes_s.split(','))
    K = MField(primes)
    pts, edges = pickle.load(open(pkl, 'rb'))
    with open(out + '.vtx', 'w') as f:
        for (x, y) in pts:
            f.write('{%s, %s}\n' % (elem_to_mathematica(K, x), elem_to_mathematica(K, y)))
    with open(out + '.edges', 'w') as f:
        for a, b in sorted((min(u, v), max(u, v)) for u, v in edges):
            f.write(f'{a} {b}\n')
    print(f'wrote {out}.vtx ({len(pts)} vertices) and {out}.edges ({len(edges)} edges)')


if __name__ == '__main__':
    main()

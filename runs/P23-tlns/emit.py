"""Emit a self-contained witness file from a universe + vertex subset.

The subset pickles produced by the search only carry indices into the universe;
this writes out the exact coordinates and the *recomputed* exact edge list, so
`verify.py` can check the witness with no other file present.

Usage: python3 emit.py UNIVERSE.pkl SUBSET.pkl OUT.pkl
"""
import pickle
import sys

import mfield

F = mfield.MField([3, 5, 11])


def emit(univ, subset, out):
    pts, _ = pickle.load(open(univ, 'rb'))
    S = sorted(pickle.load(open(subset, 'rb')))
    points = [pts[v] for v in S]
    z = [(F.to_float(x), F.to_float(y)) for x, y in points]
    edges = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dxf, dyf = z[i][0] - z[j][0], z[i][1] - z[j][1]
            if abs(dxf * dxf + dyf * dyf - 1.0) > 1e-4:
                continue
            dx = F.sub(points[i][0], points[j][0])
            dy = F.sub(points[i][1], points[j][1])
            if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
                edges.append((i, j))
    pickle.dump({'points': points, 'edges': edges, 'primes': [3, 5, 11],
                 'universe': univ, 'source': subset}, open(out, 'wb'))
    print(f'{len(points)} vertices, {len(edges)} exact edges -> {out}')


if __name__ == '__main__':
    emit(sys.argv[1], sys.argv[2], sys.argv[3])

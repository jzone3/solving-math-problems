"""Load a DIMACS 'p edge' graph into a (points, edges) pool pickle for
coremin.py / greedy.py. Coordinates are placeholders (ints): SAT-core
minimization only needs the edge structure. Any induced subgraph of a
unit-distance graph is a unit-distance graph, so minimizing the *structure*
is valid; exact coordinates are recovered separately only if a witness < 509
emerges."""
import pickle, sys

src, out = sys.argv[1], sys.argv[2]
E = []
n = 0
for line in open(src):
    line = line.strip()
    if line.startswith('p'):
        parts = line.split()
        n = int(parts[2])
    elif line.startswith('e'):
        _, a, b = line.split()
        a, b = int(a) - 1, int(b) - 1  # 0-index
        if a != b:
            E.append((min(a, b), max(a, b)))
E = sorted(set(E))
allp = list(range(n))  # placeholder "coords"
pickle.dump((allp, E), open(out, 'wb'))
print(f'{out}: {n} vertices, {len(E)} edges')

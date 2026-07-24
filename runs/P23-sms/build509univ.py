"""Build a universe pkl from the exact 509-vertex Parts record (solutions/P23).
Used to validate the k=4 CEGAR machinery on a universe KNOWN to be non-4-colorable,
and to constructively re-derive that the record is the minimum non-4-colorable subset
of itself (vertex-critical)."""
import sys, os, pickle
from mfield import MField, load_vtx

VTX = os.path.join(os.path.dirname(__file__), "..", "..",
                   "solutions", "P23", "v509e2442.vtx")
fld = MField((3, 5, 11))
pts = load_vtx(fld, VTX)
print(f"parsed {len(pts)} vertices into Q(sqrt3,sqrt5,sqrt11)")
assert len(set(pts)) == len(pts), "dup coords"
# exact edges
ONE = fld.ONE
import math
fx = [(fld.to_float(p[0]), fld.to_float(p[1])) for p in pts]
cell = 1.0
grid = {}
for i, (x, y) in enumerate(fx):
    grid.setdefault((int(math.floor(x)), int(math.floor(y))), []).append(i)
edges = []
for i, (x, y) in enumerate(fx):
    ci, cj = int(math.floor(x)), int(math.floor(y))
    cand = []
    for a in range(ci - 1, ci + 2):
        for b in range(cj - 1, cj + 2):
            cand += grid.get((a, b), [])
    for j in cand:
        if j <= i:
            continue
        dx, dy = x - fx[j][0], y - fx[j][1]
        if abs(dx * dx + dy * dy - 1.0) > 1e-6:
            continue
        if fld.norm2(pts[i], pts[j]) == ONE:
            edges.append((i, j))
edges.sort()
print(f"{len(edges)} exact unit edges")
with open("U_509.pkl", "wb") as f:
    pickle.dump({"points": pts, "edges": edges, "perms": [], "primes": (3, 5, 11)}, f)
print("wrote U_509.pkl")

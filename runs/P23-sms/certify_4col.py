"""Certify that a universe is 4-colorable (=> contains NO 5-chromatic subgraph),
by producing a proper 4-coloring with kissat and INDEPENDENTLY checking, in exact
integer arithmetic, that every one of the universe's exact unit-distance edges is
bichromatic. A proper coloring is a self-verifying certificate of 4-colorability.
Prints PASS + the coloring's class sizes."""
import sys, pickle, subprocess, tempfile, os
KISSAT = os.path.expanduser("~/p23/kissat/build/kissat")

path = sys.argv[1]
with open(path, "rb") as f:
    u = pickle.load(f)
n = len(u["points"])
edges = u["edges"]
k = 4
var = lambda v, c: v * k + c + 1
cls = []
for v in range(n):
    cls.append([var(v, c) for c in range(k)])
for (a, b) in edges:
    for c in range(k):
        cls.append([-var(a, c), -var(b, c)])
with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
    cnf = f.name
    f.write(f"p cnf {n*k} {len(cls)}\n")
    for c in cls:
        f.write(" ".join(map(str, c)) + " 0\n")
r = subprocess.run([KISSAT, "-q", cnf], capture_output=True, text=True)
os.unlink(cnf)
if "s SATISFIABLE" not in r.stdout:
    print(f"{path}: NOT 4-colorable (kissat != SAT) -> cannot certify")
    sys.exit(1)
model = set()
for line in r.stdout.splitlines():
    if line.startswith("v "):
        for tok in line[2:].split():
            l = int(tok)
            if l > 0:
                model.add(l)
# at-least-one + edge constraints force adjacent color-SETS disjoint, so picking the
# min assigned color per vertex yields a proper coloring.
color = [None] * n
for v in range(n):
    for c in range(k):
        if var(v, c) in model:
            color[v] = c
            break
assert all(c is not None for c in color), "some vertex uncolored"
# independent check: every exact edge is bichromatic
bad = [(a, b) for (a, b) in edges if color[a] == color[b]]
sizes = [color.count(c) for c in range(k)]
if bad:
    print(f"{path}: FAIL - {len(bad)} monochromatic edges")
    sys.exit(1)
print(f"{path}: n={n} edges={len(edges)} proper 4-coloring VERIFIED "
      f"(class sizes {sizes}) => chi<=4 => NO 5-chromatic subgraph. PASS")

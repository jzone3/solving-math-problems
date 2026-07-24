"""Quick: is the WHOLE universe k-colorable? (kissat on the direct k-coloring CNF)
If UNSAT for k=4 => chi(U)>=5 => U contains a 5-chromatic subgraph (worth mining).
If SAT   for k=4 => chi(U)<=4 => NO 5-chromatic subgraph exists anywhere in U."""
import sys, pickle, subprocess, tempfile, os, time
KISSAT = os.path.expanduser("~/p23/kissat/build/kissat")

path = sys.argv[1]
k = int(sys.argv[2]) if len(sys.argv) > 2 else 4
with open(path, "rb") as f:
    u = pickle.load(f)
n = len(u["points"])
edges = u["edges"]
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
t = time.time()
r = subprocess.run([KISSAT, "-q", cnf], capture_output=True, text=True)
res = "UNSAT" if "s UNSATISFIABLE" in r.stdout else ("SAT" if "s SATISFIABLE" in r.stdout else "UNKNOWN")
os.unlink(cnf)
print(f"{path}: n={n} edges={len(edges)} {k}-coloring={res} ({time.time()-t:.1f}s)"
      f"  => chi(U){'>=' if res=='UNSAT' else '<='}{k+1 if res=='UNSAT' else k}")

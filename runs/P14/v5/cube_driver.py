"""Cube-and-conquer driver for reduced I1: level-2 cubes fix Q rows 0,1,2.
Dedupe: swapping Q rows 0,1 swaps classes C2<->C3, i.e. (a,b,c,d)~(a,c,b,d),
so keep b<=c. Runs kissat on each cube with a per-cube timeout, logs results.
Any SAT cube => witness. All cubes UNSAT => b2=14 sector of I1 is empty.
"""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor

KISSAT = "/home/ubuntu/kissat/build/kissat"
TL = int(sys.argv[1]) if len(sys.argv) > 1 else 1800

cubes = []
for t in range(8):
    for a in range(min(t, 7) + 1):
        for b in range(min(7 - t, 7 - a) + 1):
            for c in range(b, min(7 - t, 7 - a - b) + 1):
                d = 7 - a - b - c
                if 0 <= d <= t:
                    cubes.append((t, a, b, c, d))
print(f"{len(cubes)} cubes, TL={TL}s each", flush=True)

def run(cube):
    t, a, b, c, d = cube
    tag = f"{t}_{a}{b}{c}{d}"
    cnf = f"cc/cube_{tag}.cnf"
    if not os.path.exists(cnf):
        with open(cnf, "w") as f:
            subprocess.run(["python3", "i1_sat.py", str(t), str(a), str(b),
                            str(c), str(d)], stdout=f, check=True)
    p = subprocess.run(["timeout", str(TL), KISSAT, "-q", cnf],
                       capture_output=True, text=True)
    out = p.stdout
    if "s SATISFIABLE" in out:
        res = "SAT"
        with open(f"cc/model_{tag}.txt", "w") as f:
            f.write(out)
    elif "s UNSATISFIABLE" in out:
        res = "UNSAT"
    else:
        res = "TIMEOUT"
    print(f"cube {tag}: {res}", flush=True)
    return (tag, res)

os.makedirs("cc", exist_ok=True)
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(run, cubes))
n = {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}
for _, r in results: n[r] += 1
print("SUMMARY:", n, flush=True)

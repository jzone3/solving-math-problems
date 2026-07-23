#!/usr/bin/env python3
"""Encoding self-test: K6 -> (3,3)^e (UNSAT expected), K5 -/-> (SAT expected),
since R(3,3)=6. Uses same clause scheme as gen_cnf.py, solved with kissat."""
import itertools, subprocess, sys, tempfile, os

def arrow_cnf(n):
    edges = list(itertools.combinations(range(n), 2))
    var = {e: i + 1 for i, e in enumerate(edges)}
    cls = []
    for t in itertools.combinations(range(n), 3):
        a, b, c = var[(t[0], t[1])], var[(t[0], t[2])], var[(t[1], t[2])]
        cls.append((a, b, c)); cls.append((-a, -b, -c))
    return len(edges), cls

for n, expect in ((5, 10), (6, 20)):  # kissat exit: 10 SAT, 20 UNSAT
    nv, cls = arrow_cnf(n)
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")
        path = f.name
    r = subprocess.run(["kissat", "-q", path], capture_output=True)
    os.unlink(path)
    status = {10: "SAT", 20: "UNSAT"}.get(r.returncode, r.returncode)
    print(f"K{n}: {status} (expected {'SAT' if expect==10 else 'UNSAT'})")
    assert r.returncode == expect
print("SELF-TEST PASS")

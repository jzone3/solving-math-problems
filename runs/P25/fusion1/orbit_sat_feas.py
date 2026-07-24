#!/usr/bin/env python3
"""SAT feasibility for one cyclic monomial symmetry class.

Usage:
  orbit_sat_feas.py TARGET "lam" "assign" WORKDIR [TIMEOUT] [--proof]

Writes instance.cnf, proof.drat, and (on SAT) code.txt in WORKDIR.  The
weighted bound is encoded by expanding each orbit variable into one repeated
literal per orbit member and applying a capped unary totalizer.
"""
import ast
import os
import subprocess
import sys
import time

N = 729
S3 = {"id": (0, 1, 2), "tau": (1, 0, 2), "sigma": (1, 2, 0)}


def digits(w):
    return [(w // 3**i) % 3 for i in range(6)]


def undig(d):
    return sum(v * 3**i for i, v in enumerate(d))


BALL = []
for w in range(N):
    d = digits(w)
    b = [w]
    for i in range(6):
        for v in (1, 2):
            e = d[:]
            e[i] = (e[i] + v) % 3
            b.append(undig(e))
    BALL.append(b)


def build_g(cycles):
    perm = [0] * 6
    smap = [S3["id"]] * 6
    pos = 0
    for length, symbol in cycles:
        idxs = list(range(pos, pos + length))
        for k, i in enumerate(idxs):
            perm[i] = idxs[(k + 1) % length]
        smap[idxs[-1]] = S3[symbol]
        pos += length
    return perm, smap


def apply_g(perm, smap, w):
    d = digits(w)
    e = [0] * 6
    for i in range(6):
        e[perm[i]] = smap[i][d[i]]
    return undig(e)


def orbits_of(perm, smap):
    seen = [False] * N
    orbits = []
    orb_id = [0] * N
    for w in range(N):
        if seen[w]:
            continue
        orbit = []
        x = w
        while not seen[x]:
            seen[x] = True
            orb_id[x] = len(orbits)
            orbit.append(x)
            x = apply_g(perm, smap, x)
        orbits.append(orbit)
    return orbits, orb_id


class CNF:
    def __init__(self):
        self.clauses = []
        self.nv = 0

    def new_var(self):
        self.nv += 1
        return self.nv

    def add(self, *lits):
        self.clauses.append(list(lits))

    def write(self, path):
        with open(path, "w") as f:
            f.write(f"p cnf {self.nv} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")


def merge_totalizer(cnf, left, right, cap):
    """Merge unary vectors, where v[i] means count >= i+1."""
    out_len = min(cap, len(left) + len(right))
    out = [cnf.new_var() for _ in range(out_len)]
    for i, a in enumerate(left, 1):
        if i <= out_len:
            cnf.add(-a, out[i - 1])
    for j, b in enumerate(right, 1):
        if j <= out_len:
            cnf.add(-b, out[j - 1])
    for i, a in enumerate(left, 1):
        for j, b in enumerate(right, 1):
            if i + j <= out_len:
                cnf.add(-a, -b, out[i + j - 1])
            else:
                cnf.add(-a, -b)
    for i in range(out_len - 1):
        cnf.add(-out[i + 1], out[i])
    return out


def totalizer_atmost(cnf, lits, bound):
    # A balanced merge tree keeps propagation and construction compact.
    vectors = [[lit] for lit in lits]
    while len(vectors) > 1:
        nxt = []
        for i in range(0, len(vectors), 2):
            if i + 1 == len(vectors):
                nxt.append(vectors[i])
            else:
                nxt.append(merge_totalizer(cnf, vectors[i], vectors[i + 1], bound + 1))
        vectors = nxt
    if vectors and len(vectors[0]) > bound:
        cnf.add(-vectors[0][bound])


def build_cnf(orbits, orb_id, target):
    cnf = CNF()
    # Orbit variables are deliberately 1..M, simplifying model decoding.
    cnf.nv = len(orbits)
    for w in range(N):
        cnf.add(*sorted({orb_id[b] + 1 for b in BALL[w]}))
    expanded = [j + 1 for j, orbit in enumerate(orbits) for _ in orbit]
    totalizer_atmost(cnf, expanded, target)
    return cnf


def main():
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    target = int(sys.argv[1])
    lam = ast.literal_eval(sys.argv[2])
    assign = ast.literal_eval(sys.argv[3])
    if isinstance(assign, str):
        assign = (assign,)
    workdir = sys.argv[4]
    timeout = float(sys.argv[5]) if len(sys.argv) > 5 else 7200.0
    with_proof = "--proof" in sys.argv[5:]
    os.makedirs(workdir, exist_ok=True)
    perm, smap = build_g(list(zip(lam, assign)))
    orbits, orb_id = orbits_of(perm, smap)
    cnf = build_cnf(orbits, orb_id, target)
    cnf_path = os.path.join(workdir, "instance.cnf")
    proof_path = os.path.join(workdir, "proof.drat")
    cnf.write(cnf_path)
    kissat = os.environ.get("KISSAT", "/home/ubuntu/repos/kissat-build/build/kissat")
    cmd = [kissat, cnf_path]
    if with_proof:
        cmd = [kissat, "--no-binary", cnf_path, proof_path]
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=workdir, text=True, capture_output=True,
                              timeout=timeout)
        status = {10: "SAT", 20: "UNSAT"}.get(proc.returncode, "UNDECIDED")
    except subprocess.TimeoutExpired as exc:
        proc = exc
        status = "UNDECIDED"
    elapsed = time.monotonic() - started
    with open(os.path.join(workdir, "kissat.log"), "w") as f:
        f.write(getattr(proc, "stdout", "") or "")
        f.write(getattr(proc, "stderr", "") or "")
    if status == "UNSAT" and with_proof:
        drat = os.environ.get("DRAT_TRIM", "/home/ubuntu/repos/drat-trim-build/drat-trim")
        if os.path.exists(drat):
            check = subprocess.run([drat, cnf_path, proof_path],
                                   cwd=workdir, text=True, capture_output=True)
            with open(os.path.join(workdir, "drat-trim.log"), "w") as f:
                f.write(check.stdout + check.stderr)
            print(f"DRAT_VERIFY rc={check.returncode}", flush=True)
            try:
                os.unlink(proof_path)
            except FileNotFoundError:
                pass
    print(f"RESULT {status} lam={lam} assign={assign} orbits={len(orbits)} "
          f"vars={cnf.nv} clauses={len(cnf.clauses)} seconds={elapsed:.3f}",
          flush=True)
    if status == "SAT":
        model = set()
        for line in (proc.stdout or "").splitlines():
            if line.startswith("v "):
                model.update(int(x) for x in line.split()[1:] if x != "0")
        chosen = [w for j, orbit in enumerate(orbits, 1) if j in model for w in orbit]
        code_path = os.path.join(workdir, "code.txt")
        with open(code_path, "w") as f:
            for w in sorted(chosen):
                f.write("".join(map(str, digits(w))) + "\n")
        verify = subprocess.run(
            [sys.executable, "/home/ubuntu/repos/solving-math-problems/runs/P25/v1/verify.py", code_path],
            text=True, capture_output=True)
        with open(os.path.join(workdir, "verify.log"), "w") as f:
            f.write(verify.stdout + verify.stderr)
        print(f"CODE size={len(chosen)} verify_rc={verify.returncode}", flush=True)


if __name__ == "__main__":
    main()

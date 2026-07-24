#!/usr/bin/env python3
"""Native pseudo-Boolean feasibility search using RoundingSat.

Usage:
  orbit_pb_feas.py TARGET "lam" "assign" WORKDIR [TIMEOUT]
"""
import ast
import os
import re
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


def write_opb(path, orbits, orb_id, target):
    constraints = []
    for w in range(N):
        cols = sorted({orb_id[b] + 1 for b in BALL[w]})
        constraints.append(" ".join(f"+1 x{j}" for j in cols) + " >= 1;")
    weighted = " ".join(f"-{len(orbit)} x{j + 1}"
                        for j, orbit in enumerate(orbits))
    constraints.append(weighted + f" >= -{target};")
    with open(path, "w") as f:
        f.write(f"* #variable= {len(orbits)} #constraint= {len(constraints)}\n")
        f.write("* orbit covering feasibility instance\n")
        for line in constraints:
            f.write(line + "\n")


def decode_model(output, m):
    chosen = set()
    # RoundingSat's --print-sol output uses xN=1; tolerate common variants.
    for match in re.finditer(r"\bx(\d+)\s*=\s*([01])", output):
        if match.group(2) == "1":
            chosen.add(int(match.group(1)))
    for line in output.splitlines():
        if line.startswith("v "):
            for token in line.split()[1:]:
                if token.startswith("x") and token[1:].isdigit():
                    chosen.add(int(token[1:]))
    return {j for j in chosen if 1 <= j <= m}


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
    os.makedirs(workdir, exist_ok=True)
    orbits, orb_id = orbits_of(*build_g(list(zip(lam, assign))))
    opb_path = os.path.join(workdir, "instance.opb")
    write_opb(opb_path, orbits, orb_id, target)
    solver = os.environ.get(
        "ROUNDINGSAT", "/home/ubuntu/repos/roundingsat-build/build/roundingsat")
    started = time.monotonic()
    try:
        proc = subprocess.run([solver, "--verbosity=0", "--print-sol=1", opb_path],
                              cwd=workdir, text=True, capture_output=True,
                              timeout=timeout)
        output = (proc.stdout or "") + (proc.stderr or "")
        if "s UNSATISFIABLE" in output or "UNSATISFIABLE" in output:
            status = "UNSAT"
        elif "s SATISFIABLE" in output or "SATISFIABLE" in output:
            status = "SAT"
        else:
            status = "UNDECIDED"
    except subprocess.TimeoutExpired as exc:
        proc = exc
        output = (exc.stdout or "") + (exc.stderr or "")
        status = "UNDECIDED"
    elapsed = time.monotonic() - started
    with open(os.path.join(workdir, "roundingsat.log"), "w") as f:
        f.write(output)
    print(f"RESULT {status} lam={lam} assign={assign} orbits={len(orbits)} "
          f"constraints=730 seconds={elapsed:.3f}", flush=True)
    if status == "SAT":
        chosen_ids = decode_model(output, len(orbits))
        chosen = [w for j, orbit in enumerate(orbits, 1) if j in chosen_ids for w in orbit]
        code_path = os.path.join(workdir, "code.txt")
        with open(code_path, "w") as f:
            for w in sorted(chosen):
                f.write("".join(map(str, digits(w))) + "\n")
        verify = subprocess.run(
            [sys.executable, "/home/ubuntu/repos/solving-math-problems/runs/P25/v1/verify.py",
             code_path], text=True, capture_output=True)
        with open(os.path.join(workdir, "verify.log"), "w") as f:
            f.write(verify.stdout + verify.stderr)
        print(f"CODE size={len(chosen)} verify_rc={verify.returncode}", flush=True)


if __name__ == "__main__":
    main()

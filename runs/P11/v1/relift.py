#!/usr/bin/env python3
"""Re-run TIMEOUT'd pinned lifts from pipeline logs with a bigger budget."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = os.path.expanduser("~/bin/kissat")
N, K = int(sys.argv[1]), int(sys.argv[2])
TL = int(sys.argv[3])
logs = sys.argv[4:]

seen = set()
jobs = []
pat = re.compile(r"LIFT\[(\S+)\] d=(\d+) b=\[([-0-9, ]+)\] -> TIMEOUT")
pat2 = re.compile(r"\[(\S+?)#(\d+)\] b=\[([-0-9, ]+)\] -> TIMEOUT")
for lg in logs:
    for line in open(lg):
        m = pat.search(line)
        if m:
            d, b = int(m.group(2)), [int(v) for v in m.group(3).split(",")]
        else:
            m = pat2.search(line)
            if not m:
                continue
            b = [int(v) for v in m.group(3).split(",")]
            d = len(b)
        key = (d, tuple(b))
        if key not in seen:
            seen.add(key)
            jobs.append((d, b))
print(f"{len(jobs)} timeout lifts to retry at TL={TL}", flush=True)
for i, (d, b) in enumerate(jobs):
    cnf = f"/tmp/relift{N}_{i}.cnf"
    out = f"/tmp/relift{N}_{i}.out"
    spec = f"--liftsum={d}:" + ",".join(map(str, b))
    subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"), "encode",
                    str(N), str(K), cnf, spec, "--nofix0"], check=True, capture_output=True)
    with open(out, "w") as f:
        r = subprocess.run(["timeout", str(TL), KISSAT, "-q", cnf], stdout=f)
    res = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "TIMEOUT")
    print(f"[{i}] d={d} b={b} -> {res}", flush=True)
    if res == "SAT":
        dec = subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"), "decode",
                              str(N), str(K), "x", out], capture_output=True, text=True)
        for line in dec.stdout.splitlines():
            if line.startswith("ROW"):
                row = json.loads(line[4:])
                wp = os.path.join(HERE, f"witness_{N}_{K}.json")
                json.dump({"n": N, "k": K, "row": row}, open(wp, "w"))
                print(f"WITNESS WRITTEN {wp}", flush=True)
        break
    os.remove(cnf); os.remove(out)
print("RELIFT DONE", flush=True)

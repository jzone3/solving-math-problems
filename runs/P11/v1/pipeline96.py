#!/usr/bin/env python3
"""Multi-level fold-and-lift DFS pipeline for CW(96,36).

Levels: canonical folds mod 6 (DFS enum) -> mod 12 -> mod 24 -> mod 48 (each
SAT-enumerated conditioned on the parent fold) -> final kissat lift to n=96
with liftsum=48:b (pair-sum pinning, validated fast on CW(48,36)).

DFS order so lifts are attempted early. Per-branch enumeration budgets and
caps; everything logged. Propriety clauses are in the final lift encoding.

Env: WORKER_ID/NUM_WORKERS shard the top-level mod-6 classes.
     ENUM_TL per-branch seconds, LIFT_TL lift seconds, MAX_B per-branch cap.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fold_enum import enumerate_folds
from stageA_fold import canon
from stageA_sat import build

KISSAT = os.path.expanduser("~/bin/kissat")
N = int(os.environ.get("CW_N", "96"))
K = int(os.environ.get("CW_K", "36"))
TOP_D = int(os.environ.get("TOP_D", "6"))
LEVELS = [int(v) for v in os.environ.get("LEVELS", "12,24,48").split(",")]
LIFT_TL = int(os.environ.get("LIFT_TL", "600"))
ENUM_TL = int(os.environ.get("ENUM_TL", "600"))
MAX_B = int(os.environ.get("MAX_B", "500"))
WORKER_ID = int(os.environ.get("WORKER_ID", "0"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", "1"))
LIFT_D = LEVELS[-1]


def sat_enum(d, subfold, budget, tag):
    """Enumerate folds mod d conditioned on parent fold (d_par, values)."""
    cnf, U, V, units = build(N, K, d, [subfold])
    path = f"/tmp/enum{N}_w{WORKER_ID}_{tag}.cnf"
    t0 = time.time()
    out = []
    clauses = cnf.clauses
    nv = cnf.nv
    while time.time() - t0 < budget and len(out) < MAX_B:
        with open(path, "w") as f:
            f.write(f"p cnf {nv} {len(clauses)}\n")
            for cl in clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")
        left = int(budget - (time.time() - t0))
        if left <= 1:
            break
        r = subprocess.run(["timeout", str(left), KISSAT, "-q", path],
                           capture_output=True, text=True)
        if r.returncode == 20:
            os.remove(path)
            return out, "exhausted"
        if r.returncode != 10:
            break
        mdl = set()
        for line in r.stdout.splitlines():
            if line.startswith("v"):
                mdl.update(int(t) for t in line.split()[1:] if int(t) > 0)
        b = [sum(1 for l in U[j] if l in mdl) - sum(1 for l in V[j] if l in mdl)
             for j in range(d)]
        out.append(b)
        clauses.append([-l if l in mdl else l for l in units])
    if os.path.exists(path):
        os.remove(path)
    return out, "budget"


def lift(b, tag, d=None):
    d = d or LIFT_D
    cnf_path = f"/tmp/lift{N}_{tag}.cnf"
    out_path = f"/tmp/lift{N}_{tag}.out"
    spec = f"--liftsum={d}:" + ",".join(map(str, b))
    subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"), "encode",
                    str(N), str(K), cnf_path, spec, "--nofix0"],
                   check=True, capture_output=True)
    with open(out_path, "w") as f:
        r = subprocess.run(["timeout", str(LIFT_TL), KISSAT, "-q", cnf_path], stdout=f)
    res = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "TIMEOUT")
    row = None
    if res == "SAT":
        dec = subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"), "decode",
                              str(N), str(K), "x", out_path], capture_output=True, text=True)
        for line in dec.stdout.splitlines():
            if line.startswith("ROW"):
                row = json.loads(line[4:])
        print(dec.stdout, flush=True)
    os.remove(cnf_path); os.remove(out_path)
    return res, row


STATS = {"lift": {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}, "enum_branches": 0}


def dfs(level, parent_fold, tag):
    pd, pb = parent_fold
    if N // pd <= 5:
        # early lift attempt at this level: SAT wins, UNSAT prunes subtree,
        # TIMEOUT falls through to deeper enumeration
        res, row = lift(pb, tag, pd)
        STATS["lift"][res] += 1
        print(f"  LIFT[{tag}] d={pd} b={pb} -> {res}", flush=True)
        if row:
            wpath = os.path.join(HERE, f"witness_{N}_{K}.json")
            json.dump({"n": N, "k": K, "row": row}, open(wpath, "w"))
            print(f"WITNESS WRITTEN {wpath}", flush=True)
            raise SystemExit(0)
        if res == "UNSAT" or level == len(LEVELS):
            return
    if level == len(LEVELS):
        return
    d = LEVELS[level]
    bs, status = sat_enum(d, parent_fold, ENUM_TL, tag)
    STATS["enum_branches"] += 1
    print(f"[{tag}] d={d} parent={parent_fold[0]} -> {len(bs)} folds ({status})", flush=True)
    for i, b in enumerate(bs):
        dfs(level + 1, (d, b), f"{tag}.{i}")


def main():
    ftop = enumerate_folds(N, K, TOP_D)
    ctops = sorted(set(canon(c, TOP_D) for c in ftop))
    print(f"mod{TOP_D}: {len(ftop)} raw -> {len(ctops)} classes", flush=True)
    for i, ct in enumerate(ctops):
        if i % NUM_WORKERS != WORKER_ID:
            continue
        print(f"=== top-level class {i}: {list(ct)} ===", flush=True)
        dfs(0, (TOP_D, list(ct)), f"c{i}")
    print("PIPELINE COMPLETE", STATS, flush=True)


if __name__ == "__main__":
    main()

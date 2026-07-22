#!/usr/bin/env python3
"""Multi-level fold-and-lift pipeline for CW(105,36).

Level 0: enumerate folds mod 5 (canonical classes) and mod 7 (RAW, since the
         group action was spent canonicalizing mod 5) -- both cheap by DFS.
Level 1: for each (c5, c7raw) pair, SAT-enumerate folds b mod 35 with both
         subfold constraints pinned (stageA_sat build + incremental cadical).
Level 2: for each b found, kissat the full CW(105,36) lift with liftsum=35:b.

Any SAT lift -> decode row, verify, write witness. Logs JSON checkpoints.
"""
import json, os, subprocess, sys, time
from pysat.solvers import Cadical195

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fold_enum import enumerate_folds
from stageA_fold import canon
from stageA_sat import build

KISSAT = os.path.expanduser("~/bin/kissat")
N, K = 105, 36
LIFT_TL = int(os.environ.get("LIFT_TL", "300"))
ENUM_TL = int(os.environ.get("ENUM_TL", "600"))  # per (c5,c7) branch, seconds
MAX_B_PER_BRANCH = int(os.environ.get("MAX_B", "2000"))
WORKER_ID = int(os.environ.get("WORKER_ID", "0"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", "1"))


def enum_level1(c5, c7, budget, tag="e"):
    """File-based kissat enumeration with per-call wall timeouts (robust to
    hard instances, unlike blocking incremental cadical)."""
    cnf, U, V, units = build(N, K, 35, [(5, list(c5)), (7, list(c7))])
    path = f"/tmp/enum105_w{WORKER_ID}_{tag}.cnf"
    t0 = time.time()
    out = []
    clauses = cnf.clauses
    nv = cnf.nv
    while time.time() - t0 < budget and len(out) < MAX_B_PER_BRANCH:
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
        b = []
        for j in range(35):
            b.append(sum(1 for l in U[j] if l in mdl) - sum(1 for l in V[j] if l in mdl))
        out.append(b)
        clauses.append([-l if l in mdl else l for l in units])
    if os.path.exists(path):
        os.remove(path)
    return out, "budget"


def lift(b, tag):
    cnf_path = f"/tmp/lift105_{tag}.cnf"
    out_path = f"/tmp/lift105_{tag}.out"
    spec = "--liftsum=35:" + ",".join(map(str, b))
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


def main():
    f5 = enumerate_folds(N, K, 5)
    f7 = enumerate_folds(N, K, 7)
    c5s = sorted(set(canon(c, 5) for c in f5))
    print(f"mod5: {len(f5)} raw -> {len(c5s)} classes; mod7 raw: {len(f7)}", flush=True)
    state_path = os.path.join(HERE, f"pipeline105_state_w{WORKER_ID}.json")
    state = {"done": [], "b_stats": {}, "lift_stats": {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}}
    if os.path.exists(state_path):
        state = json.load(open(state_path))
    for i5, c5 in enumerate(c5s):
        for i7, c7 in enumerate(f7):
            if (i5 * len(f7) + i7) % NUM_WORKERS != WORKER_ID:
                continue
            key = f"{i5}_{i7}"
            if key in state["done"]:
                continue
            bs, status = enum_level1(c5, c7, ENUM_TL)
            print(f"[{key}] c5={list(c5)} c7={c7} -> {len(bs)} folds ({status})", flush=True)
            state["b_stats"][key] = {"count": len(bs), "status": status}
            for ib, b in enumerate(bs):
                res, row = lift(b, f"w{WORKER_ID}_{key}_{ib}")
                state["lift_stats"][res] += 1
                print(f"  [{key}#{ib}] b={b} -> {res}", flush=True)
                if row:
                    wpath = os.path.join(HERE, f"witness_{N}_{K}.json")
                    json.dump({"n": N, "k": K, "row": row}, open(wpath, "w"))
                    print(f"WITNESS WRITTEN {wpath}", flush=True)
                    json.dump(state, open(state_path, "w"))
                    return
            state["done"].append(key)
            json.dump(state, open(state_path, "w"))
    print("PIPELINE COMPLETE", state["lift_stats"], flush=True)


if __name__ == "__main__":
    main()

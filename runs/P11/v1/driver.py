#!/usr/bin/env python3
"""Branch-and-solve driver: for each folded solution mod d, encode the
streamlined CNF and run kissat with a per-branch time limit. Rounds with
escalating budgets; SAT branch => decode, verify, write witness JSON.

Usage: python3 driver.py n k d timeout_s [start_idx] [end_idx] [tag]
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = os.path.expanduser("~/bin/kissat")


def main():
    n, k, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    tl = int(sys.argv[4])
    lo = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    hi = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    tag = sys.argv[7] if len(sys.argv) > 7 else f"n{n}d{d}"
    sys.path.insert(0, HERE)
    from fold_enum import enumerate_folds
    folds = enumerate_folds(n, k, d)
    print(f"[{tag}] {len(folds)} folded branches (running {lo}..{min(hi,len(folds))-1}), tl={tl}s", flush=True)
    stats = {"SAT": 0, "UNSAT": 0, "TIMEOUT": 0}
    for idx in range(lo, min(hi, len(folds))):
        cs = folds[idx]
        cnf_path = f"/tmp/{tag}_b{idx}.cnf"
        out_path = f"/tmp/{tag}_b{idx}.out"
        spec = f"--classsum={d}:{','.join(map(str, cs))}"
        subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"),
                        "encode", str(n), str(k), cnf_path, spec],
                       check=True, capture_output=True)
        t0 = time.time()
        with open(out_path, "w") as f:
            r = subprocess.run(["timeout", str(tl), KISSAT, "-q", cnf_path], stdout=f)
        el = time.time() - t0
        rc = r.returncode
        res = {10: "SAT", 20: "UNSAT"}.get(rc, "TIMEOUT")
        stats[res] += 1
        print(f"[{tag}] branch {idx} cs={cs} -> {res} ({el:.1f}s)", flush=True)
        if res == "SAT":
            dec = subprocess.run([sys.executable, os.path.join(HERE, "cw_cnf.py"),
                                  "decode", str(n), str(k), "x", out_path],
                                 capture_output=True, text=True)
            print(dec.stdout, flush=True)
            for line in dec.stdout.splitlines():
                if line.startswith("ROW"):
                    row = json.loads(line[4:].replace(" ", "").replace(",]", "]"))
                    wpath = os.path.join(HERE, f"witness_{n}_{k}.json")
                    json.dump({"n": n, "k": k, "row": row}, open(wpath, "w"))
                    print(f"WITNESS WRITTEN {wpath}", flush=True)
            return
        os.remove(cnf_path); os.remove(out_path)
    print(f"[{tag}] DONE stats={stats}", flush=True)


if __name__ == "__main__":
    main()

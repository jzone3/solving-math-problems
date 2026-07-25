"""Iteratively extract DRAT-certified UNSAT cores from one scoped universe."""
import argparse
import json
import os
import pickle
import time

import coremin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_r3.pkl")
    ap.add_argument("--out", default="core_r3.pkl")
    ap.add_argument("--start", default="")
    ap.add_argument("--log", default="logs/core_extract_r3.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-iters", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=7200)
    args = ap.parse_args()

    os.environ["POOL"] = args.pool
    # coremin is imported above for its helpers; reload its pool-specific
    # globals after setting POOL when this script is launched directly.
    import importlib
    global coremin
    coremin = importlib.reload(coremin)
    current = (set(pickle.load(open(args.start, "rb")))
               if args.start else set(range(coremin.NALL)))
    with open(args.log, "a", buffering=1) as log:
        for iteration in range(1, args.max_iters + 1):
            started = time.time()
            status, keep = coremin.solve_core(
                current, seed=args.seed * 1000 + iteration,
                timeout=args.timeout, tag=f"r3core{args.seed}")
            rec = {
                "iteration": iteration,
                "input_vertices": len(current),
                "status": status,
                "seconds": round(time.time() - started, 3),
            }
            if status == "UNSAT":
                assert keep and set(keep) <= current
                current = set(keep)
                rec["core_vertices"] = len(current)
                pickle.dump(sorted(current), open(args.out, "wb"))
                rec["snapshot"] = args.out
            print(json.dumps(rec), flush=True)
            log.write(json.dumps(rec) + "\n")
            if status != "UNSAT" or rec["core_vertices"] >= rec["input_vertices"]:
                break
    print(f"FINAL {len(current)} vertices -> {args.out}", flush=True)


if __name__ == "__main__":
    main()

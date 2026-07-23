#!/usr/bin/env python3
"""Dense finisher: load an INCOMPLETE .part cover (from engine5), run the
dense repair()/one_opt() local search from engine4 in RAM (needs ~3 bytes per
element of Z_N). Writes a verified-format witness on success."""
import argparse
import numpy as np
from engine4 import repair, one_opt


def load(path):
    congs = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            a, v = map(int, line.split())
            congs.append((a, v))
    return congs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part_file")
    ap.add_argument("-N", type=int, required=True)
    ap.add_argument("--budget", type=int, default=3600)
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    N = args.N
    congs = load(args.part_file)
    rem = None
    for cyc in range(args.cycles):
        U = np.ones(N, dtype=bool)
        for a, v in congs:
            U[a::v] = False
        congs, rem = repair(N, None, congs, U, rounds=10**9,
                            t_budget=args.budget // (2 * args.cycles),
                            seed=args.seed + cyc)
        if rem == 0:
            break
        congs, rem = one_opt(N, congs,
                             t_budget=args.budget // (2 * args.cycles),
                             seed=args.seed + cyc)
        print(f"cycle {cyc}: uncovered={rem}", flush=True)
        if rem == 0:
            break
    status = "SUCCESS" if rem == 0 else "INCOMPLETE"
    print(f"finish_dense: {status} congs={len(congs)} uncovered={rem}")
    path = args.out if rem == 0 else args.out + ".part"
    with open(path, "w") as f:
        f.write(f"# finish_dense from {args.part_file} status={status} "
                f"uncovered={rem}\n")
        for a, v in sorted(congs, key=lambda t: t[1]):
            f.write(f"{a} {v}\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()

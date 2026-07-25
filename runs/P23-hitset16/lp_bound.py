"""Fractional LP lower bound for a banked hitting-set instance."""
import argparse
import json
import pickle
import numpy as np
from scipy.optimize import linprog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    bank = pickle.load(open(args.bank, "rb"))
    support = sorted(set().union(*map(set, bank)))
    pos = {v: i for i, v in enumerate(support)}
    a = np.zeros((len(bank), len(support)))
    for row, d in enumerate(bank):
        a[row, [pos[v] for v in d]] = -1.0
    result = linprog(
        np.ones(len(support)), A_ub=a, b_ub=-np.ones(len(bank)),
        bounds=[(0.0, 1.0)] * len(support), method="highs")
    rec = {
        "bank": args.bank,
        "hyperedges": len(bank),
        "support": len(support),
        "status": result.message,
        "lp_bound": float(result.fun) if result.success else None,
    }
    print(json.dumps(rec))
    if args.out:
        json.dump(rec, open(args.out, "w"), indent=2)


if __name__ == "__main__":
    main()

"""Independent Kissat checks for random bank complements."""
import argparse
import os
import pickle
from multiprocessing import Pool


def one(args):
    pool, bank, idx, d = args
    os.environ["POOL"] = pool
    os.environ["WHOLE"] = "1"
    os.environ["FROZEN"] = ""
    import hyperpar as h
    st = h.kissat_color(sorted(set(range(h.NP)) - set(d)), f"bank_{idx}")
    return idx, len(d), bool(st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_r3.pkl")
    ap.add_argument("--bank", default="hyperedges_r3.pkl")
    ap.add_argument("--sample", type=int, default=8)
    ap.add_argument("--out", default="logs/bank_check.log")
    args = ap.parse_args()
    bank = pickle.load(open(args.bank, "rb"))
    import random
    sample = random.Random(917263).sample(bank, min(args.sample, len(bank)))
    jobs = [(args.pool, args.bank, i, d) for i, d in enumerate(sample)]
    with Pool(min(8, len(jobs))) as p:
        results = p.map(one, jobs)
    with open(args.out, "w") as f:
        for idx, size, ok in sorted(results):
            f.write(f"sample={idx} size={size} SAT={ok}\n")
    assert all(ok for _, _, ok in results)
    print(f"checked {len(results)} bank complements: all SAT")


if __name__ == "__main__":
    main()

"""Materialize an induced reduced universe from a core vertex-id list."""
import argparse
import pickle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_r3.pkl")
    ap.add_argument("--core", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pts, edges = pickle.load(open(args.pool, "rb"))
    keep = sorted(pickle.load(open(args.core, "rb")))
    remap = {old: new for new, old in enumerate(keep)}
    red_edges = [(remap[u], remap[v]) for u, v in edges
                 if u in remap and v in remap]
    pickle.dump(([pts[i] for i in keep], red_edges), open(args.out, "wb"))
    print(f"{args.pool}: {len(pts)} -> {len(keep)} vertices, "
          f"{len(edges)} -> {len(red_edges)} edges")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate matched-size v2-style star cubes for comparison."""
import argparse
import json
import random
from pathlib import Path

P = 127
CUBIC = sorted({pow(x, 3, P) for x in range(1, P)})
STAR = [(0, c) for c in CUBIC]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="16,20,30,42")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=22128)
    parser.add_argument("--out", type=Path, default=Path("star_table.json"))
    args = parser.parse_args()
    rng = random.Random(args.seed)
    rows = []
    for size in [int(x) for x in args.sizes.split(",") if x]:
        edges = STAR[:size]
        samples = []
        for _ in range(args.samples):
            values = [rng.randrange(2) for _ in edges]
            # plain.cnf fixes global var 1, edge (0,1), to True.
            if (0, 1) in edges:
                values[edges.index((0, 1))] = 1
            samples.append(
                {
                    "lits": [
                        (i + 1) if value else -(i + 1)
                        for i, value in enumerate(values)
                    ],
                    "edges": [list(e) for e in edges],
                    "global_vars": list(range(1, size + 1)),
                    "vertices": [0],
                }
            )
        rows.append(
            {
                "edges": size,
                "induced_triangles": 0,
                "all_cubes": 1 << size,
                "surviving_cubes": 1 << (size - 1),
                "compression_ratio": 2.0,
                "samples": samples,
            }
        )
        print(f"star |S|={size} samples={len(samples)}")
    args.out.write_text(json.dumps(rows, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

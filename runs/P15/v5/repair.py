"""Phase 2: local-search repair on top of greedy (greedy_cover.greedy).

State: assignment r_d for each usable modulus d (all used).  Maintain
cnt[n] = number of congruences covering n.  Move: pick an uncovered residue n,
pick a modulus d, reassign its class to n mod d; accept if the number of
uncovered residues does not increase (sideways moves allowed), with occasional
random uphill kicks (annealing-lite).  All vectorized per move: O(N/d).
"""
import argparse
import json
import time
from functools import reduce

import numpy as np

from greedy_cover import divisors, greedy


def class_idx(N, d, r):
    return np.arange(r, N, d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", required=True)
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--time", type=float, default=600, help="seconds budget")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    factors = []
    for tok in a.factors.split(","):
        p, _, e = tok.partition("^")
        factors.append((int(p), int(e or 1)))
    N = reduce(lambda x, y: x * y, (p**e for p, e in factors))
    divs = [d for d in divisors(factors) if d >= a.L]
    print(f"N={N}, usable {len(divs)}, budget {sum(1/d for d in divs):.3f}",
          flush=True)

    rng = np.random.default_rng(a.seed)
    chosen, left = greedy(N, a.L, divs, "asc", rng)
    assign = {d: r for r, d in chosen}
    for d in divs:
        if d not in assign:
            assign[d] = int(rng.integers(d))  # use every modulus
    cnt = np.zeros(N, dtype=np.uint16)
    for d, r in assign.items():
        cnt[class_idx(N, d, r)] += 1
    unc = int((cnt == 0).sum())
    print(f"after greedy+fill: uncovered {unc}", flush=True)

    dlist = np.array(divs)
    t0 = time.time()
    it = 0
    best = unc
    while unc > 0 and time.time() - t0 < a.time:
        it += 1
        # pick a random uncovered residue
        zeros = np.flatnonzero(cnt == 0)
        n = int(zeros[rng.integers(len(zeros))])
        # try moduli in random order; take first non-worsening reassignment
        for d in rng.permutation(dlist)[:40]:
            d = int(d)
            r_old, r_new = assign[d], n % d
            if r_old == r_new:
                continue
            old_idx = class_idx(N, d, r_old)
            new_idx = class_idx(N, d, r_new)
            gain = int((cnt[new_idx] == 0).sum())
            loss = int((cnt[old_idx] == 1).sum())
            if gain > loss or (gain == loss and rng.random() < 0.5):
                cnt[old_idx] -= 1
                cnt[new_idx] += 1
                assign[d] = r_new
                unc += loss - gain
                break
        if it % 200 == 0:
            if unc < best:
                best = unc
            print(f"it {it}: uncovered {unc} (best {best}), "
                  f"{time.time()-t0:.0f}s", flush=True)

    print(f"final uncovered {unc} after {it} moves, {time.time()-t0:.0f}s")
    if unc == 0:
        out = a.out or f"witness_L{a.L}_N{N}_repair.json"
        with open(out, "w") as f:
            json.dump({"N": N, "L": a.L,
                       "congruences": [[r, d] for d, r in assign.items()]},
                      f)
        print(f"SUCCESS wrote {out}")


if __name__ == "__main__":
    main()

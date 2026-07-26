"""Greedy destructive minimization with Parts' 8-4-2-1 batching and DRAT core
jumps.  Usage: POOL=pool16.pkl greedy8.py <seed> <start.pkl> [<tag>]
"""
import pickle
import random
import sys

from coremin import solve_core


def attempt(S, batch, rnd, tag):
    """Try deleting `batch` from S; return new S (core) if still UNSAT."""
    cand = set(S) - set(batch)
    if len(cand) <= 4:
        return None
    try:
        st, keep = solve_core(cand, seed=rnd.randrange(10 ** 6),
                              timeout=3600, tag=tag)
    except Exception:
        return None
    return keep if st == "UNSAT" else None


def greedy(S, seed, tag):
    rnd = random.Random(seed)
    S = set(S)
    passno = 0
    while True:
        passno += 1
        removed = 0
        order = sorted(S)
        rnd.shuffle(order)
        k = 0
        while k < len(order):
            group = [v for v in order[k:k + 8] if v in S]
            k += 8
            if not group:
                continue
            res = attempt(S, group, rnd, tag)
            if res is not None:
                S = res
                removed += len(group)
                print(f"{tag} pass{passno}: -{len(group)} (batch8) -> {len(S)}",
                      flush=True)
                pickle.dump(sorted(S), open(f"greedy_{tag}.pkl", "wb"))
                continue
            # split 4-2-1
            stack = [group[:4], group[4:]] if len(group) > 4 else [group]
            while stack:
                g = [v for v in stack.pop() if v in S]
                if not g:
                    continue
                res = attempt(S, g, rnd, tag)
                if res is not None:
                    S = res
                    removed += len(g)
                    print(f"{tag} pass{passno}: -{len(g)} -> {len(S)}",
                          flush=True)
                    pickle.dump(sorted(S), open(f"greedy_{tag}.pkl", "wb"))
                elif len(g) > 1:
                    h = len(g) // 2
                    stack.append(g[:h])
                    stack.append(g[h:])
        print(f"{tag} pass{passno} done removed={removed} n={len(S)}",
              flush=True)
        if removed == 0:
            break
    print(f"{tag} FINAL {len(S)}", flush=True)
    pickle.dump(sorted(S), open(f"greedy_{tag}.pkl", "wb"))


if __name__ == "__main__":
    seed = int(sys.argv[1])
    start = pickle.load(open(sys.argv[2], "rb"))
    tag = sys.argv[3] if len(sys.argv) > 3 else f"g{seed}"
    greedy(start, seed, tag)

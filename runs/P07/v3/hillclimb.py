"""Steepest-ascent hill climb over single edge toggles, seeded from best lollipop/dumbbell.

Usage: python3 hillclimb.py <n>
"""
import sys

from anneal import make_dumbbell_edges, evaluate


def best_seed(n):
    best = (-1.0, None)
    for a in range(2, n - 1):
        for b in (1, 2, 3):
            ell = n - a - b
            if ell < 1:
                continue
            e = make_dumbbell_edges(a, ell, b)
            s, _ = evaluate(n, e)
            if s and s > best[0]:
                best = (s, e)
    return best


def main():
    n = int(sys.argv[1])
    cur, edges = best_seed(n)
    print(f"n={n} seed score {cur:.6f}")
    improved = True
    rounds = 0
    while improved:
        improved = False
        rounds += 1
        best_move, best_s = None, cur
        for u in range(n):
            for v in range(u + 1, n):
                e = (u, v)
                ne = set(edges)
                if e in ne:
                    ne.remove(e)
                else:
                    ne.add(e)
                s, _ = evaluate(n, ne)
                if s is not None and s > best_s + 1e-12:
                    best_s, best_move = s, e
        if best_move:
            e = best_move
            if e in edges:
                edges.remove(e)
            else:
                edges.add(e)
            cur = best_s
            improved = True
            print(f"round {rounds}: toggle {e} -> {cur:.6f}")
    print(f"LOCAL OPT n={n} score={cur:.6f} m={len(edges)} violation={cur > 1}")
    if cur > 1:
        with open(f"viol_hc_n{n}.txt", "w") as f:
            f.write(f"# hillclimb violation n={n} score={cur:.6f}\n")
            for u, v in sorted(edges):
                f.write(f"{u} {v}\n")


if __name__ == "__main__":
    main()

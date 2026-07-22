"""Summarize results.jsonl: top ratios overall and per omega; flag non-multipartite near-misses."""
import json
import sys
from collections import defaultdict

from bn_core import g6_to_adj


def is_complete_multipartite(n, adj):
    # complement's components must all be cliques
    full = (1 << n) - 1
    cadj = [(~adj[i]) & full & ~(1 << i) for i in range(n)]
    seen = 0
    for v in range(n):
        if (seen >> v) & 1:
            continue
        comp = 1 << v
        stack = [v]
        while stack:
            u = stack.pop()
            nb = cadj[u] & ~comp
            while nb:
                w = (nb & -nb).bit_length() - 1
                comp |= 1 << w
                stack.append(w)
                nb &= nb - 1
        seen |= comp
        verts = [i for i in range(n) if (comp >> i) & 1]
        for u in verts:
            if (cadj[u] & comp) != comp & ~(1 << u):
                return False
    return True


def main(path):
    recs = [json.loads(l) for l in open(path)]
    print(f"{len(recs)} restarts logged")
    recs.sort(key=lambda r: -r["ratio"])
    print("\nTop 12 overall:")
    for r in recs[:12]:
        n, adj = g6_to_adj(r["g6"])
        cm = is_complete_multipartite(n, adj)
        print(f"  ratio={r['ratio']:.8f} n={r['n']} m={r['m']} w={r['omega']} "
              f"l2={r['l2']:.4f} mode={r.get('mode','?')} cm={cm}")
    best_w = defaultdict(lambda: None)
    for r in recs:
        w = r["omega"]
        if best_w[w] is None or r["ratio"] > best_w[w]["ratio"]:
            best_w[w] = r
    print("\nBest per omega:")
    for w in sorted(best_w):
        r = best_w[w]
        print(f"  w={w}: ratio={r['ratio']:.8f} n={r['n']} m={r['m']} l2={r['l2']:.4f}")
    print("\nTop 10 non-complete-multipartite:")
    cnt = 0
    for r in recs:
        n, adj = g6_to_adj(r["g6"])
        if not is_complete_multipartite(n, adj):
            print(f"  ratio={r['ratio']:.8f} n={r['n']} m={r['m']} w={r['omega']} "
                  f"l2={r['l2']:.4f} g6={r['g6']}")
            cnt += 1
            if cnt >= 10:
                break


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results.jsonl")

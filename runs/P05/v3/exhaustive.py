"""Sanity cross-check: run the analyzer over ALL connected graphs of order n
(nauty-geng -c). Conjecture predicts score >= 1 everywhere. Also serves as an
independent verifier of the V3 pipeline against the known exhaustive frontier.

Usage: pypy3 exhaustive.py <n> [res/mod]
"""
import subprocess
import sys
import time

from lp_core import analyze, edges_to_adj
from families import graph6_to_edges


def main():
    n = int(sys.argv[1])
    extra = [sys.argv[2]] if len(sys.argv) > 2 else []
    proc = subprocess.Popen(["nauty-geng", "-q", "-c", str(n)] + extra,
                            stdout=subprocess.PIPE, text=True)
    t0 = time.time()
    cnt = 0
    best = 99
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        cnt += 1
        nn, edges = graph6_to_edges(g6)
        adj = edges_to_adj(nn, edges)
        res = analyze(nn, adj, cap=3000)
        sc = res["score"]
        if sc < best:
            best = sc
        if sc == 0:
            print("WITNESS!!! g6=%s edges=%s triple=%s" % (g6, edges, res["witness"]))
            with open("WITNESS_exh_%d.txt" % n, "w") as f:
                f.write("g6=%s edges=%s triple=%s\n" % (g6, edges, res["witness"]))
            return
        if cnt % 20000 == 0:
            print("n=%d cnt=%d best=%d elapsed=%.0fs" % (n, cnt, best, time.time() - t0))
            sys.stdout.flush()
    print("DONE n=%d graphs=%d best=%d elapsed=%.0fs" % (n, cnt, best, time.time() - t0))


if __name__ == "__main__":
    main()

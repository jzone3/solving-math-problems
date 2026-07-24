"""Resolve HARD instances deferred by biregk.c's node-limited backtracker:
re-check each with the independent fastcuts enumerator + CaDiCaL."""
import os
import sys
import time
from fastcuts import min_dicuts
from pysat.solvers import Cadical153


def check(K, p, flat):
    q = len(flat) // K
    sinks = [flat[K * t:K * t + K] for t in range(q)]
    arcs = [(s, p + t) for t, tri in enumerate(sinks) for s in tri]
    cuts, tau = min_dicuts(p + q, arcs)
    if cuts is None or tau != K:
        return "degenerate"
    var = lambda a, c: a * K + c + 1
    cl = []
    for a in range(len(arcs)):
        cl.append([var(a, c) for c in range(K)])
        for c1 in range(K):
            for c2 in range(c1 + 1, K):
                cl.append([-var(a, c1), -var(a, c2)])
    for cut in cuts:
        for c in range(K):
            cl.append([var(a, c) for a in cut])
    s = Cadical153(bootstrap_with=cl)
    if s.solve():
        return "packs"
    print("UNSAT COUNTEREXAMPLE", K, p, sinks, flush=True)
    with open("counterexample.txt", "a") as f:
        f.write("HARDRESOLVE K=%d p=%d %r\n" % (K, p, sinks))
    return "UNSAT"


def main(seconds):
    t0 = time.time()
    done = 0
    while time.time() - t0 < seconds:
        lines = []
        if os.path.exists("hardk.txt"):
            lines = open("hardk.txt").read().strip().split("\n")
        while done < len(lines) and lines[done]:
            parts = lines[done].split()
            K = int(parts[1].split("=")[1])
            p = int(parts[2].split("=")[1])
            flat = [int(x) for x in parts[3:]]
            r = check(K, p, flat)
            done += 1
            print(f"[resolve] #{done}: {r}", flush=True)
        time.sleep(30)
    print(f"[resolve] DONE resolved={done}", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 11400)

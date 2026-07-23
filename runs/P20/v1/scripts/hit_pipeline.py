#!/usr/bin/env python3
"""Watch sms/ for HIT5_*.adjlist files; for each new one: verify (5-regular,
girth>=6, non-3-colorable), compute affine automorphisms, run cover-CEGAR
(matching_cegar3). One CEGAR at a time. Log results."""
import glob, json, math, os, subprocess, time
import networkx as nx

DIR = "/home/ubuntu/p20/sms"
done = set()

def affine_auts(G, n):
    E = set(tuple(sorted(e)) for e in G.edges())
    perms = []
    for a in range(1, n):
        if math.gcd(a, n) != 1: continue
        for b in range(n):
            p = [(a*v+b) % n for v in range(n)]
            if all(tuple(sorted((p[u], p[w]))) in E for u, w in E):
                perms.append(p)
    return perms

while True:
    for f in sorted(glob.glob(DIR + "/HIT5_*.adjlist")):
        if f in done: continue
        done.add(f)
        G = nx.read_adjlist(f, nodetype=int)
        n = G.number_of_nodes()
        auts = affine_auts(G, n)
        json.dump(auts, open(f.replace(".adjlist", ".auts.json"), "w"))
        log = f.replace(".adjlist", ".cegar.log")
        print(f"CEGAR start {f} n={n} |auts|={len(auts)}", flush=True)
        with open(log, "w") as lf:
            subprocess.run(["python3", "/home/ubuntu/p20/matching_cegar3.py", f, "cover"],
                           stdout=lf, stderr=lf)
        tail = open(log).read().strip().split("\n")[-1]
        print(f"CEGAR done {f}: {tail}", flush=True)
    time.sleep(30)

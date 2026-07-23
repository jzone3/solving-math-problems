"""Exhaustive dense-band verification of Hajos' conjecture.

Theorem target: "Every simple connected Eulerian graph G on n vertices with
complement having at most E_n edges satisfies Hajos' conjecture."

Method: enumerate ALL defect graphs H on n labeled vertices (up to iso, geng)
with <= E edges and the parity condition making G = K_n - H Eulerian
(odd n: all degrees of H even; even n: all degrees odd, hence min degree 1),
then SAT-decide "G decomposes into <= floor((n-1)/2) cycles" for each.
UNSAT => counterexample. Sharding via geng's res/mod feature.

Usage: exhaustive_band.py n maxE res mod [minE]
Enumeration is piped through the compiled C parity filter (parity_filter.c,
validated against the Python check) for speed.
"""

import os

import subprocess
import sys
import time

import networkx as nx

from sat_decider import decompose_le_k


def parity_ok_g6(line, n, want_odd):
    """Fast degree-parity check straight from graph6 bytes."""
    data = line.strip()
    assert 0 < n <= 62
    bits = []
    for ch in data[1:]:
        b = ch - 63
        bits.extend(((b >> 5) & 1, (b >> 4) & 1, (b >> 3) & 1,
                     (b >> 2) & 1, (b >> 1) & 1, b & 1))
    deg = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                deg[i] ^= 1
                deg[j] ^= 1
            idx += 1
    if want_odd:
        return all(d == 1 for d in deg)
    return all(d == 0 for d in deg)


def main():
    n, maxE, res, mod = map(int, sys.argv[1:5])
    want_odd = (n % 2 == 0)
    k = (n - 1) // 2
    minE = int(sys.argv[5]) if len(sys.argv) > 5 else (n // 2 if want_odd else 0)
    cmd = ["nauty-geng", "-q", str(n), f"{minE}:{maxE}"]
    if want_odd:
        cmd.insert(2, "-d1")
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    here = os.path.dirname(os.path.abspath(__file__))
    cmd = " ".join(cmd) + f" | {here}/parity_filter {n} {1 if want_odd else 0}"
    log = f"band_n{n}_E{minE}-{maxE}_s{res}.log"
    Kn = nx.complete_graph(n)
    t0 = time.time()
    seen = cand = 0
    stats = {"OK": 0, "CE": 0}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    for line in proc.stdout:
        seen += 1
        H = nx.from_graph6_bytes(line.strip())
        Hf = nx.Graph()
        Hf.add_nodes_from(range(n))
        Hf.add_edges_from(H.edges())
        G = nx.difference(Kn, Hf)
        if not nx.is_connected(G):
            continue
        cand += 1
        sat, _ = decompose_le_k(n, list(G.edges()), k)
        if not sat:
            g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
            print(f"*** COUNTEREXAMPLE *** n={n} g6={g6}", flush=True)
            with open(log, "a") as f:
                f.write(f"COUNTEREXAMPLE n={n} g6={g6}\n")
            stats["CE"] += 1
        else:
            stats["OK"] += 1
        if cand % 500 == 0:
            print(f"[seen={seen} cand={cand}] {stats} {time.time()-t0:.0f}s",
                  flush=True)
    proc.wait()
    msg = (f"DONE band n={n} maxE={maxE} shard={res}/{mod} seen={seen} "
           f"cand={cand} {stats} time={time.time()-t0:.0f}s")
    print(msg, flush=True)
    with open(log, "a") as f:
        f.write(msg + "\n")


if __name__ == "__main__":
    main()

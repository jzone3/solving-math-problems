"""Probe 3f: EXHAUSTIVE sweep of all connected 6-regular graphs on n vertices
(nauty-geng stream). n=13: 367,860 graphs. Every graph is Eulerian; check the
Hajos bound with a fast greedy first, CP-SAT on survivors.

A clean negative here is a frontier statement: 'no 6-regular counterexample on
n vertices exists', complementing HNS's full n<=12 verification.
Usage: python3 sweep_regular.py <n> [<res> <mod>]   (geng res/mod splitting)
"""
import subprocess
import sys
import time
from hajos import check_decomposition, hajos_ok, is_eulerian, rlc_decompose

def g6_to_edges(g6):
    data = [c - 63 for c in g6.encode()]
    n = data[0]
    assert n < 63
    bits = []
    for c in data[1:]:
        bits += [(c >> i) & 1 for i in range(5, -1, -1)]
    edges = []
    idx = 0
    for v in range(1, n):
        for u in range(v):
            if bits[idx]:
                edges.append((u, v))
            idx += 1
    return n, tuple(edges)

def main():
    n = int(sys.argv[1])
    resmod = sys.argv[2:4]
    cmd = ["nauty-geng", "-c", "-d6", "-D6", str(n)]
    if resmod:
        cmd.append(f"{resmod[0]}/{resmod[1]}")
    bound = (n - 1) // 2
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    t0 = time.time()
    cnt = hard = 0
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        cnt += 1
        nn, edges = g6_to_edges(g6)
        h = rlc_decompose(nn, edges, tries=120)
        if h is not None and len(h) <= bound:
            check_decomposition(nn, edges, h)  # trust nothing: validate greedy output
            if cnt % 20000 == 0:
                print(f"[{cnt}] t={int(time.time()-t0)}s hard-so-far={hard}", flush=True)
            continue
        hard += 1
        ok, _ = hajos_ok(nn, edges, time_limit=1200, workers=4)
        print(f"HARD #{cnt} {g6}: cpSAT={ok}", flush=True)
        if ok is False:
            print(f"*** COUNTEREXAMPLE g6={g6} edges={edges}", flush=True)
            with open(f"counterexample_6reg_n{n}.txt", "w") as f:
                f.write(repr((nn, edges)))
    print(f"DONE n={n} resmod={resmod}: {cnt} graphs, {hard} escalated, "
          f"t={int(time.time()-t0)}s", flush=True)

if __name__ == "__main__":
    main()

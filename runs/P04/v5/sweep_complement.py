"""Probe 8: COMPLEMENT-BASED exhaustion of dense Eulerian graphs.

A graph on odd n with even degrees has an even-degree complement. Dense layers
(degrees {8,10} at n=13, 8-regular n=14, etc.) are unreachable by direct geng,
but their complements are sparse: degree d graph <-> degree (n-1-d) complement.
So enumerate ALL graphs with complement-degree bounds via geng (no -c: the
complement of a disconnected sparse graph can still be a connected dense
Eulerian graph -- we must not require connectivity on the sparse side), take
complements, keep those that are connected + all-even-degree + min degree >= 6,
and check the Hajos bound (greedy first, CP-SAT on survivors).

Usage: python3 sweep_complement.py <n> <dlo> <dhi> [<res> <mod>]
       (dlo/dhi are degree bounds on the SPARSE side, i.e. complement side)
"""
import subprocess
import sys
import time
from hajos import check_decomposition, hajos_ok, rlc_decompose
from sweep_regular import g6_to_edges

def main():
    n = int(sys.argv[1])
    dlo, dhi = sys.argv[2], sys.argv[3]
    resmod = sys.argv[4:6]
    cmd = ["nauty-geng", "-q", f"-d{dlo}", f"-D{dhi}", str(n)]
    if resmod:
        cmd.append(f"{resmod[0]}/{resmod[1]}")
    bound = (n - 1) // 2
    allpairs = {(u, v) for v in range(1, n) for u in range(v)}
    gen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc = subprocess.Popen(["./evenfilt"], stdin=gen.stdout, stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    gen.stdout.close()
    t0 = time.time()
    cnt = kept = hard = 0
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        cnt += 1
        nn, sparse = g6_to_edges(g6)
        deg = [0] * nn
        for u, v in sparse:
            deg[u] += 1
            deg[v] += 1
        edges = tuple(sorted(allpairs - set(sparse)))
        cdeg = [nn - 1 - d for d in deg]
        if min(cdeg) < 6:
            continue
        # connectivity of complement
        adj = [[] for _ in range(nn)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        seen = {0}
        stack = [0]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(seen) != nn:
            continue
        kept += 1
        h = rlc_decompose(nn, edges, tries=120)
        if h is not None and len(h) <= bound:
            check_decomposition(nn, edges, h)
            if kept % 20000 == 0:
                print(f"[gen {cnt} kept {kept}] t={int(time.time()-t0)}s hard={hard}",
                      flush=True)
            continue
        hard += 1
        ok, _ = hajos_ok(nn, edges, time_limit=1200, workers=4)
        print(f"HARD #{kept} complement-of {g6}: cpSAT={ok}", flush=True)
        if ok is False:
            print(f"*** COUNTEREXAMPLE complement-of g6={g6} edges={edges}", flush=True)
            with open(f"counterexample_comp_n{n}.txt", "w") as f:
                f.write(repr((nn, edges)))
    print(f"DONE n={n} d=[{dlo},{dhi}] resmod={resmod}: parity-ok {cnt}, "
          f"kept {kept}, {hard} escalated, t={int(time.time()-t0)}s", flush=True)

if __name__ == "__main__":
    main()

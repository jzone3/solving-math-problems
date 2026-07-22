"""Convert nearly cubic 1H seeds (nc_*.txt) to HC-normal form (C_n + chords)
and run the seeded completion DFS (dfs4 seed mode) on each.

Usage: python3 seed_driver.py nc_22.txt <budget_per_seed_s> [maxnodes]
"""
import subprocess, sys, itertools
from hcutil import hc_count

def find_hc(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    path = [0]
    used = [False] * n
    used[0] = True
    def ext():
        u = path[-1]
        if len(path) == n:
            return 0 in adj[u]
        for w in adj[u]:
            if not used[w]:
                used[w] = True; path.append(w)
                if ext():
                    return True
                path.pop(); used[w] = False
        return False
    assert ext()
    return path

def normalize(edges):
    n = max(max(e) for e in edges) + 1
    assert hc_count(n, list(edges)) == 1
    hc = find_hc(n, edges)
    lab = {v: i for i, v in enumerate(hc)}
    cyc = set()
    for i in range(n):
        a, b = lab[hc[i]], lab[hc[(i + 1) % n]]
        cyc.add((min(a, b), max(a, b)))
    chords = []
    for u, v in edges:
        e = (min(lab[u], lab[v]), max(lab[u], lab[v]))
        if e not in cyc:
            chords.append(e)
    return n, chords

if __name__ == "__main__":
    fname = sys.argv[1]
    budget = sys.argv[2]
    maxnodes = sys.argv[3] if len(sys.argv) > 3 else "999999999999"
    for gi, line in enumerate(l for l in open(fname) if l.strip()):
        edges = eval(line)
        n, chords = normalize(edges)
        inp = f"{len(chords)}\n" + "\n".join(f"{u} {v}" for u, v in chords)
        print(f"=== seed {fname} g{gi}: n={n} chords={len(chords)} ===", flush=True)
        r = subprocess.run(["./dfs4", str(n), str(1000 + gi), budget, maxnodes, "seed"],
                           input=inp, capture_output=True, text=True)
        print(r.stdout, flush=True)
        if r.returncode == 42:
            print("WITNESS from seed", gi)
            break

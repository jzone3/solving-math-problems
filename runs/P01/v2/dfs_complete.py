"""V2 attack 3 (main): DFS completion to 4-regular while preserving unique
hamiltonicity.

Start from a uniquely hamiltonian seed graph (nearly cubic 1H seed, or the bare
cycle C_n). Repeatedly add an edge between two degree-deficient (<4) vertices
such that the HC count REMAINS exactly 1 (checked exactly with cutoff 2 -- an
edge (u,v) is addable iff the current graph has no hamiltonian u-v path).
If all vertices reach degree 4 => 4-regular uniquely hamiltonian graph =>
counterexample to Sheehan. DFS with randomized ordering + restarts; logs the
best depth (fewest deficient vertices remaining) as near-miss metric.

Usage: python3 dfs_complete.py cycle <n> <seed> [time_budget_s]
       python3 dfs_complete.py file <nc_file> <seed> [time_budget_s]
"""
import random, sys, time
from hcutil import hc_count

def run_dfs(n, edges, rng, budget, tag):
    edges = list(edges)
    eset = set(edges)
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    assert hc_count(n, edges) == 1, "seed not uniquely hamiltonian"
    t0 = time.time()
    best = [sum(4 - d for d in deg)]

    def deficient():
        return [v for v in range(n) if deg[v] < 4]

    def dfs():
        if time.time() - t0 > budget:
            return False
        defs = deficient()
        rem = sum(4 - deg[v] for v in defs)
        if rem < best[0]:
            best[0] = rem
            print(f"[{tag}] depth: {rem} stubs remaining, t={time.time()-t0:.0f}s", flush=True)
            if rem <= 4:
                with open("dfs_nearmiss.txt", "a") as f:
                    f.write(f"{tag} rem={rem} n={n} edges={sorted(edges)}\n")
        if not defs:
            with open("WITNESS.txt", "a") as f:
                f.write(f"DFS-COMPLETE n={n} edges={sorted(edges)}\n")
            print("!!! WITNESS FOUND !!!", flush=True)
            return True
        cands = []
        u = min(defs, key=lambda v: (deg[v], rng.random()))  # fill lowest-degree vertex first
        for v in defs:
            if v == u or (min(u, v), max(u, v)) in eset:
                continue
            cands.append(v)
        rng.shuffle(cands)
        for v in cands:
            e = (min(u, v), max(u, v))
            edges.append(e); eset.add(e); deg[u] += 1; deg[v] += 1
            if hc_count(n, edges, cutoff=2) == 1:
                if dfs():
                    return True
            edges.pop(); eset.discard(e); deg[u] -= 1; deg[v] -= 1
            if time.time() - t0 > budget:
                return False
        return False

    found = dfs()
    print(f"[{tag}] done: found={found}, best remaining stubs={best[0]}, "
          f"t={time.time()-t0:.0f}s", flush=True)
    return found, best[0]

if __name__ == "__main__":
    mode = sys.argv[1]
    seed = int(sys.argv[3])
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 600
    rng = random.Random(seed)
    if mode == "cycle":
        n = int(sys.argv[2])
        edges = [(i, (i + 1) % n) for i in range(n)]
        edges = [(min(e), max(e)) for e in edges]
        run_dfs(n, edges, rng, budget, f"C{n}-s{seed}")
    else:
        fname = sys.argv[2]
        for gi, edges in enumerate([eval(l) for l in open(fname) if l.strip()]):
            n = max(max(e) for e in edges) + 1
            run_dfs(n, edges, rng, budget, f"{fname}-g{gi}-s{seed}")

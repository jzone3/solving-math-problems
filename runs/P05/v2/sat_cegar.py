#!/usr/bin/env python3
"""P05 V2: SAT+CEGAR search for a counterexample to Gallai's 3 longest paths question
at fixed (n, L): a connected graph on n vertices, longest path length exactly L (edges),
containing three longest paths with empty common vertex intersection.

Key WLOG reductions (proved in NOTES.md):
  R1. Every vertex lies on >=1 of the three paths (else delete it; witness survives).
  R2. Every edge lies on >=1 of the three paths (else delete it; witness survives).
      => the graph is exactly the union of the three paths.
  R3. Connectivity is then automatic (paths pairwise intersect by the 2-path theorem;
      here it is forced implicitly: if the union were disconnected, some pair of the
      three length-L paths would be disjoint, giving a path... we do NOT rely on this;
      the CEGAR oracle checks the candidate and rejects disconnected candidates).
  R4. WLOG path 0 = (0, 1, ..., L) (relabeling).
  R5. Each path oriented with first endpoint < last endpoint; path1 first vtx <= path2 first vtx.

"No path longer than L" handled by CEGAR: exact bitmask-DP longest path oracle (longpath.c);
if a longer path exists, block a length-(L+1) subpath via clause OR(!e) over its edges.
Final UNSAT at (n, L) = complete refutation for that size (given R1/R2 minimality).

Usage: sat_cegar.py n L [--max-iters K] [--time-limit sec]
Exit prints: RESULT n=<n> L=<L> status=<UNSAT|COUNTEREXAMPLE|TIMEOUT> iters=<k> time=<s>
On COUNTEREXAMPLE writes witness JSON to witness_n<L>_L<L>.json.
"""
import sys, os, time, json, subprocess, itertools, argparse
from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))
LONGPATH = os.path.join(HERE, "longpath")


def ensure_oracle():
    if not os.path.exists(LONGPATH):
        subprocess.check_call(["gcc", "-O2", "-o", LONGPATH, os.path.join(HERE, "longpath.c")])


def longest_path(n, edges):
    inp = f"{n} {len(edges)}\n" + "\n".join(f"{u} {v}" for u, v in edges) + "\n"
    out = subprocess.run([LONGPATH], input=inp, capture_output=True, text=True, check=True).stdout.split("\n")
    length = int(out[0])
    path = [int(x) for x in out[1].split()]
    return length, path


def all_paths_of_length(n, edges, k, cap=200000):
    """Yield edge-tuples of all simple paths with exactly k edges in sparse graph."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    out = []
    def dfs(v, visited, path):
        if len(out) >= cap:
            return
        if len(path) == k:
            out.append(tuple(path))
            return
        for w in adj[v]:
            if not (visited >> w) & 1:
                path.append((v, w) if v < w else (w, v))
                dfs(w, visited | (1 << w), path)
                path.pop()
    for s in range(n):
        dfs(s, 1 << s, [])
    # dedup reversed duplicates
    seen = set()
    res = []
    for p in out:
        key = frozenset(p)
        if key not in seen:
            seen.add(key)
            res.append(p)
    return res


def connected(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    seen = {0}; stack = [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return len(seen) == n


class Enc:
    def __init__(self):
        self.top = 0
        self.emap = {}

    def new(self):
        self.top += 1
        return self.top

    def evar(self, u, v):
        if u > v: u, v = v, u
        if (u, v) not in self.emap:
            self.emap[(u, v)] = self.new()
        return self.emap[(u, v)]


def build(n, L, solver):
    enc = Enc()
    P = 3
    # x[p][t][v]
    x = [[[enc.new() for _ in range(n)] for _ in range(L + 1)] for _ in range(P)]
    # membership in[p][v]
    inn = [[enc.new() for _ in range(n)] for _ in range(P)]
    cls = []
    # edge vars (create all up front for determinism)
    for u in range(n):
        for v in range(u + 1, n):
            enc.evar(u, v)

    for p in range(P):
        for t in range(L + 1):
            # exactly one vertex at position t
            cls.append([x[p][t][v] for v in range(n)])
            for v in range(n):
                for w in range(v + 1, n):
                    cls.append([-x[p][t][v], -x[p][t][w]])
        # each vertex at most once per path
        for v in range(n):
            for t in range(L + 1):
                for s in range(t + 1, L + 1):
                    cls.append([-x[p][t][v], -x[p][s][v]])
        # adjacency
        for t in range(L):
            for u in range(n):
                for v in range(n):
                    if u != v:
                        cls.append([-x[p][t][u], -x[p][t + 1][v], enc.evar(u, v)])
        # membership definition in[p][v] <-> OR_t x[p][t][v]
        for v in range(n):
            cls.append([-inn[p][v]] + [x[p][t][v] for t in range(L + 1)])
            for t in range(L + 1):
                cls.append([inn[p][v], -x[p][t][v]])

    # empty common intersection + R1 coverage
    for v in range(n):
        cls.append([-inn[0][v], -inn[1][v], -inn[2][v]])
        cls.append([inn[0][v], inn[1][v], inn[2][v]])

    # R4: fix path 0 = 0..L
    for t in range(L + 1):
        cls.append([x[0][t][t]])

    # R5: orientation first<last for paths 1,2
    for p in (1, 2):
        for v in range(n):
            for w in range(v, n):  # forbid first=v >= last=w
                cls.append([-x[p][0][v], -x[p][L][w]])
    # R5: first vertex of p1 <= first vertex of p2
    for v in range(n):
        for w in range(v):
            cls.append([-x[1][0][v], -x[2][0][w]])

    # R2: every true edge is used by some path consecutively
    # aux y -> x[p][t][u] & x[p][t+1][v]
    for (u, v), ev in list(enc.emap.items()):
        ors = [-ev]
        for p in range(P):
            for t in range(L):
                for (a, b) in ((u, v), (v, u)):
                    y = enc.new()
                    cls.append([-y, x[p][t][a]])
                    cls.append([-y, x[p][t + 1][b]])
                    ors.append(y)
        cls.append(ors)

    for c in cls:
        solver.add_clause(c)
    return enc, x


def run(n, L, max_iters, time_limit, log):
    ensure_oracle()
    t0 = time.time()
    solver = Cadical153()
    enc, x = build(n, L, solver)
    it = 0
    status = "TIMEOUT"
    witness = None
    blocked = set()
    nclauses = 0
    while True:
        if time.time() - t0 > time_limit:
            status = "TIMEOUT"; break
        if it >= max_iters:
            status = "MAXITERS"; break
        if not solver.solve():
            status = "UNSAT"; break
        it += 1
        model = set(l for l in solver.get_model() if l > 0)
        edges = [(u, v) for (u, v), ev in enc.emap.items() if ev in model]
        if not connected(n, edges):
            # block this exact edge-set's "missing connectivity": simplest sound cut —
            # require an edge across the split (candidate rejected; add cut clause)
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v); adj[v].append(u)
            seen = {0}; stack = [0]
            while stack:
                u = stack.pop()
                for w in adj[u]:
                    if w not in seen:
                        seen.add(w); stack.append(w)
            cut = [enc.evar(u, v) for u in seen for v in range(n) if v not in seen]
            solver.add_clause(cut)
            continue
        length, path = longest_path(n, edges)
        if length <= L:
            assert length == L
            paths = []
            for p in range(3):
                pv = []
                for t in range(L + 1):
                    for v in range(n):
                        if x[p][t][v] in model:
                            pv.append(v); break
                paths.append(pv)
            witness = {"n": n, "L": L, "edges": sorted(edges), "paths": paths}
            status = "COUNTEREXAMPLE"; break
        # block ALL length-(L+1) paths present in this candidate graph
        added = 0
        for pe in all_paths_of_length(n, edges, L + 1):
            key = frozenset(pe)
            if key in blocked:
                continue
            blocked.add(key)
            solver.add_clause([-enc.evar(u, v) for (u, v) in pe])
            added += 1
        nclauses += added
        if added == 0:
            # safety: fall back to blocking a truncation of the returned longest path
            sub = path[: L + 2]
            solver.add_clause([-enc.evar(sub[i], sub[i + 1]) for i in range(L + 1)])
            nclauses += 1
    dt = time.time() - t0
    line = f"RESULT n={n} L={L} status={status} iters={it} blockclauses={nclauses} time={dt:.1f}s"
    print(line, flush=True)
    with open(log, "a") as f:
        f.write(line + "\n")
    if witness:
        wf = os.path.join(HERE, f"witness_n{n}_L{L}.json")
        with open(wf, "w") as f:
            json.dump(witness, f, indent=1)
        print("witness written to", wf)
    solver.delete()
    return status


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("L", type=int)
    ap.add_argument("--max-iters", type=int, default=10**9)
    ap.add_argument("--time-limit", type=float, default=3600)
    ap.add_argument("--log", default=os.path.join(HERE, "results.log"))
    a = ap.parse_args()
    run(a.n, a.L, a.max_iters, a.time_limit, a.log)

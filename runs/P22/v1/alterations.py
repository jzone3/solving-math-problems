"""Step 2: K4-destroying alterations of H_3 (paper's Appendix A experiments 1-5),
each candidate tested for G -> (3,3)^e via SAT. UNSAT => Folkman graph on <=63 vertices.

Each candidate must be K4-free (checked exactly) before the SAT test.
SAT results are verified independently (coloring witness re-checked in python).
"""
import random, sys, json, os
from itertools import combinations
from h3 import adj, edges as h3_edges, maximal_cliques_C, nondegenerate_triangles
from arrow import triangles_of, cnf_for_arrowing, solve, has_k4, count_k4, verify_coloring

N = 63
H3_ADJ = [set(j for j in range(N) if adj[i][j]) for i in range(N)]
CLIQUES = [set(v) for v in maximal_cliques_C().values()]  # 28 cliques of size 9
NDT = nondegenerate_triangles()

def edge_set(adjset):
    return sorted((i, j) for i in range(N) for j in adjset[i] if i < j)

def test_candidate(adjset, tag, log):
    """Returns 'FOLKMAN' if UNSAT, else records stats."""
    k4 = has_k4(N, adjset)
    if k4:
        log.append({"tag": tag, "result": "not-K4-free", "k4": k4})
        return None
    es = edge_set(adjset)
    tris = triangles_of(N, adjset)
    if not tris:
        log.append({"tag": tag, "result": "no-triangles"})
        return None
    var, clauses = cnf_for_arrowing(es, tris)
    status, model, cnf = solve(len(var), clauses)
    if status == "UNSAT":
        log.append({"tag": tag, "result": "UNSAT-FOLKMAN", "edges": len(es), "tris": len(tris)})
        return ("FOLKMAN", es, tris)
    assert status == "SAT"
    bad = verify_coloring(es, tris, var, model)
    assert bad is None, f"SAT model failed independent verification: {bad}"
    log.append({"tag": tag, "result": "SAT", "edges": len(es), "tris": len(tris)})
    return None

# ---------- Experiment 1: replace each maximal clique with complete bipartite graph ----------
def exp1(rng):
    adjset = [set(s) for s in H3_ADJ]
    for cl in CLIQUES:
        cl = list(cl)
        # remove all internal edges
        for a, b in combinations(cl, 2):
            adjset[a].discard(b); adjset[b].discard(a)
    for cl in CLIQUES:
        cl = list(cl)
        rng.shuffle(cl)
        A, B = cl[:4], cl[4:]  # K_{4,5} on 9 vertices
        for a in A:
            for b in B:
                adjset[a].add(b); adjset[b].add(a)
    return adjset

# ---------- Experiment 2: replace each clique with random maximal triangle-free graph ----------
def random_maximal_triangle_free(verts, rng):
    verts = list(verts)
    pairs = list(combinations(verts, 2))
    rng.shuffle(pairs)
    adj_l = {v: set() for v in verts}
    for a, b in pairs:
        # add edge iff it creates no triangle
        if not (adj_l[a] & adj_l[b]):
            adj_l[a].add(b); adj_l[b].add(a)
    return [(a, b) for a in verts for b in adj_l[a] if a < b]

def exp2(rng):
    adjset = [set(s) for s in H3_ADJ]
    for cl in CLIQUES:
        for a, b in combinations(sorted(cl), 2):
            adjset[a].discard(b); adjset[b].discard(a)
    for cl in CLIQUES:
        for a, b in random_maximal_triangle_free(cl, rng):
            adjset[a].add(b); adjset[b].add(a)
    return adjset

# ---------- Experiment 3: remove random edges until K4-free ----------
def exp3(rng):
    adjset = [set(s) for s in H3_ADJ]
    while True:
        k4 = has_k4(N, adjset)
        if not k4:
            return adjset
        # remove a random edge of this K4 (random edge overall is slower; edge of a K4 is equivalent in effect)
        a, b = rng.sample(list(k4), 2)
        adjset[a].discard(b); adjset[b].discard(a)

# ---------- Experiment 4: greedily remove edge in most K4s ----------
def exp4(rng):
    adjset = [set(s) for s in H3_ADJ]
    while True:
        # count K4s per edge
        cnt = {}
        for i in range(N):
            ni = sorted(x for x in adjset[i] if x > i)
            for a in range(len(ni)):
                j = ni[a]
                common = [x for x in ni[a+1:] if x in adjset[j]]
                for b in range(len(common)):
                    k = common[b]
                    for l in common[b+1:]:
                        if l in adjset[k]:
                            for e in combinations(sorted((i, j, k, l)), 2):
                                cnt[e] = cnt.get(e, 0) + 1
        if not cnt:
            return adjset
        mx = max(cnt.values())
        e = rng.choice([e for e, c in cnt.items() if c == mx])
        a, b = e
        adjset[a].discard(b); adjset[b].discard(a)

# ---------- Experiment 5: build up from random non-degenerate triangles, stay K4-free ----------
def edge_in_k4(adjset, a, b):
    common = adjset[a] & adjset[b]
    for u, v in combinations(sorted(common), 2):
        if v in adjset[u]:
            return True
    return False

def exp5(rng):
    adjset = [set() for _ in range(N)]
    order = NDT[:]
    rng.shuffle(order)
    for (i, j, k) in order:
        new = [(a, b) for a, b in ((i, j), (i, k), (j, k)) if b not in adjset[a]]
        for a, b in new:
            adjset[a].add(b); adjset[b].add(a)
        if any(edge_in_k4(adjset, a, b) for a, b in ((i, j), (i, k), (j, k))):
            for a, b in new:
                adjset[a].discard(b); adjset[b].discard(a)
    return adjset

EXPS = {"exp1": exp1, "exp2": exp2, "exp3": exp3, "exp4": exp4, "exp5": exp5}

def main():
    which = sys.argv[1]
    iters = int(sys.argv[2])
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    log = []
    fn = EXPS[which]
    found = None
    for t in range(iters):
        rng = random.Random(seed0 * 1000003 + t)
        adjset = fn(rng)
        res = test_candidate(adjset, f"{which}-{t}", log)
        if res:
            found = res
            with open(f"out/FOLKMAN_{which}_{t}.json", "w") as f:
                json.dump({"edges": res[1]}, f)
            print("!!! FOLKMAN FOUND", which, t)
            break
    os.makedirs("out", exist_ok=True)
    with open(f"out/log_{which}_{seed0}.json", "w") as f:
        json.dump(log, f)
    sat = sum(1 for l in log if l["result"] == "SAT")
    notk4 = sum(1 for l in log if l["result"] == "not-K4-free")
    print(f"{which}: {len(log)} candidates, SAT(colorable)={sat}, not-K4-free={notk4}, folkman={'YES' if found else 'no'}")

if __name__ == "__main__":
    main()

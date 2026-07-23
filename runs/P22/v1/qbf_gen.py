"""Generate a 2QBF (QDIMACS) instance for Problem 5.1:
EXISTS edge-selection s (+ triangle vars t), FORALL edge-colors x, EXISTS aux (m,a):
   K4free(s) AND t_T <-> edges(T) kept AND OR_T m_T,
   with m_T -> t_T and m_T -> allsame(x on T).
TRUE  => a K4-free subgraph of H_3 arrows (3,3)^e (Folkman graph, Graham prize).
FALSE => no K4-free subgraph of H_3 arrows => Problem 5.1 answered NO.

WLOG maximality constraints (sound, see cegar_max.py) are included to shrink
the existential search space.
"""
from itertools import combinations
from h3 import adj, edges as h3_edges

N = 63
ADJ = [set(j for j in range(N) if adj[i][j]) for i in range(N)]
EDGES = sorted((min(i, j), max(i, j)) for i, j in h3_edges)

TRIS = []
for i in range(N):
    for j in sorted(x for x in ADJ[i] if x > i):
        for k in sorted(x for x in ADJ[i] & ADJ[j] if x > j):
            TRIS.append((i, j, k))
K4S = []
for i in range(N):
    ni = sorted(x for x in ADJ[i] if x > i)
    for a, j in enumerate(ni):
        common = [x for x in ni[a+1:] if x in ADJ[j]]
        for b, k in enumerate(common):
            for l in common[b+1:]:
                if l in ADJ[k]:
                    K4S.append((i, j, k, l))

nv = 0
def new():
    global nv
    nv += 1
    return nv

S = {e: new() for e in EDGES}                     # exists level 1
T = {t: new() for t in TRIS}                      # exists level 1
Y = {}                                            # maximality aux, exists level 1
k4s_of_edge = {e: [] for e in EDGES}
for Q in K4S:
    for e in combinations(Q, 2):
        k4s_of_edge[e].append(Q)
for e in EDGES:
    for Q in k4s_of_edge[e]:
        Y[(Q, e)] = new()
X = {e: new() for e in EDGES}                     # forall level 2
M = {t: new() for t in TRIS}                      # exists level 3
A = {t: new() for t in TRIS}                      # exists level 3 (allsame)

clauses = []
tri_edges = {t: [(t[0], t[1]), (t[0], t[2]), (t[1], t[2])] for t in TRIS}

# K4-freeness
for Q in K4S:
    clauses.append([-S[e] for e in combinations(Q, 2)])
# t <-> edges
for t in TRIS:
    evs = [S[e] for e in tri_edges[t]]
    for ev in evs:
        clauses.append([-T[t], ev])
    clauses.append([T[t]] + [-ev for ev in evs])
# maximality: ~s_e -> OR_Q y_{Q,e};  y <-> other-5 kept
for e in EDGES:
    ors = []
    for Q in k4s_of_edge[e]:
        y = Y[(Q, e)]
        others = [S[f] for f in combinations(Q, 2) if f != e]
        for ov in others:
            clauses.append([-y, ov])
        clauses.append([y] + [-ov for ov in others])
        ors.append(y)
    clauses.append([S[e]] + ors)
# m_T -> t_T, m_T -> allsame via a_T
for t in TRIS:
    x1, x2, x3 = [X[e] for e in tri_edges[t]]
    clauses.append([-M[t], T[t]])
    clauses.append([-M[t], A[t]])
    clauses.append([-A[t], x1, -x2])
    clauses.append([-A[t], -x1, x2])
    clauses.append([-A[t], x2, -x3])
    clauses.append([-A[t], -x2, x3])
# some mono kept triangle
clauses.append([M[t] for t in TRIS])

with open("out/p51.qdimacs", "w") as f:
    f.write(f"p cnf {nv} {len(clauses)}\n")
    lvl1 = list(S.values()) + list(T.values()) + list(Y.values())
    f.write("e " + " ".join(map(str, lvl1)) + " 0\n")
    f.write("a " + " ".join(map(str, X.values())) + " 0\n")
    lvl3 = list(M.values()) + list(A.values())
    f.write("e " + " ".join(map(str, lvl3)) + " 0\n")
    for c in clauses:
        f.write(" ".join(map(str, c)) + " 0\n")
print("vars", nv, "clauses", len(clauses))

"""childG exploration 3: leaf-completion route.

For each connected leafy G (n <= NMAX): does there EXIST a set F of new edges,
each incident to at least one leaf, covering all leaves, such that G+F has
min degree >= 2 and RHS46(G+F) <= RHS46(G)?

If yes always, then Hyp D (Bound 46 for delta>=2) + mu monotone under edge
addition gives Bound 46 for G.  Records which completions work.

Enumeration: each leaf picks a partner vertex (any vertex != itself, != its
support... actually any non-neighbor, i.e. anything but its unique neighbor);
F = union of chosen edges (dedup).  If #leaves > CAP, random-sample partners.
Usage: explore3.py NMAX
"""
import numpy as np, subprocess, sys, math, itertools, random
from explore1 import graphs, g6_adj, t46, data

def rhs46_A(A):
    d = A.sum(1); m = A @ d / d
    n = A.shape[0]
    best = -math.inf
    for i in range(n):
        for j in range(i+1, n):
            if A[i, j]:
                v = t46(d[i], d[j], m[i], m[j])
                if v > best: best = v
    return best

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    random.seed(0)
    nfail = 0; cnt = 0
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d = A.sum(1)
            if d.min() > 1:
                continue
            cnt += 1
            r46 = rhs46_A(A)
            leaves = [i for i in range(n) if d[i] == 1]
            k = len(leaves)
            choice_lists = []
            for v in leaves:
                nb = int(np.argmax(A[v]))
                choice_lists.append([u for u in range(n) if u != v and u != nb])
            found = None
            if np.prod([len(c) for c in choice_lists]) <= 200000:
                it = itertools.product(*choice_lists)
            else:
                it = (tuple(random.choice(c) for c in choice_lists)
                      for _ in range(200000))
            for combo in it:
                B = A.copy()
                ok = True
                for v, u in zip(leaves, combo):
                    if B[v, u]:  # duplicate (two leaves picked each other) fine
                        pass
                    B[v, u] = B[u, v] = 1
                db = B.sum(1)
                if db.min() < 2:
                    continue
                if rhs46_A(B) <= r46 + 1e-9:
                    found = combo
                    break
            if found is None:
                nfail += 1
                print(f"FAIL {g6} r46={r46:.4f} leaves={leaves}")
    print(f"leafy graphs: {cnt}, completion failures: {nfail}")

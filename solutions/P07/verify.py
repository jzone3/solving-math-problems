"""Independent verifier for a Graffiti-154 counterexample witness.

Graffiti conjecture 154 (WoW; as implemented in Roucairol-Cazenave's refutationGBR
src/models/conjectures/GenerateGraph.rs, CONJECTURE == 154):

    stdev(adjacency eigenvalues)  <=  n / mean(distance matrix)

where stdev is the population standard deviation of all n adjacency eigenvalues,
and mean(distance matrix) is the mean of ALL n^2 entries of the distance matrix
(diagonal zeros included), i.e. mu2 = 2W/n^2 with W the Wiener index.

Since trace(A)=0 and sum(lambda_i^2)=2m, stdev = sqrt(2m/n) exactly. Hence
violation  <=>  2m/n > n^2/mu2^2  <=>  8 m W^2 > n^7   (exact integer test).

We ALSO check the stricter-looking classical definition mu1 = W / C(n,2)
(average over unordered vertex pairs): violation <=> 2*m*mu1^2 > n^3
<=> 8 m W^2 > n^3 * (n(n-1))^2. Since mu1 >= mu2, a mu2-violation implies
a mu1-violation; both are reported.

The witness graph is loaded from witness_edges.txt (one "u v" edge per line,
0-indexed) in the same directory. Checks:
  1. graph is simple and connected (BFS)
  2. W computed by BFS from every vertex (no matrix powers, no eigensolve)
  3. exact integer violation tests for both mu definitions
  4. floating cross-check: numpy eigensolve stdev vs n/mu (skipped if numpy absent)

Prints PASS iff the witness violates the conjecture under the source-code
definition (mu2). Only stdlib required (numpy optional cross-check).
"""
import os
import sys
from collections import deque
from fractions import Fraction


def load_edges(path):
    edges = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            u, v = map(int, line.split())
            edges.append((u, v))
    return edges


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "witness_edges.txt")
    edges = load_edges(path)
    n = max(max(e) for e in edges) + 1
    adj = [set() for _ in range(n)]
    for u, v in edges:
        assert u != v, "self-loop"
        assert v not in adj[u], "multi-edge"
        adj[u].add(v)
        adj[v].add(u)
    m = len(edges)

    # BFS all-pairs, Wiener index
    W = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        assert all(d >= 0 for d in dist), "graph not connected"
        W += sum(dist)
    assert W % 2 == 0
    W //= 2  # sum over unordered pairs

    lhs = 8 * m * W * W
    viol_mu2 = lhs > n ** 7
    viol_mu1 = lhs * n > (n - 1) ** 2 * n ** 5 * n  # 8mW^2 > n^3 (n(n-1))^2 <=> 8mW^2 > n^5 (n-1)^2
    ratio2 = Fraction(lhs, n ** 7)
    ratio1 = Fraction(lhs, n ** 5 * (n - 1) ** 2)
    print(f"n={n} m={m} W={W}")
    print(f"mu2 = 2W/n^2 = {2*W/n**2:.6f}   mu1 = W/C(n,2) = {2*W/(n*(n-1)):.6f}")
    print(f"stdev(eigs) = sqrt(2m/n) = {(2*m/n)**0.5:.6f}   n/mu2 = {n**3/(2*W):.6f}   n/mu1 = {n*(n*(n-1))/(2*W):.6f}")
    print(f"exact 8mW^2 / n^7 = {float(ratio2):.6f}  (violation iff > 1): {viol_mu2}")
    print(f"exact 2m*mu1^2 / n^3 = {float(ratio1):.6f} (violation iff > 1): {viol_mu1}")

    # optional floating eigensolve cross-check (matches original formulation directly)
    try:
        import numpy as np
        A = np.zeros((n, n))
        for u, v in edges:
            A[u, v] = A[v, u] = 1.0
        eigs = np.linalg.eigvalsh(A)
        stdev = float(np.sqrt(np.mean((eigs - eigs.mean()) ** 2)))
        mu2 = 2 * W / n ** 2
        print(f"numpy eigensolve stdev = {stdev:.6f}  vs n/mu2 = {n/mu2:.6f} -> "
              f"violation: {stdev > n/mu2}")
        assert (stdev > n / mu2) == viol_mu2, "float/exact disagreement"
    except ImportError:
        print("numpy not available; skipping eigensolve cross-check")

    print("PASS" if viol_mu2 else "FAIL")
    sys.exit(0 if viol_mu2 else 1)


if __name__ == "__main__":
    main()

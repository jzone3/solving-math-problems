"""Graph-level annealing to probe whether the intermediate reductions for 129
are actually true on graphs (H* on degree sequences is FALSE; the loss was
Hong's bound). Scores (violation if > 0):

  gstar: lambda1 * dev_L - m          (G*  => 129 via R >= m/lambda1)
  cstar: M2 * dev_L^2 - m^3           (C*  => 129 via R >= m^{3/2}/sqrt(M2))
  conj : dev_L - R                    (129 itself)

Usage: python3 reduction_anneal.py <score> <n> <restarts> <iters> [seed]
"""

import sys
import numpy as np
from local_search import anneal, adj_to_g6


def make_score(name):
    def randic(A):
        d = A.sum(axis=1).astype(float)
        i, j = np.nonzero(np.triu(A, 1))
        return float(np.sum(1.0 / np.sqrt(d[i] * d[j])))

    def base(A):
        n = len(A)
        d = A.sum(axis=1).astype(float)
        m = d.sum() / 2
        if m == 0:
            return None
        dev2 = np.sum(d * (d + 1)) / n - (2 * m / n) ** 2
        return d, m, dev2

    def gstar(A):
        b = base(A)
        if b is None:
            return -1e9
        d, m, dev2 = b
        lam1 = float(np.linalg.eigvalsh(A.astype(float))[-1])
        return lam1 * float(np.sqrt(dev2)) - m

    def cstar(A):
        b = base(A)
        if b is None:
            return -1e9
        d, m, dev2 = b
        i, j = np.nonzero(np.triu(A, 1))
        M2 = float(np.sum(d[i] * d[j]))
        # normalize to keep annealing scale sane
        return (M2 * dev2 - m ** 3) / max(m ** 2, 1.0)

    def conj(A):
        b = base(A)
        if b is None:
            return -1e9
        d, m, dev2 = b
        return float(np.sqrt(dev2)) - randic(A)

    return {"gstar": gstar, "cstar": cstar, "conj": conj}[name]


def main():
    name, n, restarts, iters = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    score = make_score(name)
    gbest, gbestA = -1e9, None
    for r in range(restarts):
        b, A = anneal(score, n, iters, r % 5)
        if b > gbest:
            gbest, gbestA = b, A
    print(f"{name} n={n} best={gbest:+.8f} g6={adj_to_g6(gbestA)}")
    if gbest > 1e-9:
        print("VIOLATION-CANDIDATE")


if __name__ == "__main__":
    main()

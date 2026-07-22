"""Two disjoint balanced Turán graphs T(n,w) (each is an equality case, and so
is their union) plus sparse cross-edge patterns; also unbalanced part sizes.
Not fully covered by the k<=6 blow-up sweep once w >= 3 with cross edges.
Exact omega via B&B; numpy eigvalsh.
"""
import random
import numpy as np
from common import graph_score, clique_number_np

random.seed(3)


def turan_pair(parts1, parts2):
    n1, n2 = sum(parts1), sum(parts2)
    n = n1 + n2
    A = np.zeros((n, n), dtype=int)

    def fill(parts, off):
        idx = np.cumsum((0,) + tuple(parts)) + off
        A[off:off + sum(parts), off:off + sum(parts)] = 1
        for i in range(len(parts)):
            A[idx[i]:idx[i + 1], idx[i]:idx[i + 1]] = 0
    fill(parts1, 0)
    fill(parts2, n1)
    np.fill_diagonal(A, 0)
    return A, n1


def report(tag, A, results):
    n = A.shape[0]
    m = int(A.sum()) // 2
    if m == n * (n - 1) // 2:
        return
    w = clique_number_np(A)
    s, l1, l2, m = graph_score(A, w)
    results.append((s, tag, l1, l2, m, w))
    if s > 1e-9:
        print("VIOLATION", s, tag, flush=True)
        np.save("violation_dt.npy", A)


def main():
    results = []
    for w in range(2, 9):
        for t in range(2, 7):  # part size
            parts = (t,) * w
            base, n1 = turan_pair(parts, parts)
            n = base.shape[0]
            report(f"2xT w={w} t={t} cross=0", base, results)
            # single cross edge, cross matching, cross star, random cross sets
            for pat, edges in [
                ("1e", [(0, n1)]),
                ("match3", [(i, n1 + i) for i in range(min(3, n1))]),
                ("star4", [(0, n1 + j) for j in range(min(4, n1))]),
            ]:
                A = base.copy()
                for (i, j) in edges:
                    A[i, j] = A[j, i] = 1
                report(f"2xT w={w} t={t} {pat}", A, results)
            for e in (2, 5, 10):
                A = base.copy()
                for _ in range(e):
                    i, j = random.randrange(n1), n1 + random.randrange(n - n1)
                    A[i, j] = A[j, i] = 1
                report(f"2xT w={w} t={t} rand{e}", A, results)
        # unbalanced pairs: T(n,w) u T(n',w)
        for t1 in range(2, 6):
            for t2 in range(t1, 6):
                A, n1 = turan_pair((t1,) * w, (t2,) * w)
                report(f"2xT w={w} t1={t1} t2={t2}", A, results)
    results.sort(key=lambda r: -r[0])
    print(f"searched {len(results)}; top 15:")
    for r in results[:15]:
        print(f"score={r[0]:+.8f} {r[1]} l1={r[2]:.4f} l2={r[3]:.4f} m={r[4]} w={r[5]}")


if __name__ == "__main__":
    main()

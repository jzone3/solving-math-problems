"""Second-generation reductions for 129 (after H*, C* died):

  G*: lambda1 * dev_L <= m                       (=> 129 via R >= m/lambda1)
  I*: s_plus * dev_L <= m                        (=> G*, since s_plus >= lambda1)
  J*: sqrt(max_u sum_{v~u} d_v) * dev_L <= m     (=> G*, since lambda1^2 <= max_u sum_{v~u} d_v)

All tight at K_k u (k-2)K_1 and (asymptotically) stars.
Usage: python3 test_reduction129b.py <n>          (exhaustive geng scan)
       python3 test_reduction129b.py anneal <n> <restarts> <iters>
"""

import subprocess
import sys
import numpy as np
from exhaustive import g6_to_adj


def scores(A):
    n = len(A)
    d = A.sum(axis=1).astype(float)
    m = d.sum() / 2
    if m == 0:
        return None
    dev = float(np.sqrt(np.sum(d * (d + 1)) / n - (2 * m / n) ** 2))
    lam = np.linalg.eigvalsh(A.astype(float))
    lam1 = float(lam[-1])
    splus = float(np.sqrt(np.sum(lam[lam > 0] ** 2)))
    T = float(np.max(A.astype(float) @ d))
    return (lam1 * dev - m, splus * dev - m, np.sqrt(T) * dev - m)


def exhaustive(n):
    proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE,
                            text=True, bufsize=1 << 20)
    worst = [[], [], []]
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        s = scores(g6_to_adj(line))
        if s is None:
            continue
        for k in range(3):
            worst[k].append((s[k], line))
        if len(worst[0]) > 10000:
            for k in range(3):
                worst[k].sort(reverse=True)
                del worst[k][3:]
    for k, name in enumerate(["G*", "I*", "J*"]):
        worst[k].sort(reverse=True)
        print(f"n={n} top {name} (violation if >0):")
        for s, g in worst[k][:3]:
            print(f"  {s:+.8f}  {g}")


def anneal_mode(n, restarts, iters):
    from local_search import anneal, adj_to_g6
    for k, name in enumerate(["G*", "I*", "J*"]):
        def sc(A, k=k):
            s = scores(A)
            return -1e9 if s is None else s[k]
        best, A = -1e9, None
        for r in range(restarts):
            b, AA = anneal(sc, n, iters, r % 5)
            if b > best:
                best, A = b, AA
        print(f"anneal {name} n={n} best={best:+.8f} g6={adj_to_g6(A)}"
              + ("  VIOLATION-CANDIDATE" if best > 1e-9 else ""))


if __name__ == "__main__":
    if sys.argv[1] == "anneal":
        anneal_mode(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        exhaustive(int(sys.argv[1]))

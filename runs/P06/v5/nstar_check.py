"""N* — a NEW pure degree-sequence reduction of conjecture 129 via an
antitone-coupling (transportation-LP) lower bound on the Randic index.

For a degree sequence d (all d_i >= 1), let e be the multiset of 2m edge
ENDPOINTS (each vertex of degree k contributes k copies of k). For any graph
realizing d,  R = sum_E 1/sqrt(du dv), and since the cost 1/sqrt(xy) is
supermodular, the transportation relaxation (pair the 2m endpoints, ignoring
graphicality) is minimized by the antitone coupling:

    LB(d) = sum_{i=1}^{m} 1/sqrt( e_(i) * e_(2m+1-i) )   (e sorted).

LB(d) <= R(G) for EVERY realization G of d. It is EXACT for stars, K_k,
complete split CS(a,b), and complete bipartite graphs.

N*:  dev_max(d) <= LB(d),  where dev_max is dev_L maximized over the number
of isolated-vertex paddings t >= 0 (optimal real n* = 8m^2/(M1+2m) clamped to
>= n', checked at neighboring integers).  N* implies conjecture 129 for ALL
graphs (any n, any realization) whose non-isolated degree sequence is d.

Modes:
  exhaustive <nmax>   -- all graphical sequences with n' <= nmax (E-G check)
  anneal <npmax> <restarts> <iters> [seed]
"""

import sys
import math
import random


def erdos_gallai(d):
    d = sorted(d, reverse=True)
    if sum(d) % 2:
        return False
    n = len(d)
    pre = [0]
    for x in d:
        pre.append(pre[-1] + x)
    for k in range(1, n + 1):
        rhs = k * (k - 1) + sum(min(x, k) for x in d[k:])
        if pre[k] > rhs:
            return False
    return True


def lb_randic(d):
    e = []
    for x in d:
        e.extend([x] * x)
    e.sort()
    m = len(e) // 2
    return sum(1.0 / math.sqrt(e[i] * e[-1 - i]) for i in range(m))


def dev_max(d):
    nprime = len(d)
    m = sum(d) / 2
    M1 = sum(x * x for x in d)
    q = M1 + 2 * m
    best = 0.0
    cands = {nprime}
    nstar = 8 * m * m / q
    for nn in (int(nstar), int(nstar) + 1):
        if nn >= nprime:
            cands.add(nn)
    for nn in cands:
        dev2 = q / nn - 4 * m * m / (nn * nn)
        if dev2 > best:
            best = dev2
    return math.sqrt(best)


def score(d):
    return dev_max(d) - lb_randic(d)


def gen_sequences(n, maxd, prefix, out):
    if n == 0:
        out.append(list(prefix))
        return
    for k in range(min(maxd, len(prefix) + n - 1), 0, -1):
        prefix.append(k)
        gen_sequences(n - 1, k, prefix, out)
        prefix.pop()


def exhaustive(nmax):
    for n in range(2, nmax + 1):
        seqs = []
        gen_sequences(n, n - 1, [], seqs)
        worst = []
        cnt = 0
        for d in seqs:
            if not erdos_gallai(d):
                continue
            cnt += 1
            worst.append((score(d), tuple(d)))
            worst.sort(reverse=True)
            del worst[3:]
        print(f"n'={n} graphical seqs={cnt} top N* (violation if >0):")
        for s, d in worst:
            print(f"  {s:+.8f}  d={d}")


def anneal(npmax, restarts, iters, seed):
    rng = random.Random(seed)
    gbest = (-1e18, None)
    for r in range(restarts):
        nprime = rng.randint(4, npmax)
        while True:
            d = sorted((rng.randint(1, nprime - 1) for _ in range(nprime)),
                       reverse=True)
            if erdos_gallai(d):
                break
        s = score(d)
        best = (s, list(d))
        T0, T1 = 1.0, 1e-4
        for t in range(iters):
            T = T0 * (T1 / T0) ** (t / iters)
            d2 = list(d)
            op = rng.random()
            if op < 0.5:
                i = rng.randrange(len(d2))
                d2[i] += rng.choice([-2, -1, 1, 2])
                j = rng.randrange(len(d2))
                d2[j] += rng.choice([-2, -1, 1, 2])
            elif op < 0.75:
                d2.append(rng.randint(1, max(1, len(d2) - 1)))
            elif op < 0.95 and len(d2) > 4:
                d2.pop(rng.randrange(len(d2)))
            else:
                i = rng.randrange(len(d2))
                d2[i] = rng.randint(1, len(d2) - 1)
            if not d2 or min(d2) < 1 or max(d2) > len(d2) - 1:
                continue
            if not erdos_gallai(d2):
                continue
            s2 = score(d2)
            if s2 >= s or rng.random() < math.exp((s2 - s) / max(T, 1e-12)):
                d, s = d2, s2
                if s > best[0]:
                    best = (s, list(d))
        if best[0] > gbest[0]:
            gbest = best
    from collections import Counter
    s, d = gbest
    print(f"anneal npmax={npmax} best N*={s:+.8f} "
          f"deg multiset={dict(sorted(Counter(d).items()))}"
          + ("  VIOLATION-CANDIDATE" if s > 1e-9 else ""))


if __name__ == "__main__":
    if sys.argv[1] == "exhaustive":
        exhaustive(int(sys.argv[2]))
    else:
        anneal(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
               int(sys.argv[5]) if len(sys.argv) > 5 else 1)

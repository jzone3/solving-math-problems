"""Adversarial search for violations of H*:
    (2m - n' + 1) * dev_L^2(n)  <=  m^2
over graphical degree sequences d (all d_i >= 1, n' = len(d)) and any number
t >= 0 of added isolated vertices (n = n' + t chosen adversarially: the
continuous optimum n* = 8m^2/(M1+2m) clamped to [n', inf), checked at
floor/ceil integers).

H* implies conjecture 129 via R >= m/lambda1 and Hong's bound.
Simulated annealing on degree multisets with Erdos-Gallai graphicality.

Usage: python3 hstar_search.py <nprime_max> <restarts> <iters> [seed]
"""

import sys
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


def hstar_gap(d):
    """max over n of (2m-n'+1)*dev2(n) - m^2  (violation if > 0)."""
    nprime = len(d)
    m = sum(d) / 2
    M1 = sum(x * x for x in d)
    q = M1 + 2 * m
    best = -1e18
    cands = {nprime}
    nstar = 8 * m * m / q
    for nn in (int(nstar), int(nstar) + 1):
        if nn >= nprime:
            cands.add(nn)
    for nn in cands:
        dev2 = q / nn - 4 * m * m / nn / nn
        best = max(best, (2 * m - nprime + 1) * dev2 - m * m)
    return best


def anneal(npmax, iters, rng):
    nprime = rng.randint(3, npmax)
    while True:
        d = [rng.randint(1, nprime - 1) for _ in range(nprime)]
        if erdos_gallai(d):
            break
    s = hstar_gap(d)
    best, bestd = s, list(d)
    T0, T1 = 5.0, 1e-3
    for t in range(iters):
        T = T0 * (T1 / T0) ** (t / iters)
        d2 = list(d)
        op = rng.random()
        if op < 0.45 and len(d2) > 3:
            i = rng.randrange(len(d2))
            d2[i] += rng.choice([-2, -1, 1, 2])
            j = rng.randrange(len(d2))
            d2[j] += rng.choice([-2, -1, 1, 2])
        elif op < 0.7:
            d2.append(rng.randint(1, max(1, len(d2) - 1)))
        elif op < 0.9 and len(d2) > 3:
            d2.pop(rng.randrange(len(d2)))
        else:
            i = rng.randrange(len(d2))
            d2[i] = rng.randint(1, len(d2) - 1)
        if not d2 or min(d2) < 1 or max(d2) > len(d2) - 1:
            continue
        if not erdos_gallai(d2):
            continue
        s2 = hstar_gap(d2)
        import math
        if s2 >= s or rng.random() < math.exp(min(0, (s2 - s) / max(T, 1e-12))):
            d, s = d2, s2
            if s > best:
                best, bestd = s, list(d)
    return best, bestd


def main():
    npmax, restarts, iters = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = random.Random(seed)
    gbest, gbestd = -1e18, None
    for r in range(restarts):
        b, d = anneal(npmax, iters, rng)
        if b > gbest:
            gbest, gbestd = b, d
    from collections import Counter
    print(f"npmax={npmax} best gap={gbest:+.6f} "
          f"deg multiset={dict(sorted(Counter(gbestd).items()))}")
    if gbest > 1e-9:
        print("HSTAR-VIOLATION-CANDIDATE", sorted(gbestd, reverse=True))


if __name__ == "__main__":
    main()

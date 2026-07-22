"""
P06/V1 escalation: search over DEGREE SEQUENCES.

Since dev(L)^2 = Var(d)+dbar depends only on the degree sequence d, a graph G
violates conj 129 only if dev(d) > R(G) >= R_lb(d), where

  R_lb(d) = (1/2) * sum_u w_u * (sum of the d_u smallest w_v over v != u),
  w_u = 1/sqrt(d_u)   (vertices with d_u = 0 contribute nothing)

is a valid lower bound on the Randic index of EVERY realization of d (each
vertex's neighbor-weight sum is at least the sum of the d_u smallest weights
available). So if dev(d) <= R_lb(d) for all graphical d of length n, no graph
on n vertices is a counterexample.

We (a) exhaust all graphical degree sequences for n <= 14, (b) run randomized
hill-climbing over graphical sequences (Erdos-Gallai test) for n up to 400,
maximizing dev - R_lb. Any positive would then be attacked with min-R
realizations and exact arithmetic.
"""
import heapq
import math
import random
import sys


def erdos_gallai(seq):
    s = sorted(seq, reverse=True)
    n = len(s)
    if sum(s) % 2:
        return False
    pref = [0]
    for x in s:
        pref.append(pref[-1] + x)
    for k in range(1, n + 1):
        rhs = k * (k - 1) + sum(min(x, k) for x in s[k:])
        if pref[k] > rhs:
            return False
    return True


def dev(seq):
    n = len(seq)
    s1 = sum(seq)
    s2 = sum(x * x for x in seq)
    return math.sqrt(max((s1 + s2) / n - (s1 / n) ** 2, 0.0))


def randic_lb(seq):
    pos = sorted((x for x in seq if x > 0))
    w = [1.0 / math.sqrt(x) for x in pos]  # descending degree -> w ascending? no:
    # pos ascending degrees -> w descending weights. We need smallest weights first:
    w = sorted(w)  # smallest weights = largest degrees
    pref = [0.0]
    for x in w:
        pref.append(pref[-1] + x)
    total = 0.0
    # for vertex u with weight w_u, the d_u smallest weights among OTHERS:
    # approximate by d_u smallest overall, subtracting own weight if included.
    for d_u in pos:
        w_u = 1.0 / math.sqrt(d_u)
        k = d_u
        s = pref[min(k, len(w))]
        # if own weight is among the k smallest, swap in the next one (still a LB)
        if w_u <= w[min(k, len(w)) - 1]:
            s = s - w_u + (w[k] if k < len(w) else w[-1])
            # note: replacement keeps it a lower bound (next-smallest >= removed)
            # if k == len(w) this vertex would need more neighbors than exist; seq
            # is graphical so this cannot happen for simple graphs.
        total += w_u * s
    return total / 2.0


def exhaust(n):
    """all non-increasing graphical sequences of length n (entries 0..n-1)"""
    best = (-1e18, None)
    seq = []

    def rec(i, maxd):
        nonlocal best
        if i == n:
            if erdos_gallai(seq):
                s = dev(seq) - randic_lb(seq)
                if s > best[0]:
                    best = (s, list(seq))
            return
        for d in range(min(maxd, n - 1), -1, -1):
            seq.append(d)
            rec(i + 1, d)
            seq.pop()

    rec(0, n - 1)
    return best


def hillclimb(n, iters, seed):
    rng = random.Random(seed)
    # seed at equality-family shape when n even: q = n/2+1 vertices of degree q-1
    q = n // 2 + 1
    cur = [q - 1] * q + [0] * (n - q)
    if not erdos_gallai(cur):
        cur = [1] * (n - n % 2) + [0] * (n % 2)
    def sc(s):
        return dev(s) - randic_lb(s)
    curs = sc(cur)
    best, bests = curs, cur[:]
    for _ in range(iters):
        cand = cur[:]
        for _ in range(rng.randint(1, 2)):
            i = rng.randrange(n)
            cand[i] = max(0, min(n - 1, cand[i] + rng.choice([-2, -1, 1, 2])))
        if not erdos_gallai(cand):
            continue
        s = sc(cand)
        if s >= curs - 0.02 * rng.random():
            cur, curs = cand, s
            if s > best:
                best, bests = s, cand[:]
    return best, bests


if __name__ == "__main__":
    for n in range(4, 15):
        s, seq = exhaust(n)
        print(f"exhaust n={n}: max dev - R_lb = {s:+.9f} at {seq}")
    for n in [16, 20, 30, 50, 100, 200, 400]:
        res = max(hillclimb(n, 4000 if n <= 100 else 1500, sd) for sd in range(4))
        print(f"hillclimb n={n}: best dev - R_lb = {res[0]:+.9f} at "
              f"{sorted(set((d, res[1].count(d)) for d in res[1]), reverse=True)}")

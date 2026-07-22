"""Unified GM reduction test (NO density condition):

  (*)  n^2 m^2 >= (nA - 4m^2) * exp( (1/m) sum_v d_v ln d_v )
       for every graphical degree sequence (A = sum d(d+1), 2m = sum d).

Since R >= m * exp(-(1/2m) sum d ln d)  (AM-GM over edge weights, as
sum_{uv in E} ln(d_u d_v) = sum_v d_v ln d_v), inequality (*) implies
n^2 R^2 >= nA - 4m^2, i.e. R^2 >= dev^2 -- ALL of WoW 129.

Anneal over graphical integer sequences maximizing
  g = ln(nA - 4m^2) + (1/m) sum d ln d - ln(n^2 m^2).
g > 0 => reduction fails on that sequence (129 may still hold via structure).
"""
import random, math

def erdos_gallai(seq):
    s = sorted(seq, reverse=True)
    n = len(s)
    if sum(s) % 2: return False
    pref = 0
    for k in range(1, n + 1):
        pref += s[k - 1]
        tail = sum(min(x, k) for x in s[k:])
        if pref > k * (k - 1) + tail:
            return False
    return True

def g(seq, n):
    m2 = sum(seq)
    if m2 == 0: return None
    m = m2 / 2
    A = sum(d * (d + 1) for d in seq)
    rhs = n * A - m2 * m2
    if rhs <= 0: return -1e18
    H = sum(d * math.log(d) for d in seq if d) / m
    return math.log(rhs) + H - math.log(n * n * m * m)

rnd = random.Random(11)
overall = None
for n in [8, 12, 16, 24, 40, 60, 100]:
    best = None
    for restart in range(40):
        kind = restart % 3
        if kind == 0:
            t = rnd.randint(2, n)
            seq = [t - 1] * t + [0] * (n - t)
        elif kind == 1:
            seq = [n - 1] + [1] * (n - 1)  # star
        else:
            seq = [rnd.randint(0, n - 1) for _ in range(n)]
            while not erdos_gallai(seq):
                seq = [rnd.randint(0, n - 1) for _ in range(n)]
        cur = g(seq, n)
        for it in range(6000):
            i, j = rnd.randrange(n), rnd.randrange(n)
            new = seq[:]
            new[i] += rnd.choice([-1, 1])
            new[j] += rnd.choice([-1, 1])
            if any(x < 0 or x > n - 1 for x in new): continue
            if not erdos_gallai(new): continue
            val = g(new, n)
            if val is not None and val >= cur:
                seq, cur = new, val
        if best is None or cur > best[0]:
            best = (cur, sorted(seq, reverse=True))
    print(f"n={n}: max g = {best[0]:.9f} seq(top8) {best[1][:8]} zeros={best[1].count(0)}", flush=True)
    if overall is None or best[0] > overall[0]:
        overall = best
print("overall max g:", overall[0])

"""Case-1 GM lemma test restricted to GRAPHICAL degree sequences.
Adversarial search: random integer graphical sequences (Erdos-Gallai checked)
satisfying the density condition 8m^2 >= A n, maximizing
   g = ln A + (1/2m) sum d ln d - ln(4m^2).
Local moves: +-1 on random coordinates, keep graphical + density.
g > 0 for a graphical sequence => the GM route to Case 1 fails on it
(but 4mR >= A may still hold via structure; report the sequence).
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

def g_and_dense(seq, n):
    m2 = sum(seq)
    if m2 == 0: return None
    A = sum(d * (d + 1) for d in seq)
    if 8 * (m2 // 2) ** 2 * 4 < A * n * 4:  # 8m^2 >= An  with m=m2/2 => 2*m2^2 >= A*n
        pass
    if 2 * m2 * m2 < A * n:
        return None
    H = sum(d * math.log(d) for d in seq if d) / m2
    return math.log(A) + H - math.log(m2 * m2)

best_overall = None
rnd = random.Random(7)
for n in [8, 12, 16, 24, 40, 60]:
    best = None
    for restart in range(40):
        # seed: clique-like graphical dense sequence
        t = rnd.randint(max(3, n // 2), n)
        seq = [t - 1] * t + [0] * (n - t)
        cur = g_and_dense(seq, n)
        if cur is None: continue
        for it in range(4000):
            i = rnd.randrange(n)
            j = rnd.randrange(n)
            delta_i = rnd.choice([-1, 1])
            delta_j = rnd.choice([-1, 1])
            new = seq[:]
            new[i] += delta_i
            new[j] += delta_j
            if any(x < 0 or x > n - 1 for x in new): continue
            val = g_and_dense(new, n)
            if val is None or not erdos_gallai(new): continue
            if val >= cur:
                seq, cur = new, val
        if best is None or cur > best[0]:
            best = (cur, sorted(seq, reverse=True))
    print(f"n={n}: max g = {best[0]:.9f} seq(top10) {best[1][:10]} zeros={best[1].count(0)}")
    if best_overall is None or best[0] > best_overall[0]:
        best_overall = best
print("overall:", best_overall[0])

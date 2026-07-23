"""
P06/V1 escalation 2: block-structured degree sequences at HUGE n.

State: up to B blocks (degree value d_b, count c_b), n = sum c_b up to 10^6.
Score = dev(d) - R_lb(d), both computed in O(B^2) closed form from blocks
(cross-checked against degseq_search on expanded sequences for small n).
Graphicality via Erdos-Gallai restricted to block boundaries (standard: it
suffices to check EG at k = cumulative block counts).
Anneal over (d_b, c_b) with moves: perturb degree, move counts between blocks,
split/merge blocks. Seeded at equality family and random states.
"""
import math
import random
import sys

sys.path.insert(0, ".")
from degseq_search import erdos_gallai, dev, randic_lb


def expand(blocks):
    seq = []
    for d, c in blocks:
        seq += [d] * c
    return sorted(seq, reverse=True)


def eg_blocks(blocks):
    # blocks sorted by degree desc; check EG at cumulative boundaries
    bl = sorted([b for b in blocks if b[1] > 0], reverse=True)
    n = sum(c for _, c in bl)
    if sum(d * c for d, c in bl) % 2:
        return False
    if any(d >= n or d < 0 for d, _ in bl):
        return False
    pref = 0
    k = 0
    for i, (d, c) in enumerate(bl):
        k += c
        pref += d * c
        rhs = k * (k - 1)
        for d2, c2 in bl[i + 1:]:
            rhs += c2 * min(d2, k)
        if pref > rhs:
            return False
    return True


def score_blocks(blocks):
    bl = sorted([b for b in blocks if b[1] > 0], reverse=True)
    n = sum(c for _, c in bl)
    s1 = sum(d * c for d, c in bl)
    s2 = sum(d * d * c for d, c in bl)
    dev2 = (s1 + s2) / n - (s1 / n) ** 2
    devv = math.sqrt(max(dev2, 0.0))
    # R_lb: weights ascending with degree descending; block-structured prefix sums
    pos = [(d, c) for d, c in bl if d > 0]
    if not pos:
        return devv
    w = [(1.0 / math.sqrt(d), c) for d, c in pos]  # ascending weight order = bl order
    npos = sum(c for _, c in pos)
    # prefix sums over sorted-ascending weights == block order (largest degree first)
    total = 0.0
    for du, cu in pos:
        wu = 1.0 / math.sqrt(du)
        k = du
        # sum of k smallest weights
        s = 0.0
        rem = k
        for wv, cv in w:
            take = min(rem, cv)
            s += take * wv
            rem -= take
            if rem == 0:
                last_w = wv
                break
        # own-weight replacement (mirror randic_lb): if wu <= last of the k smallest
        if wu <= last_w + 1e-15:
            # next weight after the k smallest
            rem2 = k
            nxt = None
            for wv, cv in w:
                if rem2 < cv:
                    nxt = wv
                    break
                rem2 -= cv
            if nxt is None:
                nxt = w[-1][0]
            s = s - wu + nxt
        total += cu * wu * s
    return devv - total / 2.0


def xcheck():
    rng = random.Random(3)
    for _ in range(300):
        B = rng.randint(1, 4)
        n = rng.randint(4, 30)
        blocks = []
        rem = n
        for b in range(B):
            c = rem if b == B - 1 else rng.randint(1, max(1, rem - (B - b - 1)))
            blocks.append((rng.randint(0, n - 1), c))
            rem -= c
            if rem <= 0:
                break
        seq = expand(blocks)
        if not erdos_gallai(seq):
            assert not eg_blocks(blocks), blocks
            continue
        assert eg_blocks(blocks), blocks
        a = score_blocks(blocks)
        b_ = dev(seq) - randic_lb(seq)
        assert abs(a - b_) < 1e-9, (blocks, a, b_)
    print("block xcheck PASS (score + EG agree with expanded sequences)")


def anneal(n, iters, seed, B=5):
    rng = random.Random(seed)
    q = n // 2 + 1
    blocks = [(q - 1, q), (0, n - q)]
    while len(blocks) < B:
        blocks.append((rng.randint(0, n - 1), 0))
    def valid(bl):
        return sum(c for _, c in bl) == n and all(c >= 0 for _, c in bl) and eg_blocks(bl)
    cur = score_blocks(blocks)
    best, bestb = cur, list(blocks)
    for t in range(iters):
        nb = [list(b) for b in blocks]
        mv = rng.random()
        i = rng.randrange(len(nb))
        if mv < 0.4:
            nb[i][0] = max(0, min(n - 1, nb[i][0] + rng.choice(
                [-1000, -100, -10, -3, -1, 1, 3, 10, 100, 1000])))
        else:
            j = rng.randrange(len(nb))
            amt = rng.choice([1, 3, 10, 100, 1000, 10000])
            amt = min(amt, nb[i][1])
            nb[i][1] -= amt
            nb[j][1] += amt
        nb = [tuple(b) for b in nb]
        if not valid(nb):
            continue
        s = score_blocks(nb)
        if s >= cur - 0.05 * rng.random() * max(0.1, 1 - t / iters):
            blocks, cur = nb, s
            if s > best:
                best, bestb = s, list(nb)
    return best, bestb


if __name__ == "__main__":
    xcheck()
    for n in [10**3, 10**4, 10**5, 10**6]:
        res = max(anneal(n, 30000, sd) for sd in range(5))
        print(f"n={n}: best block score = {res[0]:+.9f} at {sorted(res[1], reverse=True)}",
              flush=True)
        if res[0] > 1e-9:
            print("VIOLATION CANDIDATE", res)

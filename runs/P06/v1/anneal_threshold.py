"""
P06/V1 extension: simulated annealing over THRESHOLD graphs.

Rationale: dev(L)^2 = Var(deg)+avgdeg depends only on the degree sequence, so a
counterexample needs a realization minimizing the Randic index; threshold graphs
(creation sequences) connect high-degree to high-degree vertices, minimizing R
heuristically, and contain all our star-like near-miss families (star = 1 then
0s ... actually 0^(n-2) 1; complete split; pineapple-like graphs).

State: creation bits b[1..n-1] (b=1 dominating, b=0 isolated at insertion).
Score = dev - R, computed exactly from the sequence in O(n^2) worst case
(O(#dominating * n)). Moves: flip a bit / swap two bits.
Cross-checked against harness adjacency computation.
"""
import math
import random
import sys

sys.path.insert(0, ".")
import harness as H


def degseq_from_bits(bits):
    n = len(bits) + 1
    deg = [0] * n
    for i, b in enumerate(bits):
        v = i + 1
        if b:
            deg[v] += v
            for u in range(v):
                deg[u] += 1
    return deg


def score_bits(bits):
    n = len(bits) + 1
    deg = degseq_from_bits(bits)
    dev = H.dev_from_degseq(deg)
    R = 0.0
    for i, b in enumerate(bits):
        v = i + 1
        if b:
            dv = deg[v]
            s = 0.0
            for u in range(v):
                s += 1.0 / math.sqrt(deg[u])
            R += s / math.sqrt(dv)
    # NB: edges are counted once: each dominating vertex v contributes edges to
    # all u < v; later dominating vertices w>v recount edge (v,w)? No: when w is
    # added it connects to all u<w including v, and v connected only to u<v. OK.
    return dev - R, dev, R


def xcheck():
    rng = random.Random(1)
    for _ in range(50):
        bits = [rng.randint(0, 1) for _ in range(rng.randint(2, 14))]
        if not any(bits):
            bits[0] = 1
        adj = H.threshold_graph(bits)
        s, dev, R = score_bits(bits)
        assert abs(dev - H.dev_eig(adj)) < 1e-9
        assert abs(R - H.randic(adj)) < 1e-9
    print("anneal xcheck PASS")


def anneal(n, iters, seed, T0=0.5, Tend=1e-4):
    rng = random.Random(seed)
    # seed at star: vertex n-1 dominating only
    bits = [0] * (n - 1)
    bits[-1] = 1
    cur, dev, R = score_bits(bits)
    best, best_bits = cur, bits[:]
    for t in range(iters):
        T = T0 * (Tend / T0) ** (t / iters)
        i = rng.randrange(n - 1)
        bits[i] ^= 1
        if not any(bits):
            bits[i] ^= 1
            continue
        new, dev, R = score_bits(bits)
        if new >= cur or rng.random() < math.exp((new - cur) / T):
            cur = new
            if new > best:
                best, best_bits = new, bits[:]
        else:
            bits[i] ^= 1
    return best, best_bits


if __name__ == "__main__":
    xcheck()
    for n in [10, 20, 40, 80, 160, 320, 640]:
        iters = 20000 if n <= 160 else 6000
        results = [anneal(n, iters, seed) for seed in range(3)]
        best, bits = max(results)
        star = -1.0 / math.sqrt(n - 1) + (H.dev_from_degseq([n - 1] + [1] * (n - 1))
                                          - math.sqrt(n - 1) - (-1.0 / math.sqrt(n - 1)))
        s, dev, R = score_bits(bits)
        ndom = sum(bits)
        print(f"n={n:4d} best={best:+.6f} dev={dev:.4f} R={R:.4f} #dom={ndom} "
              f"star_score={H.dev_from_degseq([n-1]+[1]*(n-1)) - math.sqrt(n-1):+.6f}")
        if best > 0:
            print("POSITIVE! bits:", "".join(map(str, bits)))

"""
P06/V1: large-scale randomized search over graphical degree sequences for
violations of the reduced inequality dev(d) <= R_lb(d)  (which would be a
necessary condition for any counterexample to conj 129 on any realization).

Samplers: (a) random near-equality perturbations, (b) power-law-ish sequences,
(c) two/three-block sequences with random block sizes/degrees, (d) uniform
random graphical sequences (via random graphs' degree sequences would bias;
we use Erdos-Gallai-filtered random multisets). Reports global max score.
"""
import math
import random
import sys

sys.path.insert(0, ".")
from degseq_search import erdos_gallai, dev, randic_lb


def trial_blocks(rng, n):
    kblocks = rng.randint(1, 4)
    seq = []
    remaining = n
    for b in range(kblocks):
        c = rng.randint(1, max(1, remaining - (kblocks - b - 1)))
        if b == kblocks - 1:
            c = remaining
        d = rng.randint(0, n - 1)
        seq += [d] * c
        remaining -= c
        if remaining <= 0:
            break
    return seq[:n] + [0] * (n - len(seq))


def trial_powerlaw(rng, n):
    a = rng.uniform(1.2, 3.0)
    return [min(n - 1, max(0, int((n - 1) * (rng.random() ** a)))) for _ in range(n)]


def trial_perturb_eq(rng, n):
    q = n // 2 + 1
    seq = [q - 1] * q + [0] * (n - q)
    for _ in range(rng.randint(1, 6)):
        i = rng.randrange(n)
        seq[i] = max(0, min(n - 1, seq[i] + rng.choice([-3, -2, -1, 1, 2, 3])))
    return seq


def trial_uniform(rng, n):
    return [rng.randrange(n) for _ in range(n)]


def main(total=400000, seed=0):
    rng = random.Random(seed)
    best = (-1e18, None)
    tried = 0
    for i in range(total):
        n = rng.choice([12, 16, 24, 40, 64, 100, 160, 250, 400, 700])
        f = rng.choice([trial_blocks, trial_powerlaw, trial_perturb_eq, trial_uniform])
        seq = f(rng, n)
        if sum(seq) % 2:
            seq[seq.index(max(seq))] -= 1
        if not erdos_gallai(seq):
            continue
        tried += 1
        s = dev(seq) - randic_lb(seq)
        if s > best[0]:
            best = (s, (n, sorted(set((d, seq.count(d)) for d in set(seq)), reverse=True)))
            if s > 1e-9:
                print("VIOLATION CANDIDATE:", best, flush=True)
    print(f"random degseq search: {tried} graphical sequences scored, "
          f"max dev - R_lb = {best[0]:+.9f} at {best[1]}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400000)

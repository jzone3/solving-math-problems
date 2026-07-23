#!/usr/bin/env python3
"""
Optimistic upper-bound trajectory model for the counting+kill pipeline.

Per level (prime p): holes h -> h*p cells; structured coverage assumed
PERFECT (no overlap waste): covered fraction = sum of 1/m over all NEW
usable moduli m | M_l with m >= T (each modulus used once, so new density
at level l is S_l - S_{l-1} where S = sum over divisors >= T of 1/m).
Kills: up to current pool = #divisors(M_l) >= T minus kills spent.
If even this diverges, no greedy variant of the pipeline can succeed.
"""


def small_divisor_stats(Mf, T):
    """(count, reciprocal sum) of divisors < T; DFS bounded by T."""
    primes = sorted(Mf)
    cnt, s = 0, 0.0
    def rec(i, prod):
        nonlocal cnt, s
        if i == len(primes):
            cnt += 1
            s += 1.0 / prod
            return
        p, v = primes[i], prod
        for _ in range(Mf[p] + 1):
            if v >= T:
                break
            rec(i + 1, v)
            v *= p
    rec(0, 1)
    return cnt, s


def sigma_ratio(Mf):
    r = 1.0
    for p, e in Mf.items():
        r *= (1 - p ** -(e + 1)) / (1 - 1 / p)
    return r


def simulate(T, levels, verbose=False):
    h = 1.0
    Mf = {}
    spent = 0
    S_prev = 0.0
    for p in levels:
        Mf[p] = Mf.get(p, 0) + 1
        cnt_small, s_small = small_divisor_stats(Mf, T)
        S = sigma_ratio(Mf) - s_small
        dens_new = max(0.0, S - S_prev)
        S_prev = S
        cells = h * p
        h = max(0.0, cells * (1 - dens_new))
        D = 1
        for e in Mf.values():
            D *= e + 1
        pool = D - cnt_small - spent
        k = min(h, max(0, pool))
        h -= k
        spent += int(k)
        if verbose:
            print(f"p={p}: dens_new={dens_new:.4f} holes={h:.3e} pool={float(pool - int(k)):.3e}")
        if h <= 0:
            return True
    return h <= 0, h


CONFIGS = {
    "fat": [2]*9 + [3]*6 + [5]*4 + [7]*3 + [11]*2 + [13]*2 + [17]*2 +
           [19]*2 + [23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
            79, 83, 89, 97, 101, 103, 107, 109, 113],
    "fatter": [2]*12 + [3]*8 + [5]*5 + [7]*4 + [11]*3 + [13]*2 + [17]*2 +
              [19]*2 + [23]*2 + [29]*2 + [31, 37, 41, 43, 47, 53, 59, 61,
               67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
               131, 137, 139, 149, 151],
    "huge": [2]*20 + [3]*12 + [5]*8 + [7]*6 + [11]*4 + [13]*4 + [17]*3 +
            [19]*3 + [23]*2 + [29]*2 + [31]*2 + [37]*2 + [41]*2 + [43]*2 +
            list({*range(47, 400)} - {n for n in range(47, 400)
                 if any(n % d == 0 for d in range(2, int(n**0.5) + 1))}.__xor__(set())) ,
}
# fix: primes 47..400
def primes_upto(a, b):
    return [n for n in range(a, b) if all(n % d for d in range(2, int(n**0.5) + 1))]
CONFIGS["huge"] = [2]*20 + [3]*12 + [5]*8 + [7]*6 + [11]*4 + [13]*4 + \
    [17]*3 + [19]*3 + [23]*2 + [29]*2 + [31]*2 + [37]*2 + [41]*2 + [43]*2 + \
    primes_upto(47, 400)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print(simulate(int(sys.argv[1]), CONFIGS[sys.argv[2]], verbose=True))
    else:
        for name, lv in CONFIGS.items():
            for T in [13, 14, 16, 18, 20, 24, 30, 36, 43]:
                r = simulate(T, lv)
                print(f"config={name} T={T}: {r}")

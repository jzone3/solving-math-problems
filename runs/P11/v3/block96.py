#!/usr/bin/env python3
"""Exhaustive 4-block ansatz search for a PROPER CW(96,36).

Ansatz: h(x) = sum_{i=0}^{3} eps_i x^{a_i} F_i(x^{4 u_i})  in Z[x]/(x^96 - 1),
where each F_i is a DB first row of CW(24,9), u_i in (Z/24)*, eps_i = ±1,
a_i in Z_96. Every weight-9 CWM on Z_96 is such a block (weight 9 is fully
classified: only CW(24,9) exists among divisors of 96, up to equivalence),
so this exhausts all "sum of four weight-9 CWMs" decompositions of a CW(96,36).

Mod-4 contraction: the signed residue pattern g on Z_4 (g[r] = sum of eps_i
with a_i ≡ r) must have |ĝ(psi)| = 2 for all psi in Z_4-dual. We enumerate the
patterns passing this test, then search (u_i, a_i) exhaustively with an
FFT-flatness test |Ĥ(psi)|^2 = 36 for all psi; float hits are re-verified in
exact integer arithmetic (ternary, weight 36, PACF = 0) and properness checked.

Normalization: block 0 fixed at eps=+1, u=1, a=0 (any solution can be shifted
so a_0 = 0 for one block, and multiplier-normalized so that block's u = 1;
sign flips h -> -h). Runtime ~minutes.
"""
import sys
import numpy as np
from math import gcd
from itertools import product

sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper
from extract_table import load, table

N = 96
D = table(load())
sets24 = D[(24, 9)]["sets"]
US = [u for u in range(1, 24) if gcd(u, 24) == 1]


def block_vec(setPN, u, a):
    P, Nn = setPN
    v = np.zeros(N, dtype=np.int64)
    for x in P:
        v[(4 * u * x + a) % N] += 1
    for x in Nn:
        v[(4 * u * x + a) % N] -= 1
    return v


def main():
    nsets = len(sets24)
    print(f"CW(24,9): status {D[(24,9)]['status']}, {nsets} DB sets; |US|={len(US)}")

    # patterns
    pats = []
    for eps in product([1], [1, -1], [1, -1], [1, -1]):
        for res in product([0], range(4), range(4), range(4)):
            g = np.zeros(4)
            for e, r in zip(eps, res):
                g[r] += e
            if np.allclose(np.abs(np.fft.fft(g)), 2.0, atol=1e-9):
                pats.append((eps, res))
    print(f"{len(pats)} residue/sign patterns pass the mod-4 test")

    # precompute vectors and FFTs for every (set, u, a-residue-class shift)
    # index blocks by (si, u, a) lazily via base FFT and twiddle
    base = {}   # (si,u) -> rfft of block_vec(set,u,0)
    vecs = {}   # (si,u) -> time-domain at a=0
    for si in range(nsets):
        for u in US:
            v = block_vec(sets24[si], u, 0)
            vecs[(si, u)] = v
            base[(si, u)] = np.fft.rfft(v.astype(np.float64))
    freqs = np.arange(N // 2 + 1)
    tw = np.exp(-2j * np.pi * np.outer(np.arange(N), freqs) / N)  # shift twiddles

    def bfft(si, u, a):
        return base[(si, u)] * tw[a]

    hits, tried = [], 0
    for eps, res in pats:
        for si0 in range(nsets):
            B0 = eps[0] * bfft(si0, 1, 0)
            for si1 in range(nsets):
                for u1 in US:
                    for a1 in range(res[1], N, 4):
                        B01 = B0 + eps[1] * bfft(si1, u1, a1)
                        for si2 in range(nsets):
                            for u2 in US:
                                # vectorize over a2, and inner over (si3,u3,a3)
                                for a2 in range(res[2], N, 4):
                                    S = B01 + eps[2] * bfft(si2, u2, a2)
                                    for si3 in range(nsets):
                                        for u3 in US:
                                            # all a3 at once
                                            T = S[None, :] + eps[3] * (
                                                base[(si3, u3)][None, :]
                                                * tw[res[3]::4][:, :])
                                            tried += T.shape[0]
                                            m = np.abs(np.abs(T) ** 2 - 36.0).max(axis=1)
                                            for idx in np.where(m < 1e-6)[0]:
                                                a3 = res[3] + 4 * idx
                                                h = (eps[0] * np.roll(vecs[(si0, 1)], 0)
                                                     + eps[1] * np.roll(vecs[(si1, u1)], a1)
                                                     + eps[2] * np.roll(vecs[(si2, u2)], a2)
                                                     + eps[3] * np.roll(vecs[(si3, u3)], a3))
                                                if np.abs(h).max() > 1:
                                                    continue
                                                P = [int(i) for i in np.where(h == 1)[0]]
                                                Nn = [int(i) for i in np.where(h == -1)[0]]
                                                if len(P) + len(Nn) != 36:
                                                    continue
                                                check(N, 36, P, Nn, proper=False)
                                                pr = is_proper(N, P, Nn)
                                                hits.append((eps, res, (si0, si1, si2, si3),
                                                             (1, u1, u2, u3),
                                                             (0, a1, a2, a3), pr, P, Nn))
                                                print("HIT", hits[-1][:6])
        print(f"pattern {eps} {res} done, cumulative tried={tried}, hits={len(hits)}")
    print(f"TOTAL tried {tried}, hits {len(hits)}, proper hits "
          f"{sum(1 for h in hits if h[5])}")
    return hits


if __name__ == "__main__":
    main()

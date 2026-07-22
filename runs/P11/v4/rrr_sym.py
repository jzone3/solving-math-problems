#!/usr/bin/env python3
"""Multiplier-symmetric batched RRR for CW(n,k).

Restrict to sequences fixed by the multiplier i -> t*i (mod n), t in Z_n^*:
a_i = x_{orbit(i)} where orbits are the cosets of <t> acting on Z_n.
Most known CWM witnesses at composite n are fixed by some multiplier, so this
projection ("symmetry pruning") shrinks the search space from 3^n to 3^m with
m = #orbits, while the flat-spectrum constraint is evaluated on the full
length-n expansion.

P_B: per-orbit rounding to nearest of {-1,0,+1} (weight handled by DC bin).
P_A: flat power spectrum |F_j| = s, DC = +s, then orbit-average back.
RRR: x += beta*(P_A(2 P_B(x) - x) - P_B(x)) on batched replicas.

Usage: rrr_sym.py n s t [seconds] [R] [seed]
Prints SOLUTION vec=... on success (exact integer verification).
"""
import sys, time
import numpy as np

def orbits_of(n, t):
    seen = [False]*n
    orb = [0]*n
    reps = []
    for i in range(n):
        if not seen[i]:
            o = len(reps); reps.append(i)
            j = i
            while not seen[j]:
                seen[j] = True; orb[j] = o
                j = (j*t) % n
    return np.array(orb), len(reps)

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2]); t = int(sys.argv[3])
    secs = float(sys.argv[4]) if len(sys.argv) > 4 else 300.0
    R = int(sys.argv[5]) if len(sys.argv) > 5 else 64
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 12345
    k = s*s
    if np.gcd(t, n) != 1:
        print(f"SKIP t={t} not a unit mod {n}"); return 3
    orb, m = orbits_of(n, t)
    sizes = np.bincount(orb).astype(float)         # orbit sizes, length m
    rng = np.random.default_rng(seed)

    X = rng.normal(0, 1, (R, m))
    betas = rng.uniform(0.3, 0.9, (R, 1))
    stall = np.zeros(R, dtype=int); bestE_rep = np.full(R, 1 << 60, dtype=np.int64)
    bestE = None
    t0 = time.time(); it = 0; restarts = R

    def expand(Z):           # (R,m) -> (R,n)
        return Z[:, orb]
    def orbit_avg(Ze):       # (R,n) -> (R,m)
        out = np.zeros((Ze.shape[0], m))
        np.add.at(out.T, orb, Ze.T)   # sum per orbit
        return out / sizes

    while time.time() - t0 < secs:
        B = np.clip(np.rint(X), -1, 1)             # P_B in orbit space
        Ye = expand(2*B - X)
        F = np.fft.rfft(Ye, axis=1)
        mag = np.abs(F)
        Ph = np.where(mag > 1e-12, F/np.maximum(mag, 1e-12), 1.0)
        F2 = Ph * s
        F2[:, 0] = s
        if n % 2 == 0:
            F2[:, -1] = np.where(F[:, -1].real >= 0, s, -s)
        PA = orbit_avg(np.fft.irfft(F2, n, axis=1))
        X = X + betas*(PA - B)
        it += 1
        if it % 20 == 0:
            Be = expand(B)
            wt = np.sum(Be*Be, axis=1)
            r = np.fft.irfft(np.abs(np.fft.rfft(Be, axis=1))**2, n, axis=1)
            ri = np.rint(r).astype(np.int64)
            E = np.sum(ri[:, 1:]**2, axis=1) + (wt.astype(np.int64) - k)**2
            imp = E < bestE_rep
            stall = np.where(imp, 0, stall + 1)
            bestE_rep = np.minimum(bestE_rep, E)
            emin = int(E.min())
            if bestE is None or emin < bestE:
                bestE = emin
                j = int(np.argmin(E))
                vec = ''.join('+' if v > 0.5 else ('-' if v < -0.5 else '0') for v in Be[j])
                print(f"BEST n={n} s={s} t={t} m={m} E={bestE} it={it} restarts={restarts} tm={time.time()-t0:.0f}s vec={vec}", flush=True)
                if bestE == 0:
                    print(f"SOLUTION n={n} k={k} t={t} vec={vec}", flush=True)
                    return 0
            dead = stall > 1500
            nd = int(dead.sum())
            if nd:
                X[dead] = rng.normal(0, 1, (nd, m))
                betas[dead] = rng.uniform(0.3, 0.9, (nd, 1))
                stall[dead] = 0; bestE_rep[dead] = 1 << 60
                restarts += nd
    print(f"DONE n={n} s={s} t={t} m={m} bestE={bestE} it={it} restarts={restarts}", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Batched RRR / difference-map for CW(n,k): R replicas vectorized with numpy.

Same algorithm as rrr.py but runs R independent replicas per iteration
(rows of a matrix), each with its own beta; stalled replicas are reseeded.

Usage: rrr_batch.py n s [seconds] [R] [seed]
"""
import sys, time
import numpy as np

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
    R = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 12345
    k = s*s; npos = (k+s)//2; nneg = (k-s)//2
    rng = np.random.default_rng(seed)

    X = rng.normal(0, 1, (R, n))
    betas = rng.uniform(0.3, 0.9, (R, 1))
    stall = np.zeros(R, dtype=int)
    bestE_rep = np.full(R, 1 << 60, dtype=np.int64)
    bestE = None
    t0 = time.time(); it = 0; restarts = R

    rows = np.arange(R)[:, None]
    while time.time() - t0 < secs:
        # P_B: nearest ternary with fixed composition, per row
        idx = np.argsort(X, axis=1)
        B = np.zeros((R, n))
        B[rows, idx[:, -npos:]] = 1.0
        B[rows, idx[:, :nneg]] = -1.0
        # P_A on 2B - X
        Y = 2*B - X
        F = np.fft.rfft(Y, axis=1)
        mag = np.abs(F)
        Ph = np.where(mag > 1e-12, F/np.maximum(mag, 1e-12), 1.0)
        F2 = Ph * s
        F2[:, 0] = s
        if n % 2 == 0:
            F2[:, -1] = np.where(F[:, -1].real >= 0, s, -s)
        PA = np.fft.irfft(F2, n, axis=1)
        X = X + betas*(PA - B)
        it += 1
        if it % 20 == 0:
            FB = np.fft.rfft(B, axis=1)
            # exact integer energy per row via autocorrelation
            r = np.fft.irfft(np.abs(np.fft.rfft(B, axis=1))**2, n, axis=1)
            ri = np.rint(r).astype(np.int64)
            E = np.sum(ri[:, 1:]**2, axis=1)
            imp = E < bestE_rep
            stall = np.where(imp, 0, stall + 1)
            bestE_rep = np.minimum(bestE_rep, E)
            emin = int(E.min())
            if bestE is None or emin < bestE:
                bestE = emin
                j = int(np.argmin(E))
                vec = ''.join('+' if v > 0.5 else ('-' if v < -0.5 else '0') for v in B[j])
                print(f"BEST n={n} s={s} E={bestE} it={it} restarts={restarts} t={time.time()-t0:.0f}s vec={vec}", flush=True)
                if bestE == 0:
                    print(f"SOLUTION n={n} k={k} vec={vec}", flush=True)
                    return 0
            # reseed stalled replicas (~ 60k iterations without improvement)
            dead = stall > 3000
            nd = int(dead.sum())
            if nd:
                X[dead] = rng.normal(0, 1, (nd, n))
                betas[dead] = rng.uniform(0.3, 0.9, (nd, 1))
                stall[dead] = 0
                bestE_rep[dead] = 1 << 60
                restarts += nd
    print(f"DONE n={n} s={s} bestE={bestE} it={it} restarts={restarts} (replica-iters={it*R})", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

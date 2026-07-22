#!/usr/bin/env python3
"""V4 Fourier-side attack: RRR / difference-map (Elser) for CW(n,k).

Constraint sets in R^n:
  A = { x : |FFT(x)_j| = sqrt(k) for all j }   (flat power spectrum, DC = +s)
  B = { ternary vectors with exactly n_+ ones and n_- minus-ones }
A CW(n,k) first row is exactly a point in A ∩ B.

P_A: keep FFT phases, set magnitudes to sqrt(k) (DC bin set to +s, real).
P_B: componentwise nearest ternary with the fixed composition (via sorting).

RRR iteration: x <- x + beta*( P_A(2*P_B(x) - x) - P_B(x) ).
On (near-)fixed points P_B(x) is checked exactly (integer autocorrelation).

Usage: rrr.py n s [seconds] [beta] [seed]   (beta=0 -> random per restart)
"""
import sys, time
import numpy as np

def project_B(x, npos, nneg):
    n = len(x)
    b = np.zeros(n)
    # gain from making entry +1 is ~ (x_i - 0.5)-ish; use simple ranking:
    # choose npos largest as +1, nneg smallest as -1 (greedy nearest w/ counts)
    idx = np.argsort(x)
    b[idx[-npos:]] = 1.0
    b[idx[:nneg]] = -1.0
    return b

def project_A(x, s):
    n = len(x)
    F = np.fft.rfft(x)
    mag = np.abs(F)
    ph = np.where(mag > 1e-12, F/np.maximum(mag, 1e-12), 1.0)
    tgt = np.full_like(mag, s)
    tgt[0] = s
    F2 = ph * tgt
    F2[0] = s  # DC real, = +s
    if n % 2 == 0:
        F2[-1] = s * np.sign(F[-1].real if abs(F[-1].real) > 1e-12 else 1.0)
    return np.fft.irfft(F2, n)

def energy(b):
    n = len(b)
    F = np.fft.fft(b)
    P = (F*np.conj(F)).real
    k = int(round(np.sum(b*b)))
    # exact integer check via autocorrelation
    r = np.round(np.fft.ifft(np.abs(np.fft.fft(b))**2).real).astype(int)
    return int(np.sum(r[1:]**2))

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
    beta = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 12345
    k = s*s; npos = (k+s)//2; nneg = (k-s)//2
    rng = np.random.default_rng(seed)
    t0 = time.time()
    bestE = None
    it = 0; restarts = 0
    x = None
    while time.time() - t0 < secs:
        if x is None:
            x = rng.normal(0, 1, n); restarts += 1; stall = 0
            cur_beta = rng.uniform(0.3, 0.9) if beta == 0 else beta
        b = project_B(x, npos, nneg)
        y = project_A(2*b - x, s)
        x = x + cur_beta*(y - b)
        it += 1
        if it % 25 == 0:
            E = energy(b)
            if bestE is None or E < bestE:
                bestE = E; stall = 0
                vec = ''.join('+' if v > 0.5 else ('-' if v < -0.5 else '0') for v in b)
                print(f"BEST n={n} s={s} E={E} it={it} restarts={restarts} t={time.time()-t0:.0f}s vec={vec}", flush=True)
                if E == 0:
                    print(f"SOLUTION n={n} k={k} vec={vec}", flush=True)
                    return 0
            else:
                stall += 1
            if stall > 4000:   # ~100k iters without improvement -> restart
                x = None
    print(f"DONE n={n} s={s} bestE={bestE} it={it} restarts={restarts}", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

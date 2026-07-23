"""Round 7: relaxation-guided hybrid attack.

Phase 1 (locate): for every connected pattern H with |H| <= 8, omega >= 3, and H not
complete multipartite, maximize f_H over the simplex (blowup relaxation) and rank by
tightness. Keep the top-K tightest patterns (f closest to 0 from below).

Phase 2 (attack): for each flagged pattern, round the optimal weights to integer
blowups at N in {24, 36, 48}, then exhaustively scan all 1-flips and sample
2/3-flips plus a short plateau walk around each rounded blowup — the regime where
the continuous certificate does not apply (finite N + integer rounding).

Usage: python3 hybrid.py <npat> <res> <mod> [topk]
"""
import sys, subprocess, itertools
import numpy as np
from core import max_clique, score
from blowup import g6_to_adj, maximize, f_and_grad

def is_complete_multipartite(A):
    n = A.shape[0]
    comp = 1 - A - np.eye(n)
    # complete multipartite iff complement is disjoint union of cliques:
    seen = np.zeros(n, bool)
    for i in range(n):
        if seen[i]:
            continue
        grp = np.nonzero(comp[i] + np.eye(n)[i])[0]
        for a in grp:
            for b in grp:
                if a != b and not comp[a, b]:
                    return False
        seen[grp] = True
    return True

def opt_x(A, coef, rng, restarts=16, iters=600):
    n = A.shape[0]
    bestf, bestx = -1e9, None
    for r in range(restarts):
        x = rng.dirichlet(np.ones(n)) if r else np.ones(n) / n
        lr = 0.05
        for t in range(iters):
            f, g = f_and_grad(A, x, coef)
            g = g - g.mean()
            x = np.maximum(x + lr * g, 0)
            s = x.sum()
            if s < 1e-12:
                break
            x /= s
        f, _ = f_and_grad(A, x, coef)
        if f > bestf:
            bestf, bestx = f, x.copy()
    return bestf, bestx

def integer_blowup(A, x, N):
    n = A.shape[0]
    sizes = np.maximum(np.round(x * N).astype(int), 0)
    idx = [i for i in range(n) if sizes[i] > 0]
    offs, s = {}, 0
    for i in idx:
        offs[i] = (s, s + sizes[i]); s += sizes[i]
    B = np.zeros((s, s))
    for i in idx:
        for j in idx:
            if i < j and A[i, j]:
                B[offs[i][0]:offs[i][1], offs[j][0]:offs[j][1]] = 1
                B[offs[j][0]:offs[j][1], offs[i][0]:offs[i][1]] = 1
    return B

def attack(B, rng, name, best_seen):
    n = B.shape[0]
    if n < 4:
        return
    s0, w0 = score(B)
    if s0 is None:
        return
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    best = s0
    # exhaustive 1-flips
    for (i, j) in pairs:
        B[i, j] = B[j, i] = 1 - B[i, j]
        s, _ = score(B)
        if s is not None and s > best:
            best = s
        B[i, j] = B[j, i] = 1 - B[i, j]
    # sampled 2/3-flips
    for k, samples in ((2, 1500), (3, 1500)):
        for _ in range(samples):
            sel = rng.choice(len(pairs), k, replace=False)
            for t in sel:
                i, j = pairs[t]; B[i, j] = B[j, i] = 1 - B[i, j]
            s, _ = score(B)
            if s is not None and s > best:
                best = s
            for t in sel:
                i, j = pairs[t]; B[i, j] = B[j, i] = 1 - B[i, j]
    tag = " ***POSITIVE***" if best > 1e-9 else ""
    print(f"ATTACK {name} n={n} base={s0:+.5f} bestflip={best:+.5f}{tag}", flush=True)
    if best > best_seen[0]:
        best_seen[0] = best

def run(npat, res, mod, topk=40):
    rng = np.random.default_rng(res + 100)
    out = subprocess.run(["nauty-geng", "-cq", str(npat), f"{res}/{mod}"],
                         capture_output=True).stdout.splitlines()
    flagged = []
    for ln in out:
        A = g6_to_adj(ln.strip(), npat)
        w = max_clique(A)
        if w < 3 or w >= npat or is_complete_multipartite(A):
            continue
        coef = 1 - 1 / w
        f, x = opt_x(A, coef, rng, restarts=6, iters=300)
        supp = int((x > 1e-4).sum())
        flagged.append((f, ln.strip().decode(), x, w, supp))
    flagged.sort(key=lambda t: -t[0])
    full = [t for t in flagged if t[4] == npat]
    full.sort(key=lambda t: -t[0])
    print(f"pattern n={npat} part {res}/{mod}: {len(flagged)} non-multipartite patterns; "
          f"tightest f = {[round(t[0],6) for t in flagged[:5]]}; "
          f"tightest FULL-SUPPORT f = {[(t[1], round(t[0],6)) for t in full[:5]]}", flush=True)
    best_seen = [-1e9]
    targets = flagged[:topk] + full[:topk]
    seen = set()
    for f, g6, x, w, supp in targets:
        if g6 in seen:
            continue
        seen.add(g6)
        A = g6_to_adj(g6.encode(), npat)
        del f
        # refine x harder
        f2, x2 = opt_x(A, 1 - 1 / w, rng, restarts=16, iters=800)
        for N in (24, 36, 48):
            B = integer_blowup(A, x2, N)
            attack(B, rng, f"{g6} supp={supp} f={f2:+.6f} N={N}", best_seen)
    print(f"HYBRID SUMMARY n={npat} {res}/{mod}: best over attacks = {best_seen[0]:+.6f}", flush=True)

if __name__ == "__main__":
    npat = int(sys.argv[1]); res = int(sys.argv[2]); mod = int(sys.argv[3])
    topk = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    run(npat, res, mod, topk)

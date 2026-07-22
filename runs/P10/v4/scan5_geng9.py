"""V4 escalation: G v K_r and G v E_r for ALL connected graphs G on 9 vertices
(nauty-geng, 261080 graphs), r = 1..40. Numeric (float) deficits; any deficit
< 1e-6 that is not numerically zero gets logged for exact recheck.
"""
import subprocess, sys, time
import numpy as np

t0 = time.time()
worst = (1e18, None)
suspects = []
cnt = 0

proc = subprocess.Popen(["nauty-geng", "-q", "-c", "9"], stdout=subprocess.PIPE, text=True)

def g6_bits(s):
    # decode graph6 for n<63
    data = [ord(ch) - 63 for ch in s]
    n = data[0]
    bits = []
    for x in data[1:]:
        bits += [(x >> (5 - i)) & 1 for i in range(6)]
    A = np.zeros((n, n))
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]
            k += 1
    return A

R = 40
tvecK, tvecE = {}, {}
for r in range(1, R + 1):
    pass

for line in proc.stdout:
    g6 = line.strip()
    if not g6:
        continue
    A = g6_bits(g6)
    n = A.shape[0]
    m = int(A.sum()) // 2
    L = np.diag(A.sum(1)) - A
    e = np.sort(np.linalg.eigvalsh(L))[::-1]  # includes one ~0
    for r in range(1, R + 1):
        # G v K_r
        eigs = np.sort(np.concatenate([e[:-1] + r, np.full(r - 1, n + r, float),
                                       [n + r, 0.0]]))[::-1]
        mm = m + r * (r - 1) // 2 + n * r
        t = np.arange(1, n + r + 1)
        d = mm + t * (t + 1) / 2.0 - np.cumsum(eigs)
        dm = d.min()
        if dm < worst[0]:
            worst = (dm, f"{g6}vK{r}")
        if dm < -1e-6:
            suspects.append((dm, g6, r, "K"))
            print(f"suspect {g6} vK{r} d={dm}", flush=True)
        # G v E_r
        eigs = np.sort(np.concatenate([e[:-1] + r, np.full(r - 1, n, float),
                                       [n + r, 0.0]]))[::-1]
        mm = m + n * r
        d = mm + t * (t + 1) / 2.0 - np.cumsum(eigs)
        dm = d.min()
        if dm < worst[0]:
            worst = (dm, f"{g6}vE{r}")
        if dm < -1e-6:
            suspects.append((dm, g6, r, "E"))
            print(f"suspect {g6} vE{r} d={dm}", flush=True)
    cnt += 1
    if cnt % 20000 == 0:
        print(f"{cnt} graphs {time.time()-t0:.0f}s worst={worst}", flush=True)

print(f"DONE {cnt} graphs x {2*R} joins, {time.time()-t0:.0f}s")
print(f"WORST deficit {worst}")
print(f"suspects: {len(suspects)}")

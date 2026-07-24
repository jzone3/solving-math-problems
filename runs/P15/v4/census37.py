import numpy as np
import emitcore, emit33, emit34, emit35, emit36, emit37

congs, tails = emit37.emit37()
prev = (emitcore.emit() + emit33.emit() + list(emit34.emit34()[0])
        + list(emit35.emit()[0]) + list(emit36.emit36()[0]))
for label, N in (("w11", 2**6 * 3**5 * 5**2 * 7 * 11 * 17),
                 ("w13", 2**6 * 3**5 * 5**2 * 7 * 13 * 17)):
    base = np.zeros(N, dtype=bool)
    for r, n in prev:
        if N % n == 0:
            base[r % n::n] = True
    cov = base.copy()
    dropped = 0.0
    for r, n in congs + tails:
        if N % n == 0:
            cov[r % n::n] = True
        else:
            dropped += 1.0 / n
    idx = np.arange(N)
    B = idx % 24 == 13
    unc = idx[B & ~cov]
    print(f"{label}: N={N} uncovered {unc.size}/{B.sum()} "
          f"dropped {dropped:.2e}")
    if unc.size:
        from collections import Counter
        print("  by mod 17:", sorted(Counter(unc % 17).items()))

#!/usr/bin/env python3
"""P09 round 10: analytic scan over ALL feasible SRG parameter tuples, v <= VMAX.

For an SRG(v,k,l,u): lambda_1 = k, lambda_2 = r, 2m = v*k, and the
Delsarte/ratio bound gives omega <= W := floor(1 + k/(-s)) where s < 0 is
the smallest eigenvalue.  rhs = 2m(1-1/omega) is increasing in omega, so
omega <= W implies rhs <= v*k*(1-1/W).  Hence

    gapW := k^2 + r^2 - v*k*(1-1/W) > 0

would FORCE a Bollobas-Nikiforov violation for every SRG realizing the
tuple (actual gap >= actual s - rhs >= ... >= gapW is an upper bound on the
true gap, so gapW <= 0 certifies no SRG with that tuple can violate).

Enumeration by integer eigenvalues (r >= 0, s <= -1) and u >= 1:
    k = u - r*s,  l = u + r + s,  v = 1 + k + k*(k-l-1)/u  (must divide),
plus the conference-graph case v = 4u+1, k = 2u, l = u-1 (r,s irrational).
All arithmetic exact except the conference case (float sqrt, noted).
"""
import math

VMAX = 10000
best = []
count = 0

# integer-eigenvalue SRGs.  Note k - l - 1 = (r+1)(ms-1), independent of u,
# so u must divide k*(r+1)(ms-1) === r*ms*(r+1)*(ms-1) (mod u): u | P below.
# r = 0 (complete multipartite, the known equality family) and ms = 1
# (v = k+1, complete graph) are excluded a priori.
def divisors(P):
    ds = []
    i = 1
    while i * i <= P:
        if P % i == 0:
            ds.append(i)
            if i != P // i:
                ds.append(P // i)
        i += 1
    return ds

for r in range(1, VMAX + 1):
    if r * 2 > VMAX:
        break
    for ms in range(2, VMAX + 1):          # ms = -s
        if r * ms > VMAX:
            break
        P = r * ms * (r + 1) * (ms - 1)
        for u in sorted(divisors(P)):
            k = u + r * ms
            if k >= VMAX:
                break
            l = u + r - ms
            if l < 0 or l >= k:
                continue
            num = k * (k - l - 1)
            if num % u:
                continue
            v = 1 + k + num // u
            if v > VMAX or v < k + 2:
                continue
            # multiplicity integrality
            # g = ((v-1)(-s) - k)/(r - s) = ((v-1)ms - k)/(r + ms)
            fg_num = (v - 1) * ms - k
            if fg_num < 0 or fg_num % (r + ms):
                continue
            g = fg_num // (r + ms)
            f = v - 1 - g
            if f < 0:
                continue
            W = 1 + k // ms  # floor(1 + k/(-s)), Delsarte clique bound
            if W < 2:
                continue
            count += 1
            # gapW = k^2 + r^2 - v*k*(W-1)/W, exact via integers scaled by W
            gapW_num = (k * k + r * r) * W - v * k * (W - 1)   # sign of gapW
            gapW = gapW_num / W
            if gapW > -100:
                best.append((gapW, v, k, l, u, r, -ms, W))

# conference graphs: v = 4u+1 (v must be sum of two squares etc.; we scan all)
conf = 0
for u in range(1, (VMAX - 1) // 4 + 1):
    v = 4 * u + 1
    k = 2 * u
    rr = (-1 + math.sqrt(v)) / 2.0
    ss = (1 + math.sqrt(v)) / 2.0   # = -s
    W = int(1 + k / ss)
    if W < 2:
        continue
    conf += 1
    gapW = k * k + rr * rr - v * k * (1 - 1.0 / W)
    if gapW > -100:
        best.append((gapW, v, k, u - 1, u, rr, -ss, W))

best.sort(key=lambda b: -b[0])
print(f"integer-eigenvalue feasible tuples: {count}, conference tuples: {conf}")
print("top gapW = k^2+r^2 - vk(1-1/W)  [violation forced iff > 0]:")
for b in best[:25]:
    print(f"  gapW={b[0]:+.6f}  v={b[1]} k={b[2]} l={b[3]} u={b[4]} r={b[5]} s={b[6]} W={b[7]}")
viol = [b for b in best if b[0] > 1e-9]
print(f"tuples forcing violation: {len(viol)}")

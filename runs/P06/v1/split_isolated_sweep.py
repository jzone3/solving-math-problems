"""
P06/V1: 3-parameter family generalizing BOTH near-miss families:
  G(k,i,t) = CS(k+i, k) U t*K1  (k dominating clique, i independent, t isolated).
  k=1: star + isolated;  i=0, t=q-2: the exact equality family K_q U (q-2)K1.
Closed-form float sweep (fast), refine near maxima; positives re-checked exactly.
"""
import math

def score(k, i, t):
    n = k + i + t
    dk = k + i - 1          # degree of dominating vertices
    s1 = k * dk + i * k
    s2 = k * dk * dk + i * k * k
    dev2 = (s2 + s1) / n - (s1 / n) ** 2
    R = (k * (k - 1) / 2) / dk + (k * i) / math.sqrt(k * dk) if dk > 0 else 0.0
    return math.sqrt(max(dev2, 0.0)) - R

best = []
for k in range(1, 400):
    for i in range(0, 400):
        if k + i < 2:
            continue
        # optimal t is near 2*s1^2/(s1+s2) - k - i; scan a window
        dk = k + i - 1
        s1 = k * dk + i * k
        s2 = k * dk * dk + i * k * k
        tstar = 2 * s1 * s1 / (s1 + s2) - (k + i)
        for t in range(max(0, int(tstar) - 3), int(tstar) + 4):
            best.append((score(k, i, t), k, i, t))
best.sort(reverse=True)
print("top 12 of CS(k+i,k) U tK1 sweep (k,i<400):")
for s, k, i, t in best[:12]:
    print(f"  {s:+.10f}  k={k} i={i} t={t}")

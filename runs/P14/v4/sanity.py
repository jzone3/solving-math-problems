#!/usr/bin/env python3
"""Machine-check the divisibility/counting necessary conditions for the 4 P14 instances."""
INSTANCES = [
    (14, 18, 7, 1, 9, 7, 4),
    (12, 15, 6, 2, 10, 8, 6),
    (12, 20, 4, 3, 10, 6, 4),
    (14, 28, 8, 3, 14, 7, 6),
]
for (V, B, r1, r2, R, K, L) in INSTANCES:
    assert R == r1 + 2 * r2, (V, B)
    assert V * R == B * K, (V, B)
    # total pair coverage: sum over blocks of (K^2 - sum m^2)/2 == L*C(V,2)
    total_sq = V * r1 + 4 * V * r2  # sum over all cells of m^2
    pairs = (B * K * K - total_sq) // 2
    assert (B * K * K - total_sq) % 2 == 0, (V, B)
    assert pairs == L * V * (V - 1) // 2, (V, B, pairs, L * V * (V - 1) // 2)
    print(f"BTD({V},{B};{r1},{r2},{R};{K},{L}): VR=BK={V*R}, pair count {pairs} == L*C(V,2) OK")
print("ALL NECESSARY-CONDITION CHECKS PASS")

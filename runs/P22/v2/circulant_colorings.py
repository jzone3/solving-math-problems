#!/usr/bin/env python3
"""Exhaustive check of all translation-invariant (circulant) 2-colorings of
E(G127). Such a coloring assigns a color to each difference class
{c, 127-c} (c a cubic residue) -- 21 classes -- so there are 2^21 of them.
For each, test whether any monochromatic triangle exists (checking one
representative per translation orbit suffices). If none of the 2^21 avoid
mono triangles, then no counterexample coloring is circulant.
"""
import itertools

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
classes = sorted({min(c, p - c) for c in C})
assert len(classes) == 21
cls_idx = {c: i for i, c in enumerate(classes)}

def edge_class(u, v):
    d = (u - v) % p
    d = min(d, p - d)
    return cls_idx[d]

# triangle orbit representatives: triangles containing vertex 0
Cset = set(C)
reps = []
for i, c1 in enumerate(C):
    for c2 in C[i + 1:]:
        if (c2 - c1) % p in Cset:
            reps.append((0, c1, c2))
# each triangle orbit under translations (size 127, free action since p prime)
# contains exactly 3 triangles with vertex 0 (one per vertex), so:
assert len(reps) * 127 // 3 == 9779, len(reps)

tri_masks = []
for (u, v, w) in reps:
    a, b, c = edge_class(u, v), edge_class(u, w), edge_class(v, w)
    tri_masks.append((1 << a) | (1 << b) | (1 << c))
tri_masks = sorted(set(tri_masks) | set(tri_masks))  # dedupe not needed for soundness

good = []
FULL = (1 << 21) - 1
for m in range(1 << 21):
    ok = True
    for t in tri_masks:
        x = m & t
        if x == t or x == 0:  # all red or all blue
            ok = False
            break
    if ok:
        good.append(m)
print(f"translation-invariant colorings avoiding mono triangles: {len(good)}")
if good:
    print("WITNESS MASKS:", good[:10])
else:
    print("NONE: no circulant 2-coloring of E(G127) avoids a monochromatic triangle")

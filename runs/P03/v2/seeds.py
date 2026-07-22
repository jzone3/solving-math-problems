"""Weighted counterexample seeds to the Edmonds-Giles conjecture,
reconstructed from the figures in Feofiloff's survey
(https://www.ime.usp.br/~pf/dijoins/download/woodall-conjecture-en.pdf):

- D1: Schrijver 1980 (Figure 6): 12 vertices, 21 arcs (9 weight-1, 12 weight-0),
  tau(D1,u1)=2, nu(D1,u1)=1.
- D2: Cornuejols-Guenin 2002 (Figure 9, left drawing): 14 vertices, 25 arcs
  (11 weight-1, 14 weight-0), tau=2, nu=1.

Both were extracted programmatically from the PDF vector drawings (line
segments + arrowhead half-segments for direction, dash pattern for weight 0)
and are machine-verified by verify_seeds.py.
"""

# ---------------- Schrijver D1 ----------------
# Vertices: outer hexagon O1..O6 and inner hexagon I1..I6 in the drawing.
# index:      0   1   2   3   4   5   6   7   8   9  10  11
# name:      O1  O2  O3  O4  O5  O6  I1  I2  I3  I4  I5  I6
O1, O2, O3, O4, O5, O6, I1, I2, I3, I4, I5, I6 = range(12)

# solid = weight 1; labels a..i from Figure 6/7 (special joins check out)
D1_solid = [
    (O1, O2),  # a
    (O1, I6),  # b
    (I5, I6),  # c
    (O5, O6),  # d
    (O5, I4),  # e
    (I3, I4),  # f
    (O3, O4),  # g
    (O3, I2),  # h
    (I1, I2),  # i
]
D1_null = [
    (O1, I1), (O1, O6), (O6, I6),
    (O3, O2), (O2, I2), (I3, I2),
    (O5, O4), (O4, I4), (I5, I4),
    (I1, I6), (O3, I3), (O5, I5),
]
D1_n = 12
D1_arcs = D1_solid + D1_null
D1_w = [1] * len(D1_solid) + [0] * len(D1_null)
D1_labels = list("abcdefghi")

# ---------------- Cornuejols-Guenin D2 ----------------
# vertex names are the 1..14 labels of Figure 9 (left drawing), minus 1.
def _v(i):
    return i - 1

D2_solid = [(_v(a), _v(b)) for (a, b) in [
    (3, 2), (5, 6), (3, 4), (13, 14), (13, 12), (7, 6),
    (7, 8), (1, 2), (11, 12), (11, 10), (9, 8),
]]
D2_null = [(_v(a), _v(b)) for (a, b) in [
    (3, 10), (13, 4), (10, 2), (3, 5), (4, 6), (14, 8), (14, 6),
    (1, 8), (13, 9), (11, 9), (9, 12), (5, 2), (11, 1), (7, 14),
]]
D2_n = 14
D2_arcs = D2_solid + D2_null
D2_w = [1] * len(D2_solid) + [0] * len(D2_null)

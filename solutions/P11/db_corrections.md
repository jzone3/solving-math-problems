# P11 — La Jolla CWM repository cells settled by this run (V3)

The repository statuses (github.com/dmgordo/circulant-weighing-matrices, cwm.json, keys CW(n,s)
with weight k = s²) track **proper** CWMs. The following DB-"Open" cells are in fact settled:

| DB cell | (n, k) | Verdict | Provenance |
|---|---|---|---|
| CW(96,6) | (96, 36) | **EXISTS (proper)** | Schmidt–Smith JCTA 120 (2013), Thm 6.7/6.8, Cor 6.9 (proper CW(v,36) for all v ≡ 0 mod 48). Explicit witness: `CW96_36_proper.json`, dual-verified (`verify.py`, `verify2.py`). |
| CW(132,9) | (132, 81) | **DOES NOT EXIST** | Arasu–Gordon–Zhang, Crypt. Commun. 13 (2021), Prop 4.2; independently re-verified by orbit exhaust `../../runs/P11/v3/icw132.py` (no ⟨3⟩-fixed ICW_3(44,81)). |
| CW(648,6) | (648, 36) | **DOES NOT EXIST (proper)** | Schmidt–Smith Thm 6.10(c): proper CW(v,36) with v = 2^a·3^b needs an order-16 element; 16 ∤ 648. |
| CW(288,9) | (288, 81) | **DOES NOT EXIST (proper)** | Schmidt–Smith Thm 6.10: for v,k both products of powers of 2 and 3, proper CW(v,k) forces k ∈ {4, 9, 36}; 81 excluded. |
| CW(384,9) | (384, 81) | **DOES NOT EXIST (proper)** | same |
| CW(576,9) | (576, 81) | **DOES NOT EXIST (proper)** | same |
| CW(768,9) | (768, 81) | **DOES NOT EXIST (proper)** | same |
| CW(864,9) | (864, 81) | **DOES NOT EXIST (proper)** | same |

Notes:
- An improper CW(96,36) also exists trivially (pad CW(48,36) by x→x²): `CW96_36.json`.
- Of the six P11 target cells, (96,36) is settled YES (witness), (132,81) settled NO;
  (105,36), (112,36), (117,36), (120,49) match AGZ Table 10 and remain genuinely open —
  see `../../runs/P11/v3/NOTES.md` for the composition-route negative results and the
  ICW-lift / multiplier-orbit CP-SAT searches on them.

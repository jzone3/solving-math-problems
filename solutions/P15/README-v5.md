# P15 / V5 artifacts

**No claim on the open problem (min modulus >= 43; standing record 42, Owens 2014).**

These artifacts document the *automated-search frontier* reached by the V5 run:
machine-generated covering systems with distinct moduli, found fully automatically
(no hand-designed structure) by greedy search over a smooth universe:

- `witness_L15_N259459200.json` — 743 congruences, distinct moduli, min modulus **15**,
  lcm 2^7·3^4·5^2·7·11·13. To our knowledge no published computational (non-hand)
  optimization of the constructive minimum-modulus problem exists; this is a baseline
  datapoint, ~1/3 of the hand record.
- `verify.py` — standalone dependency-free verifier (direct sweep over the lcm):
  `python3 verify.py witness_L15_N259459200.json` → prints PASS.

A second, independently-written CRT-structured verifier (`runs/P15/v5/verify_tree.py`)
also passes on this witness. Search code and full run log: `runs/P15/v5/`.

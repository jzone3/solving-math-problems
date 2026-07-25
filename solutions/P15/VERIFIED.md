# Verified P15 covering systems

These files are explicit covering systems of \(\mathbb Z\) with pairwise
distinct moduli, where every modulus is at least the stated minimum modulus
`m`. Each witness below was checked by three independent exact verifiers:
the CRT-recursive verifier, the exact cell-subtraction verifier, and the
segmented residue-sieve verifier.

Reproduce the table with:

```text
python solutions/P15/verify_all.py
```

Literal runner output:

```text
m | congruence count | v1 | subtract | sieve
--|------------------|----|----------|------
3 | 14 | PASS: 14 congruences, distinct moduli, min modulus = 3 >= 3, cover Z (exit 0) | PASS: covering system, 14 congruences, min modulus 3, peak cells 24 (exit 0) | PASS: sieve cover, 14 congruences, min modulus 3, N=120 (exit 0)
4 | 29 | PASS: 29 congruences, distinct moduli, min modulus = 4 >= 4, cover Z (exit 0) | PASS: covering system, 29 congruences, min modulus 4, peak cells 336 (exit 0) | PASS: sieve cover, 29 congruences, min modulus 4, N=2520 (exit 0)
5 | 46 | PASS: 46 congruences, distinct moduli, min modulus = 5 >= 5, cover Z (exit 0) | PASS: covering system, 46 congruences, min modulus 5, peak cells 360 (exit 0) | PASS: sieve cover, 46 congruences, min modulus 5, N=10080 (exit 0)
6 | 64 | PASS: 64 congruences, distinct moduli, min modulus = 6 >= 6, cover Z (exit 0) | PASS: covering system, 64 congruences, min modulus 6, peak cells 306 (exit 0) | PASS: sieve cover, 64 congruences, min modulus 6, N=10080 (exit 0)
7 | 80 | PASS: 80 congruences, distinct moduli, min modulus = 7 >= 7, cover Z (exit 0) | PASS: covering system, 80 congruences, min modulus 7, peak cells 9120 (exit 0) | PASS: sieve cover, 80 congruences, min modulus 7, N=332640 (exit 0)
8 | 91 | PASS: 91 congruences, distinct moduli, min modulus = 8 >= 8, cover Z (exit 0) | PASS: covering system, 91 congruences, min modulus 8, peak cells 8928 (exit 0) | PASS: sieve cover, 91 congruences, min modulus 8, N=665280 (exit 0)
9 | 197 | PASS: 197 congruences, distinct moduli, min modulus = 9 >= 9, cover Z (exit 0) | PASS: covering system, 197 congruences, min modulus 9, peak cells 164124 (exit 0) | PASS: sieve cover, 197 congruences, min modulus 9, N=4324320 (exit 0)
10 | 388 | PASS: 388 congruences, distinct moduli, min modulus = 10 >= 10, cover Z (exit 0) | PASS: covering system, 388 congruences, min modulus 10, peak cells 74583 (exit 0) | PASS: sieve cover, 388 congruences, min modulus 10, N=51891840 (exit 0)
11 | 300 | PASS: 300 congruences, distinct moduli, min modulus = 11 >= 11, cover Z (exit 0) | PASS: covering system, 300 congruences, min modulus 11, peak cells 362496 (exit 0) | PASS: sieve cover, 300 congruences, min modulus 11, N=21621600 (exit 0)
12 | 342 | PASS: 342 congruences, distinct moduli, min modulus = 12 >= 12, cover Z (exit 0) | PASS: covering system, 342 congruences, min modulus 12, peak cells 492290 (exit 0) | PASS: sieve cover, 342 congruences, min modulus 12, N=43243200 (exit 0)
13 | 548 | PASS: 548 congruences, distinct moduli, min modulus = 13 >= 13, cover Z (exit 0) | PASS: covering system, 548 congruences, min modulus 13, peak cells 210725 (exit 0) | PASS: sieve cover, 548 congruences, min modulus 13, N=1816214400 (exit 0)
14 | 508 | PASS: 508 congruences, distinct moduli, min modulus = 14 >= 14, cover Z (exit 0) | PASS: covering system, 508 congruences, min modulus 14, peak cells 223121 (exit 0) | PASS: sieve cover, 508 congruences, min modulus 14, N=1816214400 (exit 0)
15 | 473 | PASS: 473 congruences, distinct moduli, min modulus = 15 >= 15, cover Z (exit 0) | PASS: covering system, 473 congruences, min modulus 15, peak cells 3097276 (exit 0) | PASS: sieve cover, 473 congruences, min modulus 15, N=27243216000 (exit 0)
16 | 641 | PASS: 641 congruences, distinct moduli, min modulus = 16 >= 16, cover Z (exit 0) | PASS: covering system, 641 congruences, min modulus 16, peak cells 6925956 (exit 0) | PASS: sieve cover, 641 congruences, min modulus 16, N=27243216000 (exit 0)
```

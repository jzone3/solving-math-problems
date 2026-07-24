# P15 verified explicit witnesses

Generated on the `runs/P15-fusion1` branch using `toolkit/fc_tree2.py`.

Only witnesses that passed **both** independent verifiers are listed below.
The highest verified minimum modulus in this batch is **m = 15**.

## Witness list

| m | factorization / N | congruences | `verify_v1.py` PASS line | `verify_subtract.py` PASS line |
|---|---|---:|---|---|
| 3 | `2^3,3,5` / `120` | 14 | `PASS: 14 congruences, distinct moduli, min modulus = 3 >= 3, cover Z` | `PASS: covering system, 14 congruences, min modulus 3, peak cells 24` |
| 4 | `2^3,3^2,5,7` / `2520` | 29 | `PASS: 29 congruences, distinct moduli, min modulus = 4 >= 4, cover Z` | `PASS: covering system, 29 congruences, min modulus 4, peak cells 336` |
| 5 | `2^5,3^2,5` / `1440` | 46 | `PASS: 46 congruences, distinct moduli, min modulus = 5 >= 5, cover Z` | `PASS: covering system, 46 congruences, min modulus 5, peak cells 360` |
| 6 | `2^4,3^2,5,7` / `5040` | 64 | `PASS: 64 congruences, distinct moduli, min modulus = 6 >= 6, cover Z` | `PASS: covering system, 64 congruences, min modulus 6, peak cells 306` |
| 7 | `2^5,3^3,5,7,11` / `332640` | 80 | `PASS: 80 congruences, distinct moduli, min modulus = 7 >= 7, cover Z` | `PASS: covering system, 80 congruences, min modulus 7, peak cells 9120` |
| 8 | `2^6,3^3,5,7,11` / `665280` | 91 | `PASS: 91 congruences, distinct moduli, min modulus = 8 >= 8, cover Z` | `PASS: covering system, 91 congruences, min modulus 8, peak cells 8928` |
| 9 | `2^5,3^3,5,7,11,13` / `4324320` | 197 | `PASS: 197 congruences, distinct moduli, min modulus = 9 >= 9, cover Z` | `PASS: covering system, 197 congruences, min modulus 9, peak cells 164124` |
| 10 | `2^7,3^4,5,7,11,13` / `51891840` | 388 | `PASS: 388 congruences, distinct moduli, min modulus = 10 >= 10, cover Z` | `PASS: covering system, 388 congruences, min modulus 10, peak cells 74583` |
| 11 | `2^5,3^3,5^2,7,11,13` / `21621600` | 300 | `PASS: 300 congruences, distinct moduli, min modulus = 11 >= 11, cover Z` | `PASS: covering system, 300 congruences, min modulus 11, peak cells 362496` |
| 12 | `2^6,3^3,5^2,7,11,13` / `43243200` | 342 | `PASS: 342 congruences, distinct moduli, min modulus = 12 >= 12, cover Z` | `PASS: covering system, 342 congruences, min modulus 12, peak cells 492290` |
| 13 | `2^7,3^4,5^2,7^2,11,13` / `1816214400` | 548 | `PASS: 548 congruences, distinct moduli, min modulus = 13 >= 13, cover Z` | `PASS: covering system, 548 congruences, min modulus 13, peak cells 210725` |
| 14 | `2^7,3^4,5^2,7^2,11,13` / `1816214400` | 508 | `PASS: 508 congruences, distinct moduli, min modulus = 14 >= 14, cover Z` | `PASS: covering system, 508 congruences, min modulus 14, peak cells 223121` |
| 15 | `2^7,3^5,5^3,7^2,11,13` / `27243216000` | 473 | `PASS: 473 congruences, distinct moduli, min modulus = 15 >= 15, cover Z` | `PASS: covering system, 473 congruences, min modulus 15, peak cells 3097276` |

## Not verified here

The best m=16 greedy witness in this batch passed `verify_v1.py` but failed
`verify_subtract.py` with `FAIL: cell blowup`, so it is not listed as a
verified witness and no `witness_m16.json` was saved.

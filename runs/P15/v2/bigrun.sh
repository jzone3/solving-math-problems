#!/bin/bash
# engine5 big-N ladder
cd "$(dirname "$0")"
N1="2^6,3^4,5^2,7,11,13,17"
N2="2^6,3^4,5^2,7,11,13,17,19"
for T in 10 11 12 13; do
  python3 engine5.py -T $T -N "$N1" --budget 2400 \
    -o covers/e5_T${T}_2.2e9.txt > ilogs/e5_N1_T${T}.log 2>&1
  grep -q SUCCESS ilogs/e5_N1_T${T}.log || break
done
for T in 12 14 16 18; do
  python3 engine5.py -T $T -N "$N2" --sample 40000000 --budget 10800 \
    -o covers/e5_T${T}_4.2e10.txt > ilogs/e5_N2_T${T}.log 2>&1
  grep -q SUCCESS ilogs/e5_N2_T${T}.log || break
done

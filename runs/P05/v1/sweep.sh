#!/bin/bash
cd "$(dirname "$0")"
n=$1; mod=$2
for ((r=0;r<mod;r++)); do
  setsid nohup bash -c "nauty-geng -Cq $n ${r}/${mod} | ./lp 3 > lp${n}_${r}.hits 2> lp${n}_${r}.err" >/dev/null 2>&1 </dev/null &
done

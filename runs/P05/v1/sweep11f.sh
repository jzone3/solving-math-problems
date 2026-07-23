#!/bin/bash
cd "$(dirname "$0")"
for ((r=0;r<8;r++)); do
  setsid nohup bash -c "nauty-geng -Cq 11 ${r}/8 | ./lp2 3 > lp11f_${r}.hits 2> lp11f_${r}.err" >/dev/null 2>&1 </dev/null &
done

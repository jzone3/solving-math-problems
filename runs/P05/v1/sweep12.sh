#!/bin/bash
cd "$(dirname "$0")"
for ((r=0;r<8;r++)); do
  setsid nohup bash -c "nauty-geng -Cq 12 0:22 ${r}/8 | ./lp2 3 > lp12s_${r}.hits 2> lp12s_${r}.err" >/dev/null 2>&1 </dev/null &
done

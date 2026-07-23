#!/bin/bash
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
cd $D
for s in 1 2 4; do
  pkill -f "exhaust_small.py n8e12-$s"
done
sleep 1
rm -f logs/exhaust8_1.log logs/exhaust8_2.log logs/exhaust8_4.log
: > jobs8b.txt
for s in 1 2 4; do
  for k in $(seq 0 9); do
    r=$((s+24*k))
    echo "nauty-geng -c -q 8 8:12 $r/240 | nauty-directg -T 2>/dev/null | python3 $D/exhaust_small.py n8e12r-$r > $D/logs/exhaust8r_$r.log 2>&1" >> jobs8b.txt
  done
done
nohup xargs -a jobs8b.txt -P 7 -I CMD bash -c CMD < /dev/null > logs/exhaust8b_runner.log 2>&1 &
echo launched

#!/bin/bash
# geng res/mod classes are NOT compatible across different mod values, so
# the whole n=8 sweep must use a single mod. Redo everything with mod 240.
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
cd $D
pkill -f "exhaust_small.py n8"
sleep 1
rm -f logs/exhaust8_*.log logs/exhaust8r_*.log
: > jobs8c.txt
for r in $(seq 0 239); do
  echo "nauty-geng -c -q 8 7:12 $r/240 | nauty-directg -T 2>/dev/null | python3 $D/exhaust_small.py n8c-$r > $D/logs/exhaust8c_$r.log 2>&1" >> jobs8c.txt
done
nohup xargs -a jobs8c.txt -P 7 -I CMD bash -c CMD < /dev/null > logs/exhaust8c_runner.log 2>&1 &
echo launched

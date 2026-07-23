#!/bin/bash
cd /home/ubuntu/repos/solving-math-problems/runs/P01/v1
cur=45
while [ $cur -lt 60 ]; do
  next=$((cur+1))
  ./search5 grow < seed/g$cur.txt > seed/g$next.txt 2>> logs/grow.log || { echo "grow failed at $next" >> logs/grow.log; break; }
  hc=$(./fastcount count < seed/g$next.txt)
  echo "n=$next exact hc=$hc $(date -u +%H:%M)" >> logs/grow.log
  cur=$next
done

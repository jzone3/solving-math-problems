#!/bin/bash
# Exact region trades from Parts' 509 inside the three-rotation universe
# (A u omega[15] B u omega[11] C).  The omega[11] copy supplies candidate
# vertices no previous search in this run could reach; any accepted trade is
# a 508.  Anchored kill pattern so this script cannot kill its own shell.
pkill -f '^python3 -u hlns.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
for H in 20 30 45 60; do
  POOL=r3big.pkl START=r3rec.pkl H=$H HOPS=1 TIME=900 BALL=1 SEED=$RANDOM \
    OUT=r3trade_$H.pkl setsid nohup python3 -u hlns.py > r3t$H.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc hlns.py

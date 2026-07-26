#!/bin/bash
# Hitting-set search over the smallest obstructing universe (2581 vertices):
# hyperedge generators (min-conflicts + conflict cover) feeding an append-only
# bank, and IHS workers that solve the bank to optimality each iteration.
pkill -f '^python3 -u hsfull.py'
pkill -f '^python3 -u hypgen.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
for s in 1 2 3 4; do
  POOL=tasym_1.6_1.3.pkl SEED=$s STEPS=2000000 NOISE=0.02 \
    setsid nohup python3 -u hypgen.py > hyp$s.log 2>&1 < /dev/null &
done
for s in 11 12; do
  POOL=tasym_1.6_1.3.pkl BUD=508 SEED=$s \
    setsid nohup python3 -u hsfull.py > hsf$s.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc 'hypgen.py|hsfull.py'

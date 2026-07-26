#!/bin/bash
# Squeeze cycle: alternate cover_mc3 warm restarts (fresh seed + weights) with
# repair_mc endgame trims, always continuing from the best state seen so far.
# usage: squeeze.sh N m state_in workdir threads [mc_secs] [rep_secs]
set -u
N=$1; M=$2; ST=$3; WD=$4; THR=$5; MCS=${6:-1500}; RPS=${7:-300}
mkdir -p "$WD"
cp "$ST" "$WD/cur.state"
seed=1000
while true; do
  seed=$((seed+1))
  OMP_NUM_THREADS=$THR /tmp/cover_mc3w "$N" "$M" "$MCS" "$seed" "$WD/mc.json" 16384 300 "$WD/cur.state" >> "$WD/mc.log" 2>&1
  if [ -f "$WD/mc.json" ]; then echo "SOLVED by mc at seed $seed" >> "$WD/driver.log"; cp "$WD/mc.json" "$WD/SOLVED.json"; exit 0; fi
  [ -f "$WD/mc.json.state" ] && cp "$WD/mc.json.state" "$WD/cur.state"
  for nmin in 30000 15000; do
    seed=$((seed+1))
    /tmp/repair_mc "$WD/cur.state" "$nmin" "$RPS" "$seed" "$WD/rep.json" >> "$WD/rep.log" 2>&1
    if [ -f "$WD/rep.json" ]; then echo "SOLVED by repair at seed $seed" >> "$WD/driver.log"; cp "$WD/rep.json" "$WD/SOLVED.json"; exit 0; fi
    [ -f "$WD/rep.json.state" ] && cp "$WD/rep.json.state" "$WD/cur.state"
  done
  echo "cycle seed=$seed best=$(head -1 "$WD/cur.state" | awk '{print $4}')" >> "$WD/driver.log"
done

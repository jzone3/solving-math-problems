#!/bin/bash
# 6 cores: symmetric-RRR drivers on all six open cells.
# Keeps 2 plain-RRR runs (96,105) alive; kills the other plain runs.
cd "$(dirname "$0")"
pkill -f 'rrr_batch.py 112'; pkill -f 'rrr_batch.py 117'
pkill -f 'rrr_batch.py 120'; pkill -f 'rrr_batch.py 132'
pkill -f 'rrr_batch.py 96 6 18000 64 .* '   # (none)
sleep 1
# kill one of the duplicate 96/105 plain runs if both alive
pids=$(pgrep -f 'rrr_batch.py 96' | tail -n +2); [ -n "$pids" ] && kill $pids
pids=$(pgrep -f 'rrr_batch.py 105' | tail -n +2); [ -n "$pids" ] && kill $pids
nohup python3 sym_driver.py 96  6 > logs/sym_96.log  2>&1 &
nohup python3 sym_driver.py 105 6 > logs/sym_105.log 2>&1 &
nohup python3 sym_driver.py 112 6 > logs/sym_112.log 2>&1 &
nohup python3 sym_driver.py 117 6 > logs/sym_117.log 2>&1 &
nohup python3 sym_driver.py 120 7 > logs/sym_120.log 2>&1 &
nohup python3 sym_driver.py 132 9 > logs/sym_132.log 2>&1 &
echo launched

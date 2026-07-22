#!/bin/bash
# All 8 cores on batched RRR. Two cores first calibrate on known cells (91,104),
# then join the open-cell attack.
cd "$(dirname "$0")"
pkill -f 'rrr.py' ; pkill -f 'rrr_batch.py'
sleep 1
SECS=${1:-18000}
nohup python3 rrr_batch.py 96  6 $SECS 64 $RANDOM > logs/brr_96_a.log  2>&1 &
nohup python3 rrr_batch.py 105 6 $SECS 64 $RANDOM > logs/brr_105_a.log 2>&1 &
nohup python3 rrr_batch.py 112 6 $SECS 64 $RANDOM > logs/brr_112.log   2>&1 &
nohup python3 rrr_batch.py 117 6 $SECS 64 $RANDOM > logs/brr_117.log   2>&1 &
nohup python3 rrr_batch.py 120 7 $SECS 64 $RANDOM > logs/brr_120.log   2>&1 &
nohup python3 rrr_batch.py 132 9 $SECS 64 $RANDOM > logs/brr_132.log   2>&1 &
nohup bash -c "python3 rrr_batch.py 91 6 900 64 $RANDOM > logs/bcalib_91.log 2>&1; python3 rrr_batch.py 96 6 $SECS 64 $RANDOM > logs/brr_96_b.log 2>&1" &
nohup bash -c "python3 rrr_batch.py 104 6 900 64 $RANDOM > logs/bcalib_104.log 2>&1; python3 rrr_batch.py 105 6 $SECS 64 $RANDOM > logs/brr_105_b.log 2>&1" &
echo launched

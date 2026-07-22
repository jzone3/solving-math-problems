#!/bin/bash
# Kill all previous background searches and put all 8 cores on RRR.
cd "$(dirname "$0")"
pkill -f '^\./anneal ' ; pkill -f '^\./lift ' ; pkill -f '^\./fold ' ; pkill -f '^\./ils '
sleep 1
SECS=${1:-21600}
nohup python3 rrr.py 96  6 $SECS 0 $RANDOM > logs/rrr_96_a.log  2>&1 &
nohup python3 rrr.py 96  6 $SECS 0 $RANDOM > logs/rrr_96_b.log  2>&1 &
nohup python3 rrr.py 105 6 $SECS 0 $RANDOM > logs/rrr_105_a.log 2>&1 &
nohup python3 rrr.py 105 6 $SECS 0 $RANDOM > logs/rrr_105_b.log 2>&1 &
nohup python3 rrr.py 112 6 $SECS 0 $RANDOM > logs/rrr_112.log   2>&1 &
nohup python3 rrr.py 117 6 $SECS 0 $RANDOM > logs/rrr_117.log   2>&1 &
nohup python3 rrr.py 120 7 $SECS 0 $RANDOM > logs/rrr_120.log   2>&1 &
nohup python3 rrr.py 132 9 $SECS 0 $RANDOM > logs/rrr_132.log   2>&1 &
echo launched

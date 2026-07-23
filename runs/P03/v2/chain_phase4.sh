#!/bin/bash
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
cd $D
while ! grep -q DONE $D/logs/c_n10e13_runner.log 2>/dev/null; do sleep 60; done
python3 ilp_survivors.py surv_n10e13_*.txt > logs/ilp_n10e13.log 2>&1
bash c_sweep.sh n9e14 9 14:14 32 8 > logs/c_n9e14_runner.log 2>&1
python3 ilp_survivors.py surv_n9e14_*.txt > logs/ilp_n9e14.log 2>&1
echo PHASE4CHAIN DONE

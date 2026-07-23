#!/bin/bash
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
while pgrep -f "fifo_sweep.sh n8" > /dev/null; do sleep 20; done
bash $D/fifo_sweep.sh n9 9 8:11

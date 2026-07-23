#!/bin/bash
while pgrep -f "exhaust_small.py n8" > /dev/null; do sleep 30; done
xargs -a /home/ubuntu/repos/solving-math-problems/runs/P03/v2/jobs9.txt -P 7 -I CMD bash -c CMD
echo N9DONE

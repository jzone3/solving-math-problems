#!/bin/bash
pkill -f "xargs -a /home/ubuntu/repos/solving-math-problems/runs/P03/v2/jobs8c.txt"
pkill -f "exhaust_small.py n8"
pkill -f chain9.sh
sleep 1
echo killed

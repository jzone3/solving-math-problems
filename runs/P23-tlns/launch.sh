#!/bin/bash
# Launch a chained worker in the background.
# Usage: ./launch.sh <mode> <seed> [env assignments...]
cd "$(dirname "$0")"
mode=$1; seed=$2; shift 2
env MODE="$mode" SEED="$seed" "$@" nohup ./chain.sh > "ch_${seed}.log" 2>&1 &
echo "launched $mode seed $seed pid $!"

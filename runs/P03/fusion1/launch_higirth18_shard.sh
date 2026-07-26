#!/bin/sh
set -eu

shard=$1
ENGINE=/tmp/p03_engine_higirth18
gcc -O3 -std=c11 -Wall -Wextra -o "$ENGINE" engine.c

log="higirth18_${shard}.log"
input="higirth18_shard_${shard}.txt"
resume="higirth18_resume_${shard}.txt"
completed=0
if [ -f "$log" ]; then
    completed=$(grep -c '^GRAPH ' "$log" || true)
fi
sed -n "$((completed + 1)),\$p" "$input" > "$resume"
stdbuf -oL -eL "$ENGINE" 3 tau3 0 1 < "$resume" >> "$log" 2>&1 &
echo $!

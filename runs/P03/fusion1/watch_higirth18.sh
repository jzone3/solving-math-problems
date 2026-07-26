#!/bin/sh
set -eu

while :; do
    for shard in $(seq 0 7); do
        found=0
        for pid in $(pgrep -f '/tmp/p03_engine_higirth18 3 tau3' || true); do
            if [ -r "/proc/$pid/fd/0" ] &&
               [ "$(readlink "/proc/$pid/fd/0")" = \
                 "$PWD/higirth18_resume_${shard}.txt" ]; then
                found=1
                break
            fi
        done
        if [ "$found" -eq 0 ]; then
            ./launch_higirth18_shard.sh "$shard" >> higirth18_watch.log 2>&1 || true
        fi
    done

    if git diff --quiet -- higirth18_?.log; then
        :
    else
        git add higirth18_0.log higirth18_1.log higirth18_2.log \
            higirth18_3.log higirth18_4.log higirth18_5.log \
            higirth18_6.log higirth18_7.log
        git commit -m "P03 fusion1: checkpoint high-girth n18 shards" || true
        git push origin runs/P03-fusion1 || true
    fi
    sleep 1800
done

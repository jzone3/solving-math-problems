#!/bin/sh
set -eu

while :; do
    count=$(pgrep -fc '/tmp/p03_engine_higirth18 3 tau3' || true)
    if [ "$count" -ne 8 ]; then
        if [ "$count" -gt 0 ]; then
            pkill -f '/tmp/p03_engine_higirth18 3 tau3' || true
            sleep 2
        fi
        ./resume_higirth18.sh >> higirth18_watch.log 2>&1 || true
    fi

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

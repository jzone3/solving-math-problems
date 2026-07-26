#!/bin/bash
pgrep -f "chain.sh" | xargs -r kill
pgrep -f "^python3 greedy8" | xargs -r kill
pgrep -f "^python3 tlns" | xargs -r kill
pgrep -f "monitor.sh" | xargs -r kill
sleep 2
pgrep -f kissat | xargs -r kill

#!/bin/bash
# Restart the implicit-hitting-set completion searches.
# Kill patterns are anchored so they cannot match the launching shell itself
# (an unanchored `pkill -f corehs` kept killing the very shell issuing it).
pkill -f '^python3 -u corehs.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
BUD=42 RESTRICT=union SEED=$RANDOM setsid nohup python3 -u corehs.py > hsu.log 2>&1 < /dev/null &
BUD=42 RESTRICT=near SEED=$RANDOM setsid nohup python3 -u corehs.py > hsn.log 2>&1 < /dev/null &
sleep 2
pgrep -fc 'corehs.py'

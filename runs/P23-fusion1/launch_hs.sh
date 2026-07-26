#!/bin/bash
# Restart the implicit-hitting-set completion searches: several workers per
# candidate set, all sharing one append-only clause bank that each worker
# re-reads every iteration, so clause generation parallelises.
# Kill patterns are anchored so they cannot match the launching shell itself
# (an unanchored `pkill -f corehs` kept killing the very shell issuing it).
pkill -f '^python3 -u corehs.py'
pkill -f '^python3 -u hlns.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
for i in 1 2 3 4; do
  BUD=42 RESTRICT=union SEED=$((RANDOM)) setsid nohup python3 -u corehs.py > hsu$i.log 2>&1 < /dev/null &
done
for i in 1 2; do
  BUD=42 RESTRICT=near SEED=$((RANDOM)) setsid nohup python3 -u corehs.py > hsn$i.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc 'corehs.py'

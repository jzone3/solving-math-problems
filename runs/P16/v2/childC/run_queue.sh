#!/bin/bash
# childC job queue (serialized to avoid CPU oversubscription with cpsat44)
set -x
cd "$(dirname "$0")"

# wait for d2D5 screeners
while pgrep -f "geng_screen.py d2D5" > /dev/null; do sleep 20; done

# n=11, d3..6 (near-regular, non-bipartite allowed): 64.4M graphs, 8-way
for i in $(seq 0 7); do
  bash -c "nauty-geng -q -c -d3 -D6 11 $i/8 | python3 geng_screen.py d3D6_$i" > n11_d3D6_$i.log 2>&1 &
done
wait

# overlays
python3 overlay_search.py > overlay.log 2>&1

# continuous quotient relaxation, both bounds
python3 continuous_quotient.py --bound 44 --kmin 4 --kmax 8 --restarts 30 > cont44.log 2>&1 &
python3 continuous_quotient.py --bound 46 --kmin 4 --kmax 8 --restarts 30 > cont46.log 2>&1 &
wait

# cpsat bound 46 (after cpsat44 finishes)
while pgrep -f "cpsat_quotient.py --bound 44" > /dev/null; do sleep 30; done
python3 cpsat_quotient.py --bound 46 --kmin 4 --kmax 10 --budget 500 > cpsat46.log 2>&1
echo QUEUE_DONE

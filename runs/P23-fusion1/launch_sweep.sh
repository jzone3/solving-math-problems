#!/bin/bash
# Sweep translations downward in radius (6 shards), and start greedy chains on
# the smallest obstructing universe found so far (score-65 at radius 1.6).
pkill -f '^python3 -u tsweep.py'
pkill -f '^python3 -u greedy8.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
for i in 0 1 2 3; do
  IN=tscan2.pkl START=$i STEP=4 RADII=1.6,1.5,1.4,1.3 TIME=400 \
    setsid nohup python3 -u tsweep.py > sweep$i.log 2>&1 < /dev/null &
done
cd /home/ubuntu/p23w4 || exit 1
cp /home/ubuntu/p23h/tuniv_score65_1.6.pkl t65small.pkl
python3 - <<'PY'
import pickle
pts, E = pickle.load(open('t65small.pkl', 'rb'))
pickle.dump(sorted(range(len(pts))), open('t65small_start.pkl', 'wb'))
print(len(pts), 'vertices', len(E), 'edges')
PY
for s in 1 2 3 4; do
  POOL=t65small.pkl setsid nohup python3 -u greedy8.py $s t65small_start.pkl s65$s > t65small_$s.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc 'tsweep.py|greedy8.py'

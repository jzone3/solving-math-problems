#!/bin/bash
# Greedy chains on the smallest obstructing universe found so far
# (score-65 translation, rA = 1.6, rB = 1.3: 2581 vertices), plus a further
# asymmetric-radius scan.
pkill -f '^python3 -u greedy8.py'
sleep 1
cd /home/ubuntu/p23h || exit 1
PAIRS='1.7:1.2,1.7:1.1,1.8:1.1,1.8:1.0,1.65:1.25,1.75:1.15' TIME=400 \
  setsid nohup python3 -u tasym.py > tasym3.log 2>&1 < /dev/null &
cd /home/ubuntu/p23w4 || exit 1
cp /home/ubuntu/p23h/tasym_1.6_1.3.pkl asym.pkl
python3 - <<'PY'
import pickle
pts, E = pickle.load(open('asym.pkl', 'rb'))
pickle.dump(sorted(range(len(pts))), open('asym_start.pkl', 'wb'))
print(len(pts), 'vertices', len(E), 'edges')
PY
for s in 1 2 3 4 5; do
  POOL=asym.pkl setsid nohup python3 -u greedy8.py $s asym_start.pkl as$s > asym_$s.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc 'greedy8.py|tasym.py'

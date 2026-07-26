#!/bin/bash
# Minimise the second translated universe (score-65 T) and free the r3 trade
# workers, which have been timing out without accepting a trade.
pkill -f '^python3 -u hlns.py'
sleep 1
cd /home/ubuntu/p23w4 || exit 1
cp /home/ubuntu/p23h/tuniv_65.pkl .
python3 - <<'PY'
import pickle
pts, E = pickle.load(open('tuniv_65.pkl', 'rb'))
pickle.dump(sorted(range(len(pts))), open('t65_start.pkl', 'wb'))
print(len(pts), 'vertices', len(E), 'edges')
PY
for s in 1 2 3; do
  POOL=tuniv_65.pkl setsid nohup python3 -u greedy8.py $s t65_start.pkl t65s$s > t65_$s.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc greedy8.py

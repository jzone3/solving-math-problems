#!/bin/bash
# Minimise the translated-rotation universe found by tscan/ttest:
# A u (T + omega A) with T != 0 is non-4-colorable and is NOT Parts' universe.
pkill -f '^python3 -u greedy8.py'
sleep 1
cd /home/ubuntu/p23w4 || exit 1
cp /home/ubuntu/p23h/tuniv_63.pkl .
python3 - <<'PY'
import pickle
pts, E = pickle.load(open('tuniv_63.pkl', 'rb'))
pickle.dump(sorted(range(len(pts))), open('t63_start.pkl', 'wb'))
print(len(pts), 'vertices', len(E), 'edges')
PY
for s in 1 2 3; do
  POOL=tuniv_63.pkl setsid nohup python3 -u greedy8.py $s t63_start.pkl t63s$s > t63_$s.log 2>&1 < /dev/null &
done
sleep 2
pgrep -fc greedy8.py

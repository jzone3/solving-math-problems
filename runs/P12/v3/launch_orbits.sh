#!/bin/bash
cd "$(dirname "$0")"
rm -f orbit_p11_d5.out orbit_p11_d2.out orbit_p13_d6.out orbit_p13_d4.out orbit_p13_d3.out orbit_p13_d2.out
for a in "11 5 1" "11 2 4" "13 6 1" "13 4 2" "13 3 3" "13 2 5"; do
  set -- $a
  setsid nohup nice python3 -u orbit_search.py $1 $2 $3 21600 > "orbit_p$1_d$2_k$3.out" 2>&1 < /dev/null &
done
sleep 2
ps aux | grep orbit_searc[h] | wc -l

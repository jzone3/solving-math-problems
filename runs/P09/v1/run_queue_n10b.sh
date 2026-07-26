#!/bin/bash
cd /home/ubuntu/solving-math-problems/runs/P09/v1
for i in $(seq 22 44); do
  [ -s "blowup_n10_p$i.log" ] && continue
  pgrep -f "geng -qc 10 $i/45" >/dev/null && continue
  while [ "$(pgrep -c nauty-geng)" -ge 7 ]; do sleep 60; done
  nohup bash -c "nauty-geng -qc 10 $i/45 | python3 blowup.py stdin 6 200 $((900+i)) > blowup_n10_p$i.log 2>&1" &
  sleep 5
done
wait

#!/bin/bash
# Append a one-line status snapshot every 5 minutes, so a long run can be
# inspected with a single `tail`.
cd "$(dirname "$0")"
while true; do
  echo "== $(date -u +%H:%M:%S) load=$(cut -d' ' -f1-3 /proc/loadavg)"
  python3 best.py | head -3
  for f in gr_*.log tl_*.log cm_*.log; do
    [ -f "$f" ] && echo "   $f: $(tail -n 1 "$f")"
  done
  sleep 300
done

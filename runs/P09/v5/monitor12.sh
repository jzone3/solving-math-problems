#!/bin/bash
# Periodically checkpoint n=12 sweep progress: aggregate part summaries,
# commit candidate/summary files to the run branch.
cd "$(dirname "$0")"
while true; do
  sleep 1800
  done_parts=$(ls logs12/sum_*.txt 2>/dev/null | wc -l)
  {
    echo "=== checkpoint $(date -u +%FT%TZ) parts_done=$done_parts/96 ==="
    grep -h SUMMARY logs12/sum_*.txt 2>/dev/null | \
      awk '{tot+=substr($3,7); cl+=substr($4,9); cd+=substr($5,6)} END {print "aggregate total="tot" cliqued="cl" cand="cd}'
    grep -h CAND logs12/cand_*.txt 2>/dev/null | wc -l | sed 's/^/cand_lines=/'
  } >> logs12/PROGRESS.txt
  if [ "$done_parts" -gt 0 ]; then
    git add logs12/sum_*.txt logs12/cand_*.txt logs12/PROGRESS.txt 2>/dev/null
    git commit -q -m "P09 V5 n=12 sweep checkpoint: $done_parts/96 parts done" 2>/dev/null && git push -q 2>/dev/null
  fi
  if [ "$done_parts" -ge 96 ]; then break; fi
done

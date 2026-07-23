#!/bin/bash
# Distributed rowdfs2 wrapper. usage: rowsplit.sh N LO HI JOBS [MAXSEC]
# Splits top-level candidate range [LO,HI) into JOBS chunks, runs rowdfs2 on
# each in parallel, writes results to rowres_N/LO_HI_chunk*.out, then appends
# a summary line to rowres_N/summary_${LO}_${HI}.txt, commits and pushes.
set -u
cd "$(dirname "$0")"
N=$1; LO=$2; HI=$3; J=$4; MAXSEC=${5:-999999999}
gcc -O3 -march=native -o rowdfs2 rowdfs2.c || exit 1
D=rowres_$N; mkdir -p $D
STEP=$(( (HI-LO+J-1)/J ))
pids=()
for ((k=0;k<J;k++)); do
  a=$((LO+k*STEP)); b=$((a+STEP)); [ $b -gt $HI ] && b=$HI
  [ $a -ge $b ] && continue
  out=$D/${a}_${b}.out
  if [ -s "$out" ] && grep -qE 'EXHAUSTED|WITNESS' "$out"; then continue; fi
  ( ./rowdfs2 $N 1 $a $b $MAXSEC > $out 2> $D/${a}_${b}.err ) &
  pids+=($!)
done
for p in "${pids[@]:-}"; do [ -n "$p" ] && wait $p; done
S=$D/summary_${LO}_${HI}.txt
{ echo "== rowsplit N=$N range=[$LO,$HI) $(date -u)"
  for f in $D/*_*.out; do
    [[ $f == *summary* ]] && continue
    echo "$(basename $f): $(tail -1 $f)"
    grep -A$((N)) WITNESS $f || true
  done; } > $S
git add -f $S
wit=$(grep -l WITNESS $D/*.out 2>/dev/null || true)
[ -n "$wit" ] && git add -f $wit
git commit -q -m "rowdfs2 results N=$N range $LO-$HI" && {
  for a in 1 2 3 4 5; do git pull -q --rebase && git push -q && break; sleep $((RANDOM%20+5)); done
}
echo "rowsplit done N=$N [$LO,$HI)"

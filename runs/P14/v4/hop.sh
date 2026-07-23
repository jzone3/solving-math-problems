#!/bin/bash
# Basin hopping wrapper: repeat (anneal from start; keep best; perturb best -> next start).
# usage: hop.sh name V B r1 r2 K Lam seed total_seconds leg_seconds init_start
set -u
name=$1; V=$2; B=$3; r1=$4; r2=$5; K=$6; Lam=$7; seed=$8; total=$9; leg=${10}; start=${11}
dir=$(dirname "$0"); cd "$dir"
work=hopwork_$name; mkdir -p $work
cp "$start" $work/cur.txt
end=$(( $(date +%s) + total ))
leg_i=0
bestv=999999
while [ $(date +%s) -lt $end ]; do
  leg_i=$((leg_i+1))
  ./anneal3 $V $B $r1 $r2 $K $Lam $((seed+leg_i)) $leg $work/cur.txt > $work/out_$leg_i.txt 2>&1
  if head -1 $work/out_$leg_i.txt | grep -q SOLVED; then
    echo "SOLVED leg $leg_i"; cp $work/out_$leg_i.txt $work/SOLVED.txt; exit 0
  fi
  v=$(head -1 $work/out_$leg_i.txt | sed 's/.*=//')
  if [ "$v" -le "$bestv" ]; then
    bestv=$v; tail -n +2 $work/out_$leg_i.txt > $work/best.txt
  fi
  echo "leg $leg_i viol=$v best=$bestv"
  python3 perturb.py $work/best.txt $work/cur.txt ${KICK:-8} $((seed+leg_i*7))
done
echo "DONE best=$bestv"

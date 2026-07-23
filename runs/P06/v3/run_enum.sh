#!/bin/bash
# Parallel driver for enum_seq3: verifies (*) over all graphical sequences of
# length n. Splits by d1; splits the heavy top-4 d1 values further by d2 thirds.
# usage: ./run_enum.sh n [jobs]
set -u
n=$1; J=${2:-8}
dir=enum${n}_parts; mkdir -p $dir
tasks=()
for ((d1=n-1; d1>=0; d1--)); do
    if ((d1 >= n-4)); then
        t=$((d1/3))
        tasks+=("$d1 0 $t" "$d1 $((t+1)) $((2*t))" "$d1 $((2*t+1)) $d1")
    else
        tasks+=("$d1")
    fi
done
printf '%s\n' "${tasks[@]}" | xargs -P $J -I{} sh -c \
  "./enum_seq3 $n {} > $dir/part_\$(echo {} | tr ' ' '_').out 2>&1"
echo "ALL PARTS DONE for n=$n"
grep -h VIOLATION $dir/*.out
tail -qn1 $dir/*.out | awk '{for(i=1;i<=NF;i++){if($i~/graphical=/){split($i,a,"=");s+=a[2]}if($i~/g=/&&$i!~/graphical/){split($i,b,"=");if(b[2]>m||!f){m=b[2];f=1}}}}END{printf "TOTAL graphical=%d  MAX g=%.12g\n",s,m}'

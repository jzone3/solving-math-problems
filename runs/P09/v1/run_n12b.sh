#!/bin/bash
# Wait for in-flight parts 8-15 to finish, then process parts 24-55 locally (16-23 -> child session, 56-63 held)
cd "$(dirname "$0")"
while pgrep -x bn_check > /dev/null; do sleep 60; done
seq 24 55 | xargs -P 8 -I{} sh -c 'if [ ! -f c12/n12_p{}.done ]; then nauty-geng -q 12 {}/64 2>/dev/null | ./bn_check 12 n12p{} > c12/n12_p{}.out 2> c12/n12_p{}.log && touch c12/n12_p{}.done; fi'
echo LOCALB_DONE > c12/n12_LOCALB.done

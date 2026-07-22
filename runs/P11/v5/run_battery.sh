#!/bin/bash
# ICW_d(m,k) exhausts for all open cells n<=200 admitting a McFarland
# d-multiplier (params generated from cwm_tools; match AGZ Table 9).
# solutions=0  =>  no CW(n,k), conditional on AGZ Thm 4.1 + fixed translate.
cd "$(dirname "$0")"
run() { echo "== $*"; timeout 86400 "$@"; }
{
run ./exhaust_icw 35 6 3 4     # CW(105,36)
run ./exhaust_icw 7 6 16 2     # CW(112,36)
run ./exhaust_icw 13 6 9 3     # CW(117,36)
run ./exhaust_icw 35 6 4 4     # CW(140,36)
run ./exhaust_icw 5 6 36 2     # CW(180,36)
run ./exhaust_icw 65 6 3 16    # CW(195,36)
run ./exhaust_icw 35 8 4 2     # CW(140,64)
run ./exhaust_icw 45 8 4 2     # CW(180,64)
run ./exhaust_icw 91 8 2 2     # CW(182,64)  AGZ Prop 5.1 core
run ./exhaust_icw 49 8 4 2     # CW(196,64)
run ./exhaust_icw 44 9 3 3     # CW(132,81)  AGZ Prop 4.2 core
run ./exhaust_icw 52 9 3 3     # CW(156,81)
run ./exhaust_icw 65 9 3 3     # CW(195,81)
run ./exhaust_icw 22 9 9 3     # CW(198,81)
run ./exhaust_icw 7 10 16 2    # CW(112,100)
run ./exhaust_icw 3 10 40 2    # CW(120,100)
# CW(155,100): m=31, multiplier group trivial -- no exhaust possible
run ./exhaust_icw 39 10 4 5    # CW(156,100)
run ./exhaust_icw 33 10 5 4    # CW(165,100)
run ./exhaust_icw 91 10 2 64   # CW(182,100)
run ./exhaust_icw 39 10 5 5    # CW(195,100)
} 2>&1

#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 -u verify.py "$1" > "$2" 2>&1 < /dev/null &
echo started $!

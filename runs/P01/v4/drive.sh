#!/bin/bash
# Escalation driver: g5 25 -> 26 -> 27 campaigns (8-way), logging as it goes.
set -u
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D"
./run_campaign.sh 25 -g5 16 8   >> logs/driver.log 2>&1
./run_campaign.sh 26 -g5 32 8   >> logs/driver.log 2>&1
./run_campaign.sh 27 -g5 64 8   >> logs/driver.log 2>&1
echo "DRIVER FINISHED" >> logs/driver.log

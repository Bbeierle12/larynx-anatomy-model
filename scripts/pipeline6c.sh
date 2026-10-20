#!/bin/bash
# assemble the 2x and the 1:1 builds one after the other (memory), then QA both
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
BUILD=build6 OFFSCALE=0.5 bash scripts/pipeline6b.sh
cp build6/occ_*.npz build6/part_*.ply build6/grid.npy build6/trachea_scale.npy build6_1x/
BUILD=build6_1x OFFSCALE=1.0 bash scripts/pipeline6b.sh
echo "== both done"

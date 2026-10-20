#!/bin/bash
# assemble the 2x and the 1:1 builds one after the other (memory), then QA both
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
BUILD=build7 OFFSCALE=0.5 bash scripts/pipeline6b.sh
cp build7/occ_*.npz build7/part_*.ply build7/grid.npy build7/trachea_scale.npy build7_1x/
BUILD=build7_1x OFFSCALE=1.0 bash scripts/pipeline6b.sh
echo "== both done"

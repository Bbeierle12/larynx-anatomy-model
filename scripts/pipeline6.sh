#!/bin/bash
# Stage 2 pipeline: framework (deform5) -> muscles (muscles6) -> voxelise -> trachea fit -> SDF assembly -> union
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build6}
export OFFSCALE=${OFFSCALE:-0.5}
echo "== deform5 ($BUILD)"; python3 scripts/deform5.py 2>&1 | grep -v Warning
echo "== muscles6"; python3 scripts/muscles6.py 2>&1 | grep -v Warning
echo "== vox"; python3 scripts/vox.py 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 28 31 32 35 36 38 39 48 49 2>&1 | grep -v Warning
echo "== stage1b"; MATCH=lumen python3 scripts/stage1b_trachea.py 2>&1 | grep -v Warning
echo "== stage5 (OFFSCALE $OFFSCALE)"; HE_SCULPT=1 LIG_H=3.5 SEAM=-2.0 LUMEN_BLEND=10 UNION_SEPARATE=1 NO_MERGE=1 python3 scripts/stage5_sdf.py 2>&1 | grep -v Warning
echo "== union"; python3 scripts/union_only.py 2>&1 | grep -v Warning
echo "== qa"; python3 scripts/qa_anat.py 2>&1 | grep -v Warning; python3 scripts/qa_print.py 2>&1 | grep -v Warning
echo "== done"

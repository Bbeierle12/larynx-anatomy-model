#!/bin/bash
# Version 5 pipeline: widened framework (deform7) -> wall voxels -> muscles (muscles6) -> remaining voxels -> trachea fit -> SDF assembly -> union -> QA
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}
export OFFSCALE=${OFFSCALE:-0.5}
echo "== deform7 ($BUILD)"; python3 scripts/deform7.py 2>&1 | grep -v Warning
echo "== vox (walls)"; python3 scripts/vox.py 2 3 4 5 38 39 12 13 14 15 16 28 11 2>&1 | grep -v Warning
echo "== muscles6"; python3 scripts/muscles6.py 2>&1 | grep -v Warning
echo "== vox (rest)"; python3 scripts/vox.py 1 6 7 8 9 10 17 18 19 20 21 22 23 31 32 35 36 48 49 2>&1 | grep -v Warning
echo "== tissues7"; python3 scripts/tissues7.py 2>&1 | grep -v Warning
echo "== stage1b"; MATCH=lumen python3 scripts/stage1b_trachea.py 2>&1 | grep -v Warning
echo "== stage5 (OFFSCALE $OFFSCALE)"; HE_SCULPT=1 LIG_H=3.5 SEAM=-2.0 LUMEN_BLEND=10 UNION_SEPARATE=1 NO_MERGE=1 python3 scripts/stage5_sdf.py 2>&1 | grep -v Warning
echo "== union"; python3 scripts/union_only.py 2>&1 | grep -v Warning
echo "== qa"; python3 scripts/qa_anat.py 2>&1 | grep -v Warning; python3 scripts/qa_print.py $BUILD/final_union.ply $BUILD/final_thickness.npy 2>&1 | grep -v Warning; python3 scripts/qa_muscles.py 2>&1 | grep -v Warning
echo "== done"

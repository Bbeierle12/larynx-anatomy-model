#!/bin/bash
# re-assemble after a muscle change (parts/occ already written): stage5 -> union -> QA
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build6}; export OFFSCALE=${OFFSCALE:-0.5}
echo "== stage5 (OFFSCALE $OFFSCALE)"; HE_SCULPT=1 LIG_H=3.5 SEAM=-2.0 LUMEN_BLEND=10 UNION_SEPARATE=1 NO_MERGE=1 python3 scripts/stage5_sdf.py 2>&1 | grep -v Warning
echo "== union"; python3 scripts/union_only.py 2>&1 | grep -v Warning
echo "== qa"; python3 scripts/qa_anat.py 2>&1 | grep -v Warning; python3 scripts/qa_print.py $BUILD/final_union.ply $BUILD/final_thickness.npy 2>&1 | grep -v Warning; python3 scripts/qa_muscles.py 2>&1 | grep -v Warning
echo "== done"

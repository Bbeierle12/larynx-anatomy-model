#!/bin/bash
# Version 6 full chain: petiole lift -> walls -> muscles -> rest (+constrictors) -> stage-3 tissues -> trachea fit -> 3b/3c tissues -> assembly -> QA
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}; export OFFSCALE=${OFFSCALE:-0.5}
rm -f $BUILD/srcTE_48.npz $BUILD/srcTE_49.npz
echo "== deform7 ($BUILD)"; python3 scripts/deform7.py 2>&1 | grep -v Warning
echo "== vox (walls)"; python3 scripts/vox.py 2 3 4 5 38 39 12 13 14 15 16 28 11 2>&1 | grep -v Warning
echo "== muscles6"; python3 scripts/muscles6.py 2>&1 | grep -v Warning
echo "== vox (rest)"; python3 scripts/vox.py 1 6 7 8 9 10 17 18 19 20 21 22 23 31 32 35 36 48 49 80 81 2>&1 | grep -v Warning
echo "== tissues7"; python3 scripts/tissues7.py 2>&1 | grep -v Warning
echo "== stage1b"; MATCH=lumen python3 scripts/stage1b_trachea.py 2>&1 | grep -v Warning
echo "== tissues8 tongue"; python3 scripts/tissues8.py tongue 2>&1 | grep -v Warning
echo "== tissues9"; python3 scripts/tissues9.py sinus latwall 2>&1 | grep -v Warning
echo "== tissues8 rest"; python3 scripts/tissues8.py fat saccule tendon capsule 2>&1 | grep -v Warning
echo "== tissues9 lining"; python3 scripts/tissues9.py lining 2>&1 | grep -v Warning
echo "== tissues10"; python3 scripts/tissues10.py 2>&1 | grep -v Warning
echo "== assembly"; bash scripts/pipeline6b.sh
python3 scripts/qa_stage3.py 2>&1 | grep -v Warning
echo "== all done"

#!/bin/bash
# v6 resume from the stage-3 tissues: source parts restored by deform7 (same grid), then everything constructed after the muscles is rebuilt
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}; export OFFSCALE=${OFFSCALE:-0.5}
echo "== deform7 (restore source parts)"; python3 scripts/deform7.py 2>&1 | grep -v Warning | tail -n 3
python3 -c "import numpy as np,sys; a=np.load('$BUILD/grid.npy'); b=np.load('$BUILD/grid_frozen.npy'); assert np.allclose(a,b), 'grid moved'; print('grid unchanged')"
echo "== vox 80 81"; python3 scripts/vox.py 80 81 2>&1 | grep -v Warning
rm -f $BUILD/part_78.ply $BUILD/part_79.ply $BUILD/occ_78.npz $BUILD/occ_79.npz $BUILD/final_78.ply $BUILD/final_79.ply
echo "== tissues7"; python3 scripts/tissues7.py 2>&1 | grep -v Warning
echo "== stage1b"; MATCH=lumen python3 scripts/stage1b_trachea.py 2>&1 | grep -v Warning
echo "== tissues8 tongue"; python3 scripts/tissues8.py tongue 2>&1 | grep -v Warning
echo "== tissues9 sinus"; python3 scripts/tissues9.py sinus 2>&1 | grep -v Warning
echo "== tissues8 rest"; python3 scripts/tissues8.py fat saccule tendon capsule 2>&1 | grep -v Warning
echo "== tissues9 lining"; python3 scripts/tissues9.py lining 2>&1 | grep -v Warning
echo "== tissues10"; python3 scripts/tissues10.py 2>&1 | grep -v Warning
echo "== assembly"; bash scripts/pipeline6b.sh
python3 scripts/qa_stage3.py 2>&1 | grep -v Warning
echo "== all done"

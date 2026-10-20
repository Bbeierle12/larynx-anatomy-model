#!/bin/bash
# v6 resume from the stage-3 tissues, with the constrictors restored first; the fat fills before the saccules are cut
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}; export OFFSCALE=${OFFSCALE:-0.5}
echo "== deform7 (restore source parts)"; python3 scripts/deform7.py 2>&1 | grep -v Warning | tail -n 2
python3 -c "import numpy as np; a=np.load('$BUILD/grid.npy'); b=np.load('$BUILD/grid_frozen.npy'); assert np.allclose(a,b), 'grid moved'; print('grid unchanged')"
echo "== vox 80 81"; python3 scripts/vox.py 80 81 2>&1 | grep -v Warning
echo "== tissues7"; python3 scripts/tissues7.py 2>&1 | grep -v Warning
echo "== tissues9 sinus"; python3 scripts/tissues9.py sinus 2>&1 | grep -v Warning
echo "== tissues8 rest"; python3 scripts/tissues8.py fat saccule tendon capsule 2>&1 | grep -v Warning
echo "== tissues9 lining"; python3 scripts/tissues9.py lining 2>&1 | grep -v Warning
echo "== tissues10"; python3 scripts/tissues10.py 2>&1 | grep -v Warning
echo "== assembly"; bash scripts/pipeline6b.sh
python3 scripts/qa_stage3.py 2>&1 | grep -v Warning
echo "== all done"

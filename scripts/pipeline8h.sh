#!/bin/bash
# v6 resume: restore the constrictors, rebuild the capsules (0.8 mm, no offset, above the muscles) and the hypopharyngeal mucosa (outside the larynx only), drop 78/79, reassemble
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}; export OFFSCALE=${OFFSCALE:-0.5}
echo "== deform7 (restore constrictors)"; python3 scripts/deform7.py 2>&1 | grep -v Warning | tail -n 4
echo "== vox 80 81"; python3 scripts/vox.py 80 81 2>&1 | grep -v Warning
rm -f $BUILD/part_78.ply $BUILD/part_79.ply $BUILD/occ_78.npz $BUILD/occ_79.npz $BUILD/final_78.ply $BUILD/final_79.ply
echo "== tissues8 capsule"; python3 scripts/tissues8.py capsule 2>&1 | grep -v Warning
echo "== tissues10 pharynx"; python3 scripts/tissues10.py pharynx 2>&1 | grep -v Warning
echo "== assembly"; bash scripts/pipeline6b.sh
python3 scripts/qa_stage3.py 2>&1 | grep -v Warning
echo "== all done"

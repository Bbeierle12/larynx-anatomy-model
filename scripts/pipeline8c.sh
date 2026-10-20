#!/bin/bash
# resume the version-6 chain from the fat step (parts up to the saccules already built)
set -e -o pipefail
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export BUILD=${BUILD:-build8}; export OFFSCALE=${OFFSCALE:-0.5}
echo "== tissues8 fat"; python3 scripts/tissues8.py fat 2>&1 | grep -v Warning
echo "== tissues9 lining"; python3 scripts/tissues9.py lining 2>&1 | grep -v Warning
echo "== tissues10"; python3 scripts/tissues10.py pharynx 2>&1 | grep -v Warning
echo "== assembly"; bash scripts/pipeline6b.sh
python3 scripts/qa_stage3.py 2>&1 | grep -v Warning
echo "== all done"

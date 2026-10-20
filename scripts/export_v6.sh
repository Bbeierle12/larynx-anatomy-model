#!/bin/bash
# version-6 3MF export: 2x set from build8, 1:1 set from build8_1x
set -e
cd /tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad
export OUT=out8 V2=1 NSLOT=7
export TITLE="Larynx and upper trachea (BodyParts3D 4.0 rebuild), v6"
export DESC="Version 6: pre-epiglottic and paraglottic fat, saccules, joint capsules, Broyles tendon, piriform fossae, inferior constrictors, hypopharyngeal mucosa, upper oesophagus, tongue base with vallecula. Print halves to see inside; slot 7 (yellow) is fat."
echo "== 2x"; BUILD=build8 PREFIX=Larynx_v6_2x SCALE=2 python3 scripts/build3mf.py
rm -f out8/Larynx_v6_2x_halves_7colour.3mf                       # too deep for the bed with the tower: one half per file instead
for H in R L; do BUILD=build8 PREFIX=Larynx_v6_2x SCALE=2 HALF=$H ONLY_MULTI=1 HALF_ROTZ=1 python3 scripts/build3mf.py; done
python3 scripts/patch3mf.py out8/Larynx_v6_2x_halfR_7colour.3mf wipe_tower_x=2 prime_tower_width=30
if [ -d build8_1x ]; then echo "== 1:1"; BUILD=build8_1x PREFIX=Larynx_v6_lifesize SCALE=1 python3 scripts/build3mf.py; fi
ls -la out8/*.3mf

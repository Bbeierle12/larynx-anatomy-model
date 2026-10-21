"""Insert the v6 notes section into the rebuild doc and update its header and next steps."""
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
p = '/home/claude/larynx-lifesize-rebuild.md'; s = open(p).read()
sec = open(f'{S}/out8/v6_notes_section.md').read().rstrip() + '\n\n'
assert '{' not in sec.split('### Files')[1][:200] or '{FILES}' not in sec, 'files placeholder unfilled'
assert '## Version 5' in s and '## Version 6' not in s
s = s.replace('## Version 5: widened framework and stage 3, fold and supraglottic tissues (2026-10-20)', sec + '## Version 5: widened framework and stage 3, fold and supraglottic tissues (2026-10-20)', 1)
def rep(a, b):
    global s
    assert a in s, a[:50]; s = s.replace(a, b, 1)
rep('2026-10-19 (version 4 stage 2) and 2026-10-20 (version 5: widened framework and stage 3).',
    '2026-10-19 (version 4 stage 2) and 2026-10-20 (version 5: widened framework and stage 3; version 6: stages 3b and 3c, the spaces, fossae and hypopharynx).')
rep('**Use version 5** (stage 3) for the full larynx with vocal-fold cover, false folds, ventricle and supraglottic soft tissue on the widened framework;',
    '**Use version 6** (stages 3b and 3c) for the complete larynx with its fat-filled spaces, saccules, joint capsules, piriform fossae, constrictors, hypopharynx, upper oesophagus and tongue base: a solid block, print the halves to see inside. Version 5 (stage 3) is the last version whose supraglottis is open to view from outside: vocal-fold cover, false folds, ventricle and supraglottic soft tissue on the widened framework, with the spaces still void;')
rep('- ~~Fill the paraglottic space so the vocal fold is solid rather than a hollow strip.~~ Done in versions 4 and 5 above the fold level; the space below the folds and the pre-epiglottic space are still sealed voids.',
    '- ~~Fill the paraglottic space so the vocal fold is solid rather than a hollow strip.~~ Done: muscles in version 4, fat in version 6 (pre-epiglottic 3.6 mL, paraglottic 0.44 mL per side).')
rep('- Framework: raise the petiole so the thyro-epiglottic ligament attaches above the vestibular ligament; add a pharyngeal wall and piriform fossae if the model is to show the hypopharynx.\n- A soft-tissue shell (vallecula, pharynx, oesophageal inlet).',
    '- ~~Framework: raise the petiole so the thyro-epiglottic ligament attaches above the vestibular ligament; add a pharyngeal wall and piriform fossae.~~ Done in version 6 (leaf lifted 5 mm; fossae, constrictors, hypopharyngeal mucosa, oesophagus, vallecula).\n- Version 6 residuals: seat the thyro-epiglottic ligament on cartilage without dropping it to the vestibular ligaments\' level (reshape the notch floor or the ligament); a real tongue base instead of the block; a middle constrictor so the inferior one does not have to reach above the hyoid; 1.5–2 mm of paraglottic tissue between the fossa apex and the ventricle; line the arytenoid medial faces below the vocal process; mirror the cricothyroid oblique parts.\n- Optional stage 3d: extrinsic muscles (thyrohyoid, sternothyroid, sternohyoid, omohyoid) and the neurovascular cords (superior and recurrent laryngeal nerves, laryngeal vessels) at 2×; the thyrohyoid-membrane aperture.')
rep('- [Medtronic Shiley ETT sizes]', '''- Hermans, Van der Goten & Baert 1997, volume of the pre-epiglottic and paraglottic space on spiral CT, Surg Radiol Anat 19 (no link checked)
- Vadgaonkar et al. 2024, morphometry of the thyroid cartilage, epiglottis and piriform sinus, F1000Research 13:115 (no link checked)
- Reidenbach 1996, the paraglottic space and transglottic cancer, Clin Anat 9:363 (cited by the reviewer; no link checked)
- [Medtronic Shiley ETT sizes]''')
open(p, 'w').write(s); print('inserted; placeholders:', [l[:60] for l in s.splitlines() if '{' in l and '}' in l][:3])

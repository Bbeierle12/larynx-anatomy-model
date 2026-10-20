"""Insert the v5 notes section into the rebuild doc and update its header."""
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
p = '/home/claude/larynx-lifesize-rebuild.md'; s = open(p).read()
sec = open(f'{S}/out7/v5_notes_section.md').read().rstrip() + '\n\n'
assert '## Version 4, stage 2' in s and '## Version 5' not in s
s = s.replace('## Version 4, stage 2: intrinsic muscles (2026-10-19)', sec + '## Version 4, stage 2: intrinsic muscles (2026-10-19)', 1)
s = s.replace('Built 2026-10-17 (version 1), 2026-10-18 (versions 2 and 3 stage 1) and 2026-10-19 (version 4 stage 2).',
              'Built 2026-10-17 (version 1), 2026-10-18 (versions 2 and 3 stage 1), 2026-10-19 (version 4 stage 2) and 2026-10-20 (version 5: widened framework and stage 3).')
s = s.replace('**Use version 4** (stage 2) for the framework with all intrinsic muscles;',
              '**Use version 5** (stage 3) for the full larynx with vocal-fold cover, false folds, ventricle and supraglottic soft tissue on the widened framework; version 4 (stage 2) for the framework with all intrinsic muscles and no mucosa;')
s = s.replace('- Fill the paraglottic space (lateral cricoarytenoid muscle, fat) so the vocal fold is solid rather than a hollow strip.',
              '- ~~Fill the paraglottic space so the vocal fold is solid rather than a hollow strip.~~ Done in versions 4 and 5 above the fold level; the space below the folds and the pre-epiglottic space are still sealed voids.\n- Stage 4: poses (adducted / phonatory and fully abducted glottis as separate static models).\n- Stage 5: teaching features (labels, cut-aways, a sectioned fold showing the cover, ligament and muscle layers).\n- Framework: raise the petiole so the thyro-epiglottic ligament attaches above the vestibular ligament; add a pharyngeal wall and piriform fossae if the model is to show the hypopharynx.')
s = s.replace('- [Medtronic Shiley ETT sizes]', '''- [Kitzing & Sonesson 1967, shape and shift of the laryngeal ventricle during phonation (ventricle ~3 mm tall, 14 mm long at rest)](https://www.lunduniversity.lu.se/lup/publication/e80321fa-47fa-4cc0-bec1-412408353293)
- [Saldarriaga 2016, asymmetry of the laryngeal ventricle, cadavers (depth 2.3–2.5 mm at mid-length)](https://www.researchgate.net/publication/311514363_Asymmetry_of_Laryngeal_Ventricle_A_Direct_Anatomical_Study_in_Cadavers)
- [Guida & Zorzetto 2007, morphology of the human vestibular fold](https://www.scielo.cl/pdf/ijmorphol/v25n3/art10.pdf)
- [Rothrock 1990, radiologic criteria for epiglottitis (normal aryepiglottic fold width under 7 mm)](https://doi.org/10.1016/s0196-0644(05)82557-0)
- [Medtronic Shiley ETT sizes]''')
open(p, 'w').write(s); print('inserted; placeholders:', [l for l in s.splitlines() if '{' in l and '}' in l][:3])

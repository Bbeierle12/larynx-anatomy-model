## Version 5: widened framework and stage 3, fold and supraglottic tissues (2026-10-20)

Two things in one version. First a stage-1 revisit: the thyroid is widened 10 % laterally and the cricoid's outer wall 10 % (its lumen kept), because the v4 review showed the paraglottic space could not hold a normal thyroarytenoid and the inferior horns sat too close. Second, stage 3 of the plan: the vocal-fold cover and every supraglottic soft tissue the source lacks. 65 named parts (v4: 49). Everything in stage 3 is constructed anatomy: BodyParts3D has none of it.

### Framework change (`deform6.py`)

| Landmark | v4 | v5 | Reference |
|---|---|---|---|
| Thyroid superior-horn span | 38.6 mm | 42.4 mm | men 41.5 ± 7.2 |
| Thyroid angle (outer laminae) | 75° | 81° (70–88 over 5 levels) | men 74–78 ± 5–8 |
| Cricoid outer width at the ring | 24.8 mm | 27.2 mm | 27–31 |
| Cricoid lumen | 16.0 × 16.9 | unchanged | ~16 × 17.4 |
| Cricoarytenoid facets apart | 12.1 | 12.1 (the widening starts outside the facets) | 11.8–12.6 |
| Glottis (ligament edges) | 145 mm² | 145 mm² | — |

Lateral scale ×1.10 about the midline for the thyroid (the hyoid-attached membranes blend to ×1.0 at the hyoid); the cricoid widening is radial about the airway axis, zero at r ≤ 8.8 mm (lumen and facets) and full beyond r 11.2 mm, so the lateral walls thicken from 4.4 to 5.6 mm and the cricothyroid facets move out with the inferior horns, which are re-seated as before. The muscles of stage 2 were regenerated on the new framework.

### Stage 3: what was built and from what

The tissues are placed in a fold frame: z0 = the vocal ligament's level at each point along it (46.5–47.2 mm above the base), x_edge = the ligament's medial edge.

| Part | Construction | Dimension used | Reference |
|---|---|---|---|
| Vocal fold cover R/L (50, 51) | The 1.0 mm layer on the airway side of the fold core (vocal ligament, thyroarytenoid, vocalis, upper conus), found by line of sight to the airway axis; from 1 mm in front of the anterior commissure to 1.5 mm behind the vocal process, down to z0 − 6 (infraglottic surface) and over the muscle's upper surface, capped at z0 + 3; closed cavities inside the fold filled | cover 1.0 mm | epithelium + superficial lamina propria ≈ 1 mm (Hirano) |
| Thyroarytenoid cap | The thyroarytenoid and vocalis stop at z0 + 1.8 so the ventricle lies above them (origin on the thyroid up to z0 + 0.8, insertion up to the arytenoid base + 4.3) | ventricle floor z0 + 2.8 after the cover | fold upper surface 1–3 mm above the free edge |
| Vestibular (false) fold R/L (52, 53) | Four capsule chains along the fold frame (radii 2.0–2.4 mm), free edge FF_OFF = 2.4 mm lateral of the covered true-fold edge, underside z0 + 5.6, top z0 + 10.2; from the inner thyroid angle back onto the anterolateral face of the arytenoid; clipped at the lamina's inner surface. Ranked above the quadrangular membrane so the membrane is embedded in it rather than cutting it | 4.6 mm thick, edge 2.4 lateral and 5.6 above the true-fold edge | textbook figures, not a measured series: fold 4–6 mm thick, edge 2–4 mm lateral and 4–7 mm above the true fold; ventricle ~3 mm tall and 14 mm long at rest (Kitzing & Sonesson 1967), 2.3–2.5 mm deep at mid-length in cadavers (Saldarriaga 2016) |
| Vestibular ligament R/L (54, 55) | 1.1 mm cord inside the false fold, 2.2 mm lateral of the fold edge at z0 + 7.4, thyroid angle → anterolateral arytenoid | | lower edge of the quadrangular membrane |
| Ventricle lateral wall R/L (62, 63) | Mucosa closing the paraglottic slot between the fold cover (floor) and the false fold (roof): medial face 4.5 mm lateral of the true-fold edge at the roof, sloping 0.5 mm/mm laterally toward the floor, at least 1.5 mm thick against the lamina | ventricle 2.6–4.2 mm deep, 2.9 mm tall | 2.3–2.5 mm deep (cadaver), ~3 mm tall (radiograph, at rest) |
| Quadrangular membrane R/L (56, 57) | Ruled sheet 0.6 mm thick between the vestibular ligament line and the aryepiglottic line (arytenoid apex → the source aryepiglotticus strip → the epiglottis lateral margin). The thyro-epiglottic muscle is trimmed to its lateral side | 0.6 mm | thin membrane; 1.2 mm printed at 2× |
| Vestibular mucosa R/L (64, 65) | 0.8 mm lining on the airway side of the quadrangular membrane and of the arytenoid above the vocal-process level (line of sight to the axis) | 0.8 mm | |
| Aryepiglottic fold R/L (58, 59) | 4.4 mm mucosal tube along the aryepiglottic line (muscle and membrane inside it), with a cuneiform tubercle (r 2.7) over the upper end of the cuneiform and a corniculate tubercle (r 2.4) over the corniculate | 4.4 mm; tubercles 5.4 and 4.8 mm | fold 2–4 mm in life (lateral radiograph: under 7 mm is normal, Rothrock 1990); tubercles 3–4 mm. The model's fold reads thick |
| Epiglottic tubercle (60) | Half-ellipsoid 8 wide × 7 tall grown 2.2 mm back from the laryngeal face of the petiole at the midline, z0 + 8.5; nothing on the lingual side | | midline bulge above the anterior commissure at false-fold level |
| Interarytenoid mucosa (61) | 1.2 mm layer on the anterior face of the transverse arytenoid between the arytenoid bodies (|x| < 4.5) | 1.2 mm | posterior commissure |

Priorities (higher wins a shared voxel): cartilage > vestibular ligament (58) > muscle (47–53) > false fold (46) > quadrangular membrane (45) > fold cover (40) > AE fold (37) > tubercle (36) > interarytenoid mucosa (35) > ventricle wall (34) > vestibular mucosa (33). Mucosa never displaces cartilage, ligament or muscle; the false fold owns the voxels where the membrane passes through it.

### Airway after stage 3

| Level | Area | Width | Inscribed circle |
|---|---|---|---|
| Subglottis (cricoid ring) | 221 mm² | 16.0 | 15.8 |
| Below the folds (z0 − 3) | 179 | 16.8 | 10.7 |
| Glottis with cover (z0) | 101 mm² (ligament edges alone: 145) | 7.8 | 7.7 |
| Fold upper surface (z0 + 1.5) | 148 | 9.6 | 8.1 |
| Ventricle (z0 + 3.5, coronal y −106 / −103 / −100) | air reaches 2.6 / 3.7 / 4.2 mm lateral of the fold edge | | |
| Largest sphere, trachea to above the folds | | | 7.5 mm (v4: 7.8) |

The covered glottis at 101 mm² sits between Brancatisano's tidal expiration (70 ± 7) and inspiration (126 ± 8); the ligament pose was not changed to compensate, so this is a mid-tidal breathing glottis. Above the false folds the model has no pharyngeal wall (piriform fossae, posterior pharyngeal wall are outside the plan), so the vestibule is open laterally-posteriorly behind the arytenoids; its width between the false-fold edges is 12 mm at mid-fold.

### Measurements, v4 → v5

| Quantity | v4 | v5 |
|---|---|---|
| Named parts | 49 | 65 |
| Union volume (2× build) | 18 811 mm³ | 23 016 mm³ |
| Muscle, both sides | 4.34 cm³ | 3.93 cm³ (TA complex capped at the ventricle floor: 251 / 264 mm³ per side) |
| Mucosa and fold cover | — | 3.43 cm³ |
| Surface < 0.4 / 0.8 / 1.2 mm (2× build) | 0.2 / 1.0 / 14.6 % | 0.1 / 1.1 / 13.2 % |

### Independent review

Four passes by a reviewer agent that had not seen the build, working only from the final meshes (scripts and section images under `review_v6/` and `review_v7/`).

**Pass 1 (first assembly, 61 parts).** Two must-fix items: the epiglottic tubercle was an ellipsoid centred on the epiglottis with 56 % of its volume on the lingual side; and the ventricle had no lateral wall — between the cover top (z0 + 2.8) and the false-fold underside (z0 + 5.6) the air ran from the lumen to the thyroid lamina, leaving the false folds as cantilevered slabs. Should-fix: pegs on the L cover; the quadrangular membrane (then ranked above the fold) bisected the thyro-epiglottic muscle and cut the false folds into two bodies with 0.3 mm slivers; false fold and vestibular ligament stopped 3–5 mm short of the arytenoid; vertical box-shaped fold edge; membrane and arytenoid faces bare; AE mucosa 14 % under 0.3 mm. Notes: interarytenoid plate flat; the vestibular ligament attaches to the thyroid angle above the thyro-epiglottic ligament (petiole sits 4 mm above the commissure); widening did no harm.

**Fixes.** Tubercle rebuilt as a posterior half-ellipsoid clipped at the epiglottis face. New ventricle lateral walls (62/63). Cover capped at z0 + 3. False folds measured from the covered edge, no clip plane, extended onto the arytenoid, ranked above the membrane (46 > 45); ligament moved inside the fold and extended. Thyro-epiglottic muscle trimmed to the lateral side of the membrane. AE mucosa radius 1.4 → 2.2 mm. New vestibular mucosa (64/65).

**Pass 2 (65 parts).** All eight items confirmed fixed (tubercle 96 % on the laryngeal side, 0 % lingual; ventricle 2.9–4.9 mm opening, ~3 mm deep, lumen enclosed at every level; covers matched; false folds one body each with the rounded edge 2.2–2.5 mm lateral of the true fold and the posterior end on the arytenoid; AE mucosa 1.4 % under 0.3 mm). Two new issues: the membrane had thinned to 0.4 mm (muscle priorities 49 above its 45) and a 33 mm³ anterior sliver of the thyro-epiglottic muscle below the membrane was bare on the anterior vestibule wall.

**Fixes.** Aryepiglotticus priority 49 → 44; muscle trim from the membrane's lateral face; the sliver below the membrane trimmed to the lateral side of the ligament line and dropped (thyro-epiglottic muscle 200 → 100 mm³, upper strip only). Walls grown 0.3 mm into the lamina to close 0.3–0.4 mm seams.

**Pass 3.** Membrane back to 0.60 mm (p25 0.60) with the layering mucosa | membrane | muscle at every probe; no bare muscle; seams closed; nothing else changed. One regression: removing the sliver opened a 2.4–3 mm midline channel above the thyro-epiglottic ligament from the vestibule into the empty pre-epiglottic space, plus a passage round the epiglottis margins at z0 + 9.7..11.2 (present since pass 2).

**Fix.** New part 66, the anterior vestibule wall: a plug between the ventricle walls, the thyro-epiglottic ligament, the thyroid angle and the laryngeal face of the petiole, z0 + 3.7..12.2.

**Pass 4.** Leak closed: no lumen anterior of y −110.3 at any level; recesses of 0.2–2.5 mm between plug and epiglottis margins are closed pockets, not channels; glottis and union unchanged. Verdict: export.

**Residuals recorded (accepted).**
- Aryepiglotticus 31/32: the membrane cuts them, 13 % of surface under 0.3 mm (slivers in a per-part print, solid in the union).
- Thyro-epiglottic muscle 100 mm³ per side (v4: 220) with a 1.6 mm² thyroid attachment at z0 + 9..11.
- Feather edges under 0.3 mm: membranes ~21 mm², ventricle walls ~20, vestibular mucosa ~15, thyro-epiglottic ~9 per side. All else ≥ 0.6 mm at 1:1.
- Vestibular ligament 1.6–1.8 mm from the fold edge (spec 2.2), 1.5 mm of fold between it and the membrane part; 0.5–2 % exposed at the angle.
- Ventricle walls 1.1–1.2 mm thick at y −108..−104 and 0.9–1.2 mm from the cover edge at the front.
- Membrane's anterior-upper margin near the epiglottis unlined.
- AE folds read thick (4.4 mm against 2–4); narrowest gap between them 6.5 mm at the corniculate tubercles.
- Interarytenoid mucosa a flat square-topped plate reaching the cricoid lamina.
- Framework: attachment order at the thyroid angle inverted (thyro-epiglottic ligament z0 + 0.9..5.6 below the vestibular ligament at + 5.8..8.6); paraglottic slits 0.3–0.6 mm lateral of the TA at z0 − 6..+1; pre-epiglottic and paraglottic spaces below the folds are voids; no pharyngeal wall above z0 + 13; LCA 12–16 % below the lamina's inferior border (v4).

### Files

Folder `Documents\Blender\Larynx life-size\`, sliced copies in `sliced - ready to print\`. Muscle (slot 5, red) and mucosa (slot 6, salmon) have their own filament slots, so the multi-colour files are 6-colour; the A1 mini's AMS lite has four slots, so merge mucosa into slot 4 and muscle into another in Bambu Studio, or accept two manual changes.

| File | Scale | Bambu Studio estimate |
|---|---|---|
| `Larynx_v5_2x_whole_1colour.3mf` | 2× (162 mm tall) | 13 h 32 min, 202 g |
| `Larynx_v5_2x_halves_1colour.3mf` | 2×; pins 16 mm hyoid, 10 mm cricoid | 16 h 34 min, 203 g |
| `Larynx_v5_2x_whole_6colour.3mf` | 2× | 87 h 34 min, 1102 g, 2356 colour changes (mostly purge) |
| `Larynx_v5_2x_halfR_6colour.3mf` | 2×, one half per file | 39 h 43 min, 479 g, 1019 colour changes (mostly purge) |
| `Larynx_v5_2x_halfL_6colour.3mf` | 2×, one half per file | 40 h 02 min, 482 g, 1023 colour changes (mostly purge) |
| `Larynx_v5_lifesize_whole_1colour.3mf` | 1:1 (81 mm) | 3 h 07 min, 31 g |
| `Larynx_v5_lifesize_halves_1colour.3mf` | 1:1; pins 7.5 / 4.5 mm | 3 h 45 min, 35 g |
| `Larynx_v5_lifesize_whole_6colour.3mf` | 1:1 | 41 h 22 min, 498 g, 1180 colour changes (mostly purge) |
| `Larynx_v5_lifesize_halves_6colour.3mf` | 1:1 | 19 h 41 min, 228 g, 511 colour changes (mostly purge) |

### Method notes

`pipeline7.sh`: `deform6.py` (deform5 settings plus SXT 1.10, CR_W 0.10, CR_R0 8.8, CR_R1 11.2) → `vox.py` for the airway-wall parts → `muscles6.py` (TA_OX1 7, TA_OZ0 1.8, TA_OZ1 0.8, TA_IZ 4.3, TA_K 90) → `vox.py` for the rest → `tissues7.py` (COVER 1.0, COVER_DOWN 6.0, COVER_TOP 3.0, FF_OFF 2.4, FF_ZLO 5.6, FF_ZHI 10.2, LIG_OFF 2.2, LIG_Z 1.8, VENT_D 4.5, VENT_SLOPE 0.5, VENT_MIN_T 1.5, QM_T 0.6, AE_R 2.2, CUN_R 2.7, CORN_R 2.4, ET_Z 8.5, ET_W 4, ET_D 2.5, ET_H 3.5, IA_T 1.2, MUC_T 0.8, MUC_ZMIN 2.0) → `stage1b_trachea.py` → `stage5_sdf.py` (as v4) → `union_only.py` (now fills closed cavities under 30 mm³) → `qa_anat.py`, `qa_print.py`, `qa_muscles.py`, `qa_stage3.py`. `build3mf.py` with NSLOT 6 puts mucosa on slot 6.

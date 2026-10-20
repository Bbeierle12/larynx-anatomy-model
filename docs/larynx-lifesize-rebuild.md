# Life-size larynx rebuild (BodyParts3D 4.0): build notes

Built 2026-10-17 (version 1), 2026-10-18 (versions 2 and 3 stage 1), 2026-10-19 (version 4 stage 2) and 2026-10-20 (version 5: widened framework and stage 3). This replaces the MakerWorld "Upper Airway Model" with a rebuild that puts anatomical accuracy first. The review of the original model is in `claude/upper-airway-model-review.md`.

**Use version 5** (stage 3) for the full larynx with vocal-fold cover, false folds, ventricle and supraglottic soft tissue on the widened framework; version 4 (stage 2) for the framework with all intrinsic muscles and no mucosa; version 3 (stage 1) for the corrected framework without muscles; version 2 for the open glottis on the source framework; version 1 for the source anatomy unchanged.

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

## Version 4, stage 2: intrinsic muscles (2026-10-19)

Second of the five stages. Every intrinsic muscle is now a named part: posterior cricoarytenoid, lateral cricoarytenoid, cricothyroid (straight and oblique parts), thyroarytenoid with a separate vocalis, transverse and oblique arytenoids, aryepiglotticus and the thyro-epiglottic part of the thyroarytenoid. The framework, joints, ligaments and airway are v3 stage 1 unchanged: glottis 145 mm², 24.4 mm long, 8.6 mm wide; subglottis 16.0 × 16.9 mm, 221 mm²; a 7.8 mm sphere passes. 49 named parts (v3: 37). An independent reviewer that had not seen the build checked it three times; what it still flags is under "Open items".

### Why the muscles are constructed, not warped from the source

BodyParts3D's intrinsic muscles are placeholders at 99 % polygon reduction: posterior cricoarytenoid 160 mm³ per side, lateral cricoarytenoid 33, cricothyroid 45 + 88, thyroarytenoid 138 + 223 (two sheets), vocalis 6, oblique arytenoid 13. Published sizes are 5–10× larger: cricothyroid 0.94 ± 0.12 g with a 73.8 ± 7.4 mm² cross-section (Cox, Alipour & Titze 1999, n = 6); thyroarytenoid 0.86–0.89 mL in men by MRI, 24.4–25 × 6.8 × 10.5 mm (Hamdan 2020); embalmed weights (Joshi 2024, n = 50, western India): cricothyroid 310–333 mg, posterior cricoarytenoid 230 mg, lateral cricoarytenoid 61–63 mg. The source cricothyroid also sits in the wrong place (over the lateral cricoid at the level of the thyroid lamina, not between the arch and the lamina's lower border), the source posterior cricoarytenoid floats 1–3 mm behind the lamina, and the source lateral cricoarytenoid is a 0.3 mm film. Warping these onto the corrected framework would have kept every one of those faults, so each muscle was rebuilt as a bundle of fibres between attachment footprints sampled on the v3 cartilage surfaces; the source was used only to confirm position and fibre direction. The transverse arytenoid (source, scaled with the arytenoids in stage 1) and the aryepiglotticus strips were kept.

### Method (`muscles6.py`)

A muscle is 3–70 fibres. Each fibre is a chain of capsules from a point 0.5 mm inside the origin cartilage to a point 0.6 mm inside the insertion cartilage, with a radius profile (thin at the attachments, thickest at the belly). Origin and insertion footprints are sampled on the cartilage surfaces with anatomical predicates (e.g. "posterior face of the cricoid lamina, 3.2 mm or more from the median ridge, 4 mm above the lower border, below the facet pads"), fibres are paired by rank so they do not cross, and each chain is draped: pushed out of cartilage in a chosen direction (posteriorly off the lamina for the PCA, radially off the arch for the cricothyroid, upward off the rim for the LCA, backward at the angle and medially along the lamina for the TA) and kept lateral to the conus elasticus and the vocal ligament by a lookup of the sheet's lateral surface per (y, z). Fibres are unioned by a hard minimum and smoothed with a 0.4 mm Gaussian (a smooth-minimum inflated the bellies), rasterised at 0.1 mm, and clipped by the enclosed airway lumen (a flood fill inside cartilage, conus, ligaments and transverse arytenoid, dilated 0.2 mm) so no muscle can sit in the airway or on the lumen side of its wall. Then they go through the same priority CSG as everything else (cartilage > ligament > muscle), so a muscle never displaces cartilage or ligament; bodies under 10 mm³ are dropped. The oblique arytenoids and lateral cricoarytenoids outrank the transverse arytenoid and the thyroarytenoid where they cross, and the left oblique is layered behind the right at the X. The thyroarytenoid is built as one body and split by a smooth surface at 35 % of the local width between the conus/ligament (with a vertical wall above the ligament) and the thyroid lamina; the medial part is the vocalis, never thinner than 1.2 mm before trimming.

### The muscles (volumes are the final parts after the cartilage/ligament trim, 2× build)

| Muscle (parts) | Origin → insertion in this model | Volume per side | Reference | Notes |
|---|---|---|---|---|
| Posterior cricoarytenoid (40, 41) | Posterior face of the cricoid lamina, 4 mm above its lower border to 2.5 mm below its top, 3.2–9.5 mm lateral of the ridge (narrowing upward) → posterolateral base of the arytenoid (muscular process); 70 fibres | 376 / 387 mm³ | 230 mg embalmed; ~0.7 × cricothyroid | 5.7 mm gap between the two muscles at the ridge (Tubbs 2005: 5), 3.8 mm bare strip along the inferior border (Goding & Bierbaum 1999: ~4), height 22 mm (Tubbs 19–20, men 21). 2.6 mm thick at the belly. Lower-medial fibres run vertically, upper ones horizontally to the muscular process: the two bellies of Bryant 1996, as one body. |
| Lateral cricoarytenoid (42, 43) | Upper border of the cricoid arch, lateral part (58–80° from the anterior midline, y −102.5..−98.6) → anterior face of the muscular process; 20 fibres | 83 / 74 mm³ | 61–63 mg embalmed | Lateral to the conus and inside the thyroid lamina; that slot is about 2 mm wide here, so the muscle is a 1.4 mm strap (median) and about half of what was built is trimmed by the conus, lamina and cricoid. 18–19 mm long, rising 38°. |
| Cricothyroid, straight part (44, 45) | Front of the arch, 24–38° from the midline, from 1.5 mm above the lower border to the rim → lower border and adjoining outer surface of the thyroid lamina, 4.5–9 mm from the midline; 30 fibres | 312 / 320 mm³ | Cox 1999: whole muscle 890 mm³ (0.94 g), 73.8 mm² | Vertical (83°). The median cricothyroid ligament stays exposed over 7.4 mm between the two straight parts. |
| Cricothyroid, oblique part (46, 47) | Outer surface of the arch, 36–58° from the midline, lower 7.5 mm → anterior border of the inferior horn, ending flush with a plane fitted to that border; 30 fibres | 411 / 435 mm³ | | Rises 28° backward to the cricothyroid joint. Whole cricothyroid 722 / 755 mm³ per side, 2.9–3.1 mm thick (median), 39–42 mm² cross-section: 80 % of Cox's mass, 55 % of his cross-section. |
| Thyroarytenoid (24, 25) + vocalis (26, 27) | Inner surface of the thyroid angle, 1.5–5 mm from the midline, 4.5 mm below to 4 mm above the ligament → lateral surface, vocal process and muscular process of the arytenoid, 1–8 mm above its base; 72 fibres | TA 188 / 172, vocalis 213 / 233; together 401 / 404 mm³ | Hamdan 2020, men: 860–890 mm³, 24.4–25 × 6.8 × 10.5 mm | Length 22–23 mm, height 11 mm, width up to 9.5 mm: the dimensions are near the reference but the body is a wedge between the conus, the lamina and the arytenoid, and that space holds half the reference volume. Lateral to the ligament (touching it) and to the conus, never in the airway; the vocalis is the medial compartment over the full fold height and reaches the thyroid; its medial edge above the ligament stands 0.8 mm back for the stage-3 cover. |
| Thyro-epiglottic part (48, 49) | Upper sheet of the source thyroarytenoid (FJ2803/FJ2785), fold level to the epiglottis margin, now tied to the inner thyroid lamina by ten short fibres | 265 mm³ | | Source geometry (warped in stage 1); large for a slip. |
| Transverse arytenoid (28) | Posterior surfaces of both arytenoids (source, scaled 1.9× with the arytenoids) | 254 mm³ | | Unchanged. |
| Oblique arytenoids (29, 30) | Muscular process of one arytenoid → apex of the other and the lower end of the opposite aryepiglotticus; 3 fibres each, over the back of the transverse arytenoid, left behind right at the crossing | 120 / 141 mm³ | | Rebuilt: the source bands (50 mm³) touched neither arytenoid. |

Muscle in total: 4.34 cm³ (2× build), 4.22 cm³ (1:1 build); v3 had 1.3 cm³ of strips.

### Measurements, v3 → v4

| Quantity | v3 | v4 | Reference |
|---|---|---|---|
| Named parts | 37 | 49 | — |
| Union volume (2× build / 1:1 build) | 16 130 / 16 012 mm³ | 18 811 / 19 204 mm³ | — |
| Glottis area / length / width | 145 / 24.4 / 8.5 | 145 / 24.4 / 8.6 | 126–141 / 22.1 ± 3.1 / 10 ± 6 |
| Subglottic lumen | 16.0 × 16.9, 221 mm² | same | ~16 × 17.4 |
| Largest sphere through the airway | 7.8 mm | 7.8 mm | — |
| Surface < 0.4 / 0.8 / 1.2 mm, 2× build | 0.3 / 1.3 / 20.7 % | 0.2 / 1.0 / 14.6 % | — |
| Surface < 0.4 / 0.8 / 1.2 mm, 1:1 build | 0.2 / 0.9 / — | 0.2 / 0.6 / 6.6 % | — |
| Cricothyroid per side | absent | 722–755 mm³ | 890 mm³ (Cox 1999) |
| Thyroarytenoid complex per side | 360 mm³ (strips) | 401–404 mm³ | 860–890 mm³ (Hamdan 2020) |

### Independent review

Three passes by a reviewer agent that had not seen the build. The first pass found four must-fix errors: a third of each lateral cricoarytenoid lay medial to the conus (in the subglottic wall), a strand of the left oblique arytenoid crossed the posterior glottis in front of the transverse arytenoid, the vocalis and one cricothyroid had detached fragments medial to the conus below the anterior commissure, and the cricothyroid obliqua wrapped the inferior horn and ran on behind the joint against the PCA; it also found the TA/vocalis split was a top/bottom layering, the cricothyroid 60 % of reference mass, the thyro-epiglottic sheet unattached to the thyroid, and the PCA a vertical slab. The enclosed-lumen clip, the LCA origin move, the oblique-arytenoid rebuild, the cricothyroid thickening and horn clip, the TA re-split and the thyro-epiglottic bridge came from that pass. The second pass confirmed every must-fix item resolved (ray test: 0 % of any muscle faces the airway below the free edge; no fragments; cricothyroid 83–87 % of reference) and the third pass confirmed no regression. Residuals are below.

### Open items from the review

- Posterior cricoarytenoid reads as a vertical slab with a bulge, not a fan converging on the muscular process; its arytenoid insertion is a 1 mm line and its top abuts the facet pad and the transverse arytenoid. Cause: the muscular process sits only 3 mm above the lamina top in this framework (a stage-1 arytenoid/lamina relation), so the upper fibres are short and horizontal. Revisit with the framework.
- Cricothyroid obliqua still laps around the lateral face of the inferior horn to its posterior edge at z 36–38.5 (18–26 mm³ behind the horn-tip plane) and its posterior tip comes within 0.3 mm of the PCA over 2–3 % of its surface.
- The vocalis ended up the larger compartment (53–57 % of the TA complex against the intended 35 %) because of the 1.2 mm minimum-thickness rule in the narrow posterior half, where the thyroarytenoid is a thin lateral shell (2–3 mm² cross-section at y −96); 15 % of the vocalis surface is thinner than 0.6 mm at the feathered edges against the conus.
- Lateral cricoarytenoid: 82 / 74 mm³ with tapered ends and a feather edge against the conus (16–18 % of its surface thinner than 0.6 mm); cross-section 3.5–4.1 mm².
- Thyroarytenoid complex at 47 % of the MRI volume: the paraglottic space is the limit (thyroid about 10 % narrow; the conus flares to the lamina at the fold level).
- Thin sheets at 1×: vocalis, LCA, transverse arytenoid and TA each have 14–18 % of their surface thinner than 0.6 mm (1.2 mm at 2×). Harmless in the single-material union (1.0 % of the whole surface is under 0.8 mm), relevant only if parts are ever printed separately.
- The thyro-epiglottic part (265 mm³ per side) is large for a slip; source geometry. The left oblique arytenoid stands 3.7 mm behind the transverse at the crossing (a visible bump).

### Files

Folder `Documents\Blender\Larynx life-size\`, sliced copies in `sliced - ready to print\`. Muscle has its own filament slot (5, red), so the multi-colour files are 5-colour; the A1 mini's AMS lite needs one manual change, or merge muscle into slot 4 in Bambu Studio.

| File | Scale | Bambu Studio estimate |
|---|---|---|
| `Larynx_v4_2x_whole_1colour.3mf` | 2× (162 mm tall) | 10 h 56 min, 174 g |
| `Larynx_v4_2x_halves_1colour.3mf` | 2×; pins 16 mm hyoid, 10 mm cricoid | 13 h 31 min, 167 g |
| `Larynx_v4_2x_whole_5colour.3mf` | 2× | 71 h 57 min, 903 g, 1923 colour changes (mostly purge) |
| `Larynx_v4_2x_halfR_5colour.3mf` | 2×, one half per file | 31 h 10 min, 372 g, 784 colour changes (mostly purge) |
| `Larynx_v4_2x_halfL_5colour.3mf` | 2×, one half per file | 31 h 13 min, 373 g, 785 colour changes (mostly purge) |
| `Larynx_v4_lifesize_whole_1colour.3mf` | 1:1 (81 mm) | 2 h 33 min, 27 g |
| `Larynx_v4_lifesize_halves_1colour.3mf` | 1:1; pins 7.5 / 4.5 mm | 3 h 06 min, 30 g |
| `Larynx_v4_lifesize_whole_5colour.3mf` | 1:1 | 33 h 53 min, 407 g, 963 colour changes (mostly purge) |
| `Larynx_v4_lifesize_halves_5colour.3mf` | 1:1 | 15 h 19 min, 176 g, 392 colour changes (mostly purge) |

### Method notes

`pipeline6.sh`: `deform5.py` (stage-1 settings) → `muscles6.py` (airway exclusion, then all muscles, then `grid`) → `vox.py` for the source parts → `stage1b_trachea.py` (MATCH=lumen) → `stage5_sdf.py` (HE_SCULPT=1 LIG_H=3.5 SEAM=-2.0 LUMEN_BLEND=10 UNION_SEPARATE=1 NO_MERGE=1, OFFSCALE 0.5 for 2× or 1.0 for 1:1) → `union_only.py` → `qa_anat.py`, `qa_print.py`, `qa_muscles.py`. `pipeline6b.sh` re-assembles after a muscle change; `pipeline6c.sh` does 2× then 1:1 (never both at once on the 8 GB box, and never alongside a reviewer's mesh jobs: that is what killed two runs). Muscle settings are environment variables in `muscles6.py` (PCA_*, LCA_*, CT_*, TA_*, OA_*, TE_*); the defaults are what was built. `build3mf.py` takes NSLOT (5 puts muscle on its own slot; 4 merges it with the ligaments). `partsconfig_v3.py` is the stage-1 part table.

---

## Version 3, stage 1: framework and joints (2026-10-18)

The first of five planned stages (framework and joints; intrinsic muscles; fold and supraglottic tissues; alternative poses; teaching features). Built for a 2× print for vocal-pedagogy use; also exported at 1:1. Every change below is constructed geometry steered by published adult-male dimensions, not scan data. An independent reviewer that had not seen the build checked it twice; its residual findings are under "Open items".

### Files

Folder `Documents\Blender\Larynx life-size\`, sliced copies in `sliced - ready to print\`. 37 named parts: v2's 32 plus the cricotracheal ligament, two posterior cricoarytenoid ligaments and two cricoid facet pads.

| File | Scale | Bambu Studio estimate |
|---|---|---|
| `Larynx_v3_2x_whole_1colour.3mf` | 2× (162 mm tall) | 9 h 02 min, 152 g |
| `Larynx_v3_2x_halves_1colour.3mf` | 2×; pins: 16 mm hyoid, 10 mm cricoid (2.0 mm holes, 8 and 5 mm deep per side, ≥ 2.7 mm wall) | 12 h 17 min, 151 g |
| `Larynx_v3_2x_whole_4colour.3mf` | 2× | 50 h 23 min, 1279 colour changes, ~638 g (mostly purge) |
| `Larynx_v3_2x_halfR_4colour.3mf`, `..._halfL_4colour.3mf` | 2×, one half per file (two halves plus the wipe tower do not fit the bed) | 24 h 31 min / 24 h 37 min, about 590 changes and 288 g each |
| `Larynx_v3_lifesize_whole_1colour.3mf` | 1:1 | 2 h 05 min, 23.5 g |
| `Larynx_v3_lifesize_halves_1colour.3mf` | 1:1; pins 7.5 / 4.5 mm | 2 h 49 min, 27.6 g |
| `Larynx_v3_lifesize_whole_4colour.3mf` | 1:1 | 23 h 17 min, 644 changes, ~280 g |
| `Larynx_v3_lifesize_halves_4colour.3mf` | 1:1 | 12 h 02 min, 295 changes, ~135 g |

The 2× files use half of v2's print-minimum thickening (0.6 mm life-size, 1.2 mm printed); the 1:1 files use the full thickening.

### What changed and why

1. **Thyroid deepened 12 % front-to-back** about the laryngeal prominence (superior horn tips 8 %). The source lamina measures 28–33 mm along the plate against 37.7 ± 3.4 mm in men (Jotz 2014, n = 50); as first built it could not contain a normal-size cricoid and arytenoids (the arch sat flush with the thyroid's lower edge and the arytenoid bodies 3.4 mm behind its posterior border). Now 33–36.5 mm. The hyoid was not scaled: its depth (35.3 mm) matches male CT norms (33–34 mm), so scaling it would have made it wrong.
2. **Cricoid placed, not scaled.** Its front face is set 2.5 mm behind the thyroid's lower edge and its back face 1 mm behind the thyroid's posterior border (AP 25.3 mm). Width ×1.08 at the ring rising to ×1.30 at the top of the lamina so the cricoarytenoid facets sit 12.1 mm apart (Burckardt 2021: 11.8; Randestad 2000: 12.6). Lamina lengthened to 21.4 mm and arch dropped 6 mm as in v2. Subglottic lumen 16.0 wide × 16.9 deep (median depth 17.3; cadaver men 17.4 ± 2.3 deep, deeper than wide).
3. **Arytenoids enlarged** ×1.25 medial-lateral, ×1.55 front-to-back, ×1.9 vertical about each facet contact: vocal process to apex 9.4 → 16.1 mm (men 16.2–17.5 across several series), vocal to muscular process 11.8 (11.6 ± 1.0), volume 70 → 270 mm³. A facet pad (convex hull of the base, extruded 4 mm down, clipped at the lamina's inner face so nothing hangs over the lumen) fills the lamina shoulder under each base; 96 % of each underside is within 0.3 mm of cartilage. They rock 9° about the facet's long axis (35° below horizontal, 30° from the sagittal plane, so the two axes meet at 60°, inside Randestad's 37–75°).
4. **Glottis** 145–153 mm² at its narrowest, 24.4 mm long, 8.5 mm wide at the vocal processes, inscribed circle 8.0 mm; largest sphere through the airway 7.8 mm (1:1). Brancatisano 1983 (tidal breathing, n = 12): width 10.1 ± 5.6 mm inspiration / 5.7 ± 0.5 expiration, area 126 ± 8 / 70 ± 7 mm². Vocal ligament 15.1 mm, straight within 0.36 mm.
5. **Cricotracheal junction.** The tracheal lumen morphs into the cricoid lumen over its top 10 mm (radii match within 0.1 mm at the border); a cricotracheal ligament tube 3.5 mm tall bridges the cricoid's lower border to ring 1; the trachea's outer surface is inset so the cricoid stands proud like a signet ring. v2's 1–3 mm shelf is gone.
6. **Hyo-epiglottic ligament** rebuilt as a 9 × 2.5 mm band with a rounded section from the posterior surface of the hyoid body (just below its upper border) to the anterior face of the epiglottis, clipped 0.4 mm into the 1 mm-thick plate so it cannot break through.
7. **Posterior cricoarytenoid ligaments** added as 0.8 mm cords from the posterior-medial base of each arytenoid to the lamina medial-posterior to the facet (for the adducted pose later). They are buried in the transverse arytenoid until stage 2 reshapes that muscle.
8. **Cricothyroid joints** fused: the inferior horns are re-seated on the moved facets and the union is at least 2.1 mm thick through the joint. **Median cricothyroid ligament** now follows the conus blend; the seam is 1 mm at most, with no hole.

### Measurements, v2 → v3 stage 1

| Landmark | v2 | v3 | Reference |
|---|---|---|---|
| Thyroid lamina along the plate | 28–33 mm | 33–36.5 mm | 37.7 ± 3.4 (Jotz 2014) |
| Thyroid posterior border vs cricoid back face | 0.7 mm in front | 1.3 mm in front | lamina at or just behind the border |
| Arytenoid backs vs thyroid posterior border | level | 0.3 mm inside | about level |
| Cricoid outer width (ring / lamina top) | 22.9 / 20 | 24.8 / 22.8 | lamina 27–31 |
| Cricoarytenoid facets apart | 9.6 | 12.1 | 11.8–12.6 |
| Cricoid lamina height | 21.4 | 21.4 | 21.2–25.2 (series vary) |
| Subglottic lumen, wide × deep | 14.9 × 15.6 | 16.0 × 16.9 | about 16 × 17.4 |
| Trachea lumen 6 mm above the cut | 18.5 × 18.1 | 17.7 × 18.0 | index about 1 |
| Arytenoid vocal process to apex | 9.4 | 16.1 | 16.2–17.5 |
| Glottal area / length / width | 139 / 21.8 / 10.3 | 145–153 / 24.4 / 8.5 | 126–141 / 22.1 ± 3.1 / 10 ± 6 |
| Vocal ligament | 16.0 | 15.1 | 13.8–18 |
| Cricothyroid gap | 8.7 | 8.7 | 7.9 ± 2.2 |
| Surface < 0.4 / < 0.8 mm (life-size) | 0.13 / 0.51 % | 0.3 / 1.3 % (2× build), 0.2 / 0.9 % (1:1 build) | — |

### Open items from the review

- Muscular process to thyroid posterior border 4.0–4.2 mm against 8.1 ± 1.2 mm in one CT series (Huangfu 2010); the arytenoids sit near the back edge of the thyroid shield.
- Hyoid greater-horn tips are 2 mm in front of the thyroid superior-horn tips (level with or behind them in life); scaling the hyoid 6 % would fix it but its depth is already normal.
- The vocal process rises only 3° above the anterior commissure; in-vivo CT favours 7–14°.
- Glottal width is mid-tidal while the area is at the inspiratory end, because the folds have no body (stage 3).
- The facet pads are constructed shapes; their underside is not filleted into the lateral wall.
- Conus–median cricothyroid ligament seam of about 1 mm from 40 to 46 mm up.

### Method notes

`deform5.py` (G 1.12, G_HORN 1.08, SX 1.30, SX_RING 1.08, ARCH_SETBACK 2.5, LAMINA_BEHIND 1.0, SA 1.25/1.55/1.9, ALPHA 9, AX_AZ 30, AX_EL 35, TRACHEA_DZ 2.2), then `vox.py`, `stage1b_trachea.py` (MATCH=lumen), `stage5_sdf.py` (HE_SCULPT=1 LIG_H=3.5 SEAM=-2.0 LUMEN_BLEND=10, OFFSCALE 0.5 for 2× or 1.0 for 1:1, UNION_SEPARATE=1), `union_only.py`, `build3mf.py` (SCALE 2 or 1, V2=1). The union is built in a separate process; on an 8 GB box, do not run other mesh jobs alongside stage 5.

---

## Version 2: breathing-position glottis and corrected cricoid

Built 2026-10-18 at Brandon's request ("Both changes"). Version 1 files are unchanged; version 2 sits next to them with `_v2` in the name.

### Files

| File | What it is | Bambu Studio estimate |
|---|---|---|
| `Larynx_lifesize_v2_whole_1colour.3mf` | Intact model, upright. Supports on the build plate only. | 1 h 45 min, 19.9 g |
| `Larynx_lifesize_v2_halves_1colour.3mf` | Mid-sagittal halves, cut face up. 2.0 mm pin holes: hyoid 4.0 mm deep per side (pin 7.5 mm), cricoid lamina 2.5 mm per side (pin 4.5 mm). Each hole keeps at least 0.55 mm of cartilage around it. | 2 h 27 min, 23.8 g |
| `Larynx_lifesize_v2_whole_4colour.3mf` | Intact, colour-coded by tissue (AMS lite) | about 23 h, 656 colour changes, about 282 g total |
| `Larynx_lifesize_v2_halves_4colour.3mf` | Halves, colour-coded | about 11 h 42 min, 294 changes, about 132 g total |

All four sliced in Bambu Studio 02.08.02.61's command-line slicer with no warnings. Same print settings and colour key as version 1.

### What changed and how

1. **Glottis opened to quiet breathing.**
   - Each arytenoid (with its corniculate) rocks 29° about the long axis of its cricoarytenoid facet. The axis is set 35° below horizontal and 45° from the sagittal plane, running anterolaterally downward, 3 mm below the contact patch. This follows the modern account of the joint: abduction is mainly rocking on the facet, with only a small pivot about a vertical axis.
   - Result: the vocal process moves 2.8 mm out, 1.9 mm up and 0.9 mm back, and the arytenoid tips move apart (corniculates about 8 mm apart, v1 about 4 mm). The arytenoid base stays seated on the cricoid.
   - Soft tissue between the anterior commissure and the vocal process (vocal ligament, vocalis/thyro-arytenoid, upper conus) is displaced linearly along the fold, so the free edge stays straight. It blends into the arytenoid's rigid motion over the last 20% next to the vocal process. Interarytenoid muscles are interpolated between the two arytenoids; the aryepiglottic folds and cuneiforms follow with a vertical fade.
   - A first draft rotated about a vertical axis (the textbook pivot). That drew the arytenoid tips together until the corniculates touched, so it was replaced. A second draft used a smoothstep blend that bowed the vocal folds outward by about 1 mm; the independent review caught it. The bow was supplying 15–20 mm² of the area.
2. **Cricoid corrected.**
   - The source cricoid mesh was warped smoothly (no voxel operations; an earlier voxel-column version left visible striations and terracing):
     - The lower border moves to one level all round, 7 mm below the old anterior border.
     - The anterior arch drops 6 mm as a unit, which keeps its height and opens the cricothyroid space. The drop is full within 20° of the midline and tapers to zero by 100°.
     - The lamina top, arytenoid facets and cricothyroid facets keep their heights. The lamina stretches in a band above its rounded lower edge.
   - The ring is scaled ×1.2 front to back about its centre to deepen the subglottis. This is a third change in effect: the lamina, arytenoid facets and arytenoids move about 1.2–2.4 mm backward and the arch about 1.8 mm forward. It is most of why the vocal ligament grew from 13.2 to about 15.5 mm.
3. **Trachea.**
   - Rescaled ×1.08 side to side and ×1.48 front to back to meet the new ring.
   - Moved down 1.2 mm so a cricotracheal band (annular-ligament tissue) sits under the cricoid; without that move ring 1 fused to the cricoid.
   - The overlap seam where the trachea meets the cricoid is 0.35 mm (v1 0.6 mm). This shrinks a feather-thin lip on the front of the band from 6.3 to 3.4 mm² of surface under 0.4 mm (v1 had 1.1 mm² there). A 0.2 mm seam thinned it further but left pinch edges in the merged model.
   - The model is 7 mm taller (80.9 mm).

### Measurements, v1 → v2, against adult male norms

| Landmark | v1 | v2 | Reference |
|---|---|---|---|
| Glottal area at the narrowest level | 73 mm² | 139 mm² | 140.7 ± 8.6 mm² quiet breathing (ultrasound); 217 ± 54 mm² peak inspiration |
| Largest circle in the glottis | 4.6 mm | 9.4 mm (9.2 mm 0.25 mm higher) | Ambu aScope 4 Large is 5.8 mm |
| Largest sphere from trachea through glottis | 5.3 mm | 8.8 mm | 6.0 ETT outer diameter is 8.2 mm (tubes not tested; expect them to jam in a rigid print) |
| Glottis length | 19.1 mm | 21.8 mm | 22.1 ± 3.1 mm |
| Vocal processes apart / anterior angle | — | about 9.9 mm / about 37° | Plausible for quiet breathing, at the wide end |
| Vocal ligament length | 13.2 mm | 15.2–16.1 mm (method-dependent) | 13.8 ± 2.9 to 16–18 mm |
| Cricoid lamina height | 12.2 mm midline, 15.4 at ±6 mm | 21.4 mm midline, 23.1 at ±6 mm | 21.5 ± 2.0 to 24.5 ± 2.8 mm |
| Anterior arch height | 5.4 mm | 6.3 mm | |
| Cricothyroid gap, midline | 2.6 mm (same method; the v1 note's 3.8 mm used an earlier method) | 8.7 mm | 7.9 ± 2.2 mm (CT) |
| Subglottic lumen depth × width | 12.0 × 15.0 mm | 15.6 × 14.9 mm | Depth 17.4 ± 2.3 mm (cadaver); depth ≥ width |
| Vocal folds to cricoid lower border | 17.5 mm | 24.6 mm | 25.9 ± 3.8 mm |
| Hyoid body to cricoid lower border | 42.4 mm | 49.5 mm | 53.5 ± 6.1 mm (MRI) |
| Trachea lumen width × depth | 18.4 × 13.3 mm (index 1.39) | 18.5 × 18.1 mm (index 1.02) | Index about 1 |
| Cricoid lower border to tracheal ring 1 | 0.5–1.7 mm | 0.6–1.8 mm | Cricotracheal ligament |

Printability:
- 0.13% of the surface is thinner than 0.4 mm and 0.51% thinner than 0.8 mm (v1: 0.09% and 0.57%).
- 0.04% of layer area is narrower than one 0.42 mm line.
- Every airway layer from 0 to 30 mm closes.
- All 32 parts are watertight, and the merged model is one watertight body.

### Independent review

A separate reviewer agent that had not seen the build checked the meshes twice.
- **First pass, found:** outward-bowed vocal folds; ring 1 fused to the cricoid, with one non-manifold edge there; and too abrupt a step where the lowered arch meets the side wall. All three were fixed and re-verified. The second pass found a feather-thin lip on the cricotracheal band, which a smaller seam reduced.
- **Left as is (minor):**
  - A 0.3 mm dog-leg where the vocal ligament meets the vocal process.
  - A rim that is still fairly pointed at x ≈ ±6 mm where the arch rises.
  - The cricothyroid window walls look nearly vertical from the front.
  - The lower posterolateral corners of the cricoid look extruded.
- **Wider than v1:** the thyro-arytenoid muscle's back end now swings away from the conus, leaving a gap of up to about 3 mm. This is the v1 "hollow fold" limitation, made wider: the source has no lateral cricoarytenoid or paraglottic fat to fill it.
- **Cosmetic:** small 1–1.5 mm through-holes in the back of each conus near the vocal process. The cricoid is behind them.

### Limitations specific to v2

- The new cricoid shape is a warp of the source, not scanned anatomy. The lamina height, gap and subglottic depth are steered toward published means; the shape between them is interpolated.
- The cricothyroid facets now sit about halfway up the side wall (v1 about a quarter). Real facets are probably lower. The source thyroid's inferior horns may be short, and the facets were kept where the horns meet them.
- The subglottis is still about 1 SD shallower than the cadaver mean.
- The arytenoids are 7.8 mm tall in the source. That may be small for an adult male, but I found no measured norm to check it against.
- The whole source larynx is on the small side: the thyroid is 16 mm tall at the midline, and the cricoid is 22.9 mm wide outside against about 27.5 mm posterior width in men.

### Known fault in v1

The v1 halves' cricoid pin hole breaks through the back of the lamina as a slot up to 0.45 mm deep along about 6% of its wall. v2 places holes by maximising the cartilage left around them.

### Method notes (for rebuilding)

- Scripts are in the session scratchpad:
  - `prep.py` → `deform3.py`. Its environment variables are ALPHA 29, AX_EL 35, AX_AZ 45, AX_R 3, Z_NEW 15, ARCH_A0 20, ARCH_A1 100, HF 1.5, HL 5, TRACHEA_DZ 1.2 and F_AP 1.2.
  - Then `vox.py` → `stage1b_trachea.py` → `stage5_sdf.py` (SEAM=0.35) → `qa_anat.py` / `qa_print.py`.
  - Then `build3mf.py` (V2=1, PREFIX=Larynx_lifesize_v2).
- `stage1b_trachea.py` now fits the trachea to the cricoid outline 2 mm above its rounded lower edge.
- `build3mf.py` merges vertices and drops zero-area faces when the part stays watertight. It also keeps manifold3d output unmerged, which avoids a false non-watertight on the halves.

---

# Version 1 (source anatomy)

## Files (version 1)

Location: `Documents\Blender\Larynx life-size\` on Brandon's PC. Ready-to-print sliced versions are in `sliced - ready to print\`.

All four project files are set up for the A1 mini (0.4 nozzle) with PLA Basic, and each was sliced successfully in Bambu Studio 02.08.02.61's command-line slicer.

| File | What it is | Bambu Studio estimate |
|---|---|---|
| `Larynx_lifesize_whole_1colour.3mf` | Intact model, upright. Supports on the build plate only, so none inside the airway. | 1 h 38 min, 17.4 g |
| `Larynx_lifesize_halves_1colour.3mf` | Mid-sagittal halves printed cut face up, so the inside surfaces stay support-free. Each half has 2.0 mm pin holes (hyoid body 4 mm deep, cricoid lamina 3.2 mm deep); use 1.75 mm filament pins cut to 7.5 mm and 6.0 mm. | 2 h 08 min, 20.3 g |
| `Larynx_lifesize_whole_4colour.3mf` | Intact, colour-coded by tissue (AMS lite) | about 22 h, 633 colour changes, about 269 g total |
| `Larynx_lifesize_halves_4colour.3mf` | Halves, colour-coded | about 11 h, 289 changes, about 128 g total |

Colour key:
- Beige: bone.
- Cyan: hyaline cartilage (thyroid, cricoid, arytenoids, tracheal C-rings).
- Yellow: elastic cartilage (epiglottis, corniculates, cuneiforms).
- Pink: ligaments, membranes, the tracheal membranous wall and annular ligaments, and the vocal-fold and interarytenoid muscles.

The four-colour prints change filament on almost every layer, so most of their filament goes to purge.

## Print settings

These are the saved settings, changed from the original file:
- Wall generator: Arachne.
- Walls: 3.
- Layer height: 0.16 mm.
- Supports: tree (auto) at 30°. On the build plate only for the intact model; on everywhere for the halves.
- Brim: 5 mm, outer only.

The intact model has about 56 mm² of interior ceiling flatter than 70° with no support. The largest single patch is about 9 mm², small enough to bridge.

## Source and method

- **Source:** BodyParts3D 4.0 (DBCLS), licensed CC BY 4.0 since 2025-02-27. It is one adult male dataset in millimetres, and all parts sit in their native body coordinates. The OBJ headers inside the archive still show the older CC BY-SA 2.1 JP notice; the current licence page governs.
- **Parts:** 32 named parts:
  - Hyoid.
  - Thyroid, cricoid, arytenoids, corniculates, cuneiforms and epiglottis.
  - About 22 mm (5 rings) of trachea, split into C-rings, annular ligaments and the membranous wall.
  - Vocal ligaments, conus elasticus, median cricothyroid ligament.
  - Thyrohyoid membranes, median and lateral thyrohyoid ligaments.
  - Hyo-epiglottic and thyro-epiglottic ligaments.
  - Thyro-arytenoid (with vocalis merged in), transverse and oblique arytenoids, aryepiglotticus.
- **Processing steps:**
  - The source meshes are low-poly (99% polygon reduction), so they were smoothed by Loop subdivision plus Taubin. This changes volume by less than 3% (up to about 8% on the tiny cuneiform and corniculate cartilages).
  - The whole model was rotated 6.4° so the trachea stands vertical.
  - Each part was voxelised at 0.1 mm by winding number.
  - Overlaps were resolved by priority (bone and cartilage over soft tissue).
  - Surfaces were rebuilt from exact signed-distance fields. Decimation deviation is 0.01 mm at the 99th percentile.

## Deliberate changes from the source

1. **Trachea hollowed.** The source trachea is a solid rod. It now has a 2.0 mm wall (CT normal is 1–3 mm), with a smooth lumen and the rings on the outside.
2. **Trachea seated under the cricoid.** In the source, the top of the trachea sat about 8 mm up inside the cricoid. It was trimmed to the cricoid's lower border, traced around the full ring, with a 0.6 mm seam standing in for the cricotracheal ligament. The first version trimmed by column and left a 2 mm posterior ledge inside the subglottis; the independent review caught it and it is fixed.
3. **Trachea widened to meet the cricoid.** The cross-section was scaled ×1.07 side-to-side and ×1.15 front-to-back so it continues the cricoid's lower ring. Without this the lumen would be about 16.8 × 11 mm.
4. **Trachea split by tissue.** The rings are cartilage. The membranous wall is defined as the sector where the outward normal points within about 45° of posterior. The annular ligaments are the wall behind ring grooves deeper than 0.3 mm.
5. **Hyo-epiglottic ligament trimmed.** The source models it as a 23 mm midline web filling the pre-epiglottic space. It was cut to the band at hyoid level, above the hyoid body's lower border; the pre-epiglottic space below it is fat in life and is now open.
6. **Print-minimum thickness of 1.2 mm.** Each thin part was offset outward by a fixed amount:

| Part | Offset |
|---|---|
| Epiglottis | +0.25 mm per side |
| Thyrohyoid membranes, median thyrohyoid ligament | +0.2 mm per side |
| Hyo-epiglottic ligament | +0.3 mm per side |
| Oblique arytenoids | +0.3 mm per side |
| Corniculates | +0.2–0.25 mm per side |
| Conus elasticus | +0.7 mm, one side only, away from the airway |
| Median cricothyroid ligament | +0.4 mm, one side only, away from the airway |

   These structures are thicker than in life. The airway from the trachea to the glottis was never narrowed.
7. **Glottis left as in the source.** It sits in a semi-adducted position.

## Printability, before and after

| | Original MakerWorld file | Rebuild |
|---|---|---|
| Surface thinner than 0.4 mm | 3.9% | 0.1% |
| Surface thinner than 0.8 mm | 7.6% | 0.6% |
| Layer area narrower than one 0.42 mm line | 0.3% | 0.04% |
| Junction with ring that doesn't close | Layers at 24–29 mm don't close | All layers close |
| Mesh topology | Genus 596 plus a loose sliver | 32 clean watertight parts, one connected body |

## Measurements of the rebuild (life size) against published adult norms

### Within normal variation

| Landmark | Model | Reference |
|---|---|---|
| Thyroid angle | 81° | Men 74–78° ± 5–8°, women about 95° — male-typical |
| Thyroid lamina height | About 25.5 mm | Men 26.6 ± 2.9 mm |
| Thyroid superior-horn span | 38.6 mm | Men 41.5 ± 7.2 mm |
| Epiglottis length | 30.5 mm | 29.1 ± 0.5 mm |
| Hyoid greater-horn span | 37.7 mm | Published male means 36.6–46.1 mm (definitions differ) |
| Vocal ligament length | 13.2 mm | Low-normal (13.8 ± 2.9 mm in one CT series, 16–18 in others) |
| Rima glottidis length | 19.1 mm | About 1 SD below 22.1 ± 3.1 mm |
| Trachea lumen | 18.4 × 13.3 mm | Within the male range (coronal 13–25, sagittal 13–27 mm), but width/depth is 1.39 against a normal of about 1 |

### Undersized compared with published norms

These are inherited from the BodyParts3D cricoid, not introduced by processing. Don't call them typical.

| Landmark | Model | Reference |
|---|---|---|
| Cricoid lamina height | 12.2 mm midline, 15.4 mm at ±6 mm | 21.5 ± 2.0 to 24.5 ± 2.8 mm |
| Subglottic front-to-back lumen | 12.7–13.5 mm | Men 17.4 ± 2.3 mm (cadaver), about 19–21 mm (CT); norms have depth ≥ width, this model has depth < width |
| Cricothyroid gap | About 3.8 mm (2.6 mm with the version 2 method) | Men 7.9 ± 2.2 mm (CT) — a small window for cricothyrotomy landmarking |

### Other findings

- The glottis is semi-closed: area 74 mm², largest inscribed circle 4.5 mm, against about 140 mm² for quiet breathing in men.
- The largest sphere that passes from the trachea through the glottis is 5.3 mm. The Ambu aScope 4 Slim (3.8 mm) and Regular (5.0 mm) pass; the Large (5.8 mm) and every adult endotracheal tube do not.

## Source limitations still present

- **Vocal fold shape.** The vocal fold is a thin thyro-arytenoid strip above the conus rather than a solid wedge. The source has no mucosa, and its lateral cricoarytenoid muscle is too small to fill the space. The fold reads as a flap in cross-section.
- **Arytenoid cartilage type.** The arytenoid vocal process and apex are elastic cartilage in life but are coloured with the hyaline group.
- **Missing structures.** There is no tongue base or vallecula, pharynx, oesophageal inlet, vestibular folds as tissue, or mucosa.

## Possible next steps

- ~~A glottis variant in the respiratory (abducted) position.~~ Done in version 2.
- ~~A corrected cricoid.~~ Done in version 2 by warping the source. A CT segmentation (TotalSegmentator has cricoid, thyroid, hyoid and larynx-air classes) would still be better.
- ~~Fill the paraglottic space so the vocal fold is solid rather than a hollow strip.~~ Done in versions 4 and 5 above the fold level; the space below the folds and the pre-epiglottic space are still sealed voids.
- Stage 4: poses (adducted / phonatory and fully abducted glottis as separate static models).
- Stage 5: teaching features (labels, cut-aways, a sectioned fold showing the cover, ligament and muscle layers).
- Framework: raise the petiole so the thyro-epiglottic ligament attaches above the vestibular ligament; add a pharyngeal wall and piriform fossae if the model is to show the hypopharynx.
- A soft-tissue shell (vallecula, pharynx, oesophageal inlet).
- A flexible TPU or silicone insert at the vocal folds so tubes can pass.

## Sources

- [BodyParts3D licence](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html)
- [Joshi 2011, cricoid morphometry (W. India)](https://read.qxmd.com/read/23386865/morphometric-study-of-cricoid-cartilages-in-western-india)
- [Zieliński 2001, senile larynx morphometry](https://journals.viamedica.pl/folia_morphologica/article/download/16485/13119)
- [Holzmüller 2009 (meeting abstract), CT laryngeal dimensions](https://www.egms.de/static/en/meetings/hno2009/09hno036.shtml)
- [Cricothyroid membrane dimensions on CT](https://pearl.plymouth.ac.uk/handle/10026.1/9570)
- [Vocal fold and glottis length (Eur Arch ORL 2023)](https://link.springer.com/article/10.1007/s00405-023-08025-6)
- [Thyroid cartilage morphometry](https://nicpd.ac.in/ojs-/index.php/njirm/article/view/732)
- [Cameriere 2021, thyroid cartilage](https://doi.org/10.1186/s41935-021-00219-5)
- [Hyoid morphometry (Acta Med Iran)](https://acta.tums.ac.ir/index.php/acta/article/download/9635/5722)
- [Safaee 2025, hyoid on CT](https://publish.kne-publishing.com/index.php/ACTA/article/download/20678/19236)
- [Alicandri-Ciufelli 2020, hyoid to cricoid](https://old.actaitalica.it/article/view/503)
- [Laroia 2010, trachea on CT](https://wjgnet.com/1949-8470/full/v2/i7/237.htm)
- [Ambu aScope 4 Broncho](https://www.ambu.com/ascope-4-broncho)
- [Brancatisano 1983, glottal dimensions in tidal breathing](https://pubmed.ncbi.nlm.nih.gov/6643191/)
- [CT reconstruction of vocal folds and laryngeal cartilages, male arytenoid dimensions (PMC3834040)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3834040/)
- [Hyoid morphometry on neck CT, male AP about 33–34 mm (PMC3846888)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3846888)
- [Brancatisano 1983, glottal dimensions in tidal breathing](https://pubmed.ncbi.nlm.nih.gov/6643191/)
- [CT reconstruction of vocal folds and laryngeal cartilages, male arytenoid dimensions (PMC3834040)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3834040/)
- [Hyoid morphometry on neck CT, male AP about 33–34 mm (PMC3846888)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3846888)
- [Rai 2025, glottal area on ultrasound (quiet breathing)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12680824/)
- [Scheinherr 2015, glottal area in inspiration](https://doi.org/10.1016/j.medengphy.2015.05.014)
- [Yin & Zhang 2014, cricoarytenoid joint mechanics: rocking about the facet's long axis dominates](https://www.surgery.medsch.ucla.edu/spl/papers/2014JBME.pdf)
- [Utah vocology: 3-D laryngeal anatomy and arytenoid motion](https://vocology.utah.edu/_resources/documents/three_dimensional_anatomic.pdf)
- [Cox, Alipour & Titze 1999, geometry of the human cricothyroid and thyroarytenoid (Ann Otol Rhinol Laryngol 108:1151)](https://pubmed.ncbi.nlm.nih.gov/10605920/)
- [Hamdan 2020, thyroarytenoid dimensions and volume by MRI, men vs women](https://pubmed.ncbi.nlm.nih.gov/31018691/)
- [Joshi 2024, weights of the cricothyroid, posterior and lateral cricoarytenoid muscles (n = 50)](https://doi.org/10.18231/j.ijcap.2024.046)
- [Tubbs 2005, quantitative anatomy of the posterior cricoid region (PCA height, inter-muscle gap)](https://pubmed.ncbi.nlm.nih.gov/16425148)
- [Goding & Bierbaum 1999, posterior cricoarytenoid muscle and the posterior cricoid lamina](https://doi.org/10.1053/hn.1999.v120.a91407)
- [Bryant 1996, human posterior cricoarytenoid muscle compartments](https://pubmed.ncbi.nlm.nih.gov/8956745/)
- [Kitzing & Sonesson 1967, shape and shift of the laryngeal ventricle during phonation (ventricle ~3 mm tall, 14 mm long at rest)](https://www.lunduniversity.lu.se/lup/publication/e80321fa-47fa-4cc0-bec1-412408353293)
- [Saldarriaga 2016, asymmetry of the laryngeal ventricle, cadavers (depth 2.3–2.5 mm at mid-length)](https://www.researchgate.net/publication/311514363_Asymmetry_of_Laryngeal_Ventricle_A_Direct_Anatomical_Study_in_Cadavers)
- [Guida & Zorzetto 2007, morphology of the human vestibular fold](https://www.scielo.cl/pdf/ijmorphol/v25n3/art10.pdf)
- [Rothrock 1990, radiologic criteria for epiglottitis (normal aryepiglottic fold width under 7 mm)](https://doi.org/10.1016/s0196-0644(05)82557-0)
- [Medtronic Shiley ETT sizes](https://www.medtronic.com/content/dam/medtronic-wide/public/united-states/products/respiratory/shiley-endotracheal-tube-intermediate-cuff-information-sheet.pdf)

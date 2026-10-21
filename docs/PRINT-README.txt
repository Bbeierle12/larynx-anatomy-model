LARYNX (BodyParts3D 4.0 rebuild) - print notes
================================================

Six versions live in this folder. Newest first:

  Larynx_v6_2x_*        version 6, stages 3b and 3c (fat-filled spaces, saccules, joint capsules,
                        piriform fossae, constrictors, hypopharynx, oesophagus, tongue base), 2x
  Larynx_v6_lifesize_*  the same geometry at 1:1
  Larynx_v5_2x_*        version 5, wider framework + stage 3 (fold cover, false folds,
                        ventricle, membranes, aryepiglottic folds, tubercles), 2x life size
  Larynx_v5_lifesize_*  the same geometry at 1:1
  Larynx_v4_2x_*        version 4, stage 2 (all intrinsic muscles), printed at 2x life size
  Larynx_v4_lifesize_*  the same geometry at 1:1
  Larynx_v3_2x_*        version 3, stage 1 (framework and joints), 2x
  Larynx_v3_lifesize_*  the same geometry at 1:1
  Larynx_lifesize_v2_*  version 2 (open glottis, lengthened cricoid), 1:1
  Larynx_lifesize_*     version 1 (source anatomy), 1:1

All files are Bambu Studio projects for the A1 mini, 0.4 mm nozzle, Bambu PLA
Basic, test-sliced in Bambu Studio 02.08.02.61 with no warnings. The "sliced -
ready to print" folder has the sliced versions.


VERSION 6 - stages 3b and 3c: the spaces, the fossae and the hypopharynx -
what changed from version 5
---------------------------------------------------------------------------
The decision behind this version: show as much of the anatomy as possible,
and accept that the model becomes a solid block that has to be printed in
halves to be seen inside. 81 named parts (was 65). Everything new is
constructed from published dimensions except the two inferior constrictors,
which are BodyParts3D meshes warped onto the frame. An independent reviewer
that had not seen the build checked it three times after the clean rebuild; what it
still flagged is under "Known limits".

1. Framework. The epiglottis is lifted 5 mm (petiole and tip alike) so the
   thyro-epiglottic ligament attaches to the inner thyroid angle ABOVE the
   vestibular ligaments, as in life (v5 had the order inverted); the ligament
   sits on the floor of the thyroid notch. Leaf length unchanged (30.5 mm).
   The cricothyroid muscles are bedded onto the membrane and arch (no gap
   under them) and their oblique part fans onto the lower border of the
   lamina, which closes the lower paraglottic space from the outside.

2. Stage 3b - spaces, saccules, capsules, tendon.
   Pre-epiglottic fat  3.64 mL filling the space behind the thyrohyoid
       membrane and in front of the epiglottis, down to the false-fold tops.
   Paraglottic fat (R, L)  0.44 mL per side: the wing beside the
       quadrangular membrane, the pocket between the ventricle lining and the
       lamina, and the slit lateral of the conus under the fold. Total fat
       4.5 mL (CT in men: 4.5 +/- 1.0 mL for both spaces, Hermans 1997).
       Fat has its own colour (slot 7, yellow).
   Ventricle lateral walls (R, L)  Now a 0.8 mm mucosal lining of the
       ventricle with fat behind it (in v5 the whole slot out to the lamina
       was "mucosa").
   Saccules (R, L)  8 mm blind pouch rising from the front of each ventricle
       between the false fold and the lamina, lateral of the vestibular
       ligament, 1.6 tapering to 0.9 mm radius.
   Anterior commissure tendon (Broyles)  0.5-0.8 mm cone from inside the
       thyroid angle to the vocal ligaments' ends.
   Joint capsules (4)  0.8 mm sleeves on the joint line of both
       cricoarytenoid and both cricothyroid joints.

3. Stage 3c - piriform fossae and hypopharynx.
   Piriform fossae (R, L)  Open recesses lateral of the aryepiglottic fold,
       quadrangular membrane and arytenoid, medial of the lamina and
       thyrohyoid membrane, apex at the vocal-fold level; 1.73 cm3 each
       (cadaver about 1.8), lined with 0.8 mm of mucosa. They are 8.5-9.5 mm
       wide against 14-15 in life because this framework's lamina is close.
   Inferior pharyngeal constrictors (R, L)  BodyParts3D meshes warped onto
       the lamina (oblique line) and cricoid, meeting at the median raphe,
       continuous with the oesophagus below.
   Hypopharyngeal mucosa  The hypopharynx is collapsed in the source (the
       constrictor lies on the back of the larynx), so the mucosa is a 0.8 mm
       layer over the cricoid lamina, arytenoid backs and PCA wherever the
       constrictor lies within 2.5 mm, down to the oesophageal inlet: a slit,
       not an open lumen.
   Oesophagus (upper end)  Collapsed 20 x 9 mm muscular tube on the
       membranous trachea, base cut to the cricoid's lower border, with a
       12 x 1.4 mm slit lumen.
   Tongue base and vallecula  A flat-fronted block above the hyoid with the
       two vallecula pockets, the median glossoepiglottic fold and the lateral
       folds. A landmark for the laryngoscopic view, not a tongue.

Airway: glottis 99 mm2 between the covered folds, 7.7 mm inscribed
circle; a 7.5 mm ball still passes from the tracheal base up through the
glottis. The airway ring closes at every layer.

Known limits (reviewer's residual list after the second pass):
  - The thyro-epiglottic ligament's thyroid end sits in the notch 0.7 mm off
    the cartilage, held by the anterior vestibule wall; lowering it would put
    it level with the vestibular ligaments again.
  - The postcricoid mucosa meets the oesophageal inlet across a 0.4 mm seam
    and the arytenoid backs across a hairline; both close in the union.
  - Feather edges under 0.3 mm at 1:1 on the quadrangular membranes (50 mm2
    each), the ventricle linings and the vestibular mucosa: 0.6 mm at 2x.
    0.8% of the 2x surface is under 0.8 mm.
  - The piriform fossa apex sits against the back of the ventricle with one
    0.8 mm layer between (1.5-2 mm of paraglottic tissue would be typical),
    and the fossae are 8.5-9.5 mm wide against 14-15 in life.
  - The hypopharynx is collapsed: the constrictor lies directly on the
    larynx with the mucosa as an 0.8 mm layer between, not an open lumen.
  - The tongue base is a flat-fronted block; the constrictors' upper border
    reaches 8.6 mm above the hyoid (no middle constrictor yet); the oblique
    cricothyroid parts are asymmetric in the source (419 vs 496 mm3); the
    arytenoid medial faces below the vocal process are unlined (since v5).
  - A few embedded crumbs (two 5 mm3 pieces of the anterior vestibule wall,
    7 mm3 of the right ventricle lining) are harmless in the union.

VERSION 6 - files
-----------------
Seven filament slots: bone (beige), hyaline cartilage (cyan), elastic
cartilage (yellow), ligament and membrane (pink), muscle (red), mucosa
(salmon) and fat (sunflower yellow), so the multi-colour files are "7colour".
The AMS lite has four slots: merge slots in Bambu Studio to taste (fat into
elastic cartilage and mucosa into ligament are the least confusing merges) or
accept the manual changes. The 2x halves print lying on their cut face with
the long axis along the bed, one half per file, with the wipe tower in the
front-left corner.

Everything inside - fat, saccules, capsules, fossae, mucosa - is only visible
on the halves. The whole model prints as a block with the airway, vallecula,
fossae and oesophageal slit as its only cavities.

Honest reading of the estimates: the 7-colour files are purge-dominated now
that the block is solid (a 2x half is 13 h / 170 g in one colour and 53 h /
657 g in seven, with 1,325 changes). The practical print is the 1-colour
halves; merge to four slots or paint the cut face if colour matters.

2x scale (179 mm tall; the lifted epiglottis and tongue block add 17 mm):

Larynx_v6_2x_whole_1colour.3mf         23 h 04 min, 331 g
Larynx_v6_2x_halfR_1colour.3mf         13 h 09 min, 171 g
Larynx_v6_2x_halfL_1colour.3mf         13 h 10 min, 170 g
  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).
Larynx_v6_2x_whole_7colour.3mf         126 h 03 min, 1630 g, 3416 colour changes (mostly purge)
Larynx_v6_2x_halfR_7colour.3mf         52 h 56 min, 657 g, 1325 colour changes (mostly purge)
Larynx_v6_2x_halfL_7colour.3mf         52 h 57 min, 657 g, 1326 colour changes (mostly purge)
  (2x halves: one half per file since v6 - two halves side by side need 199 mm
  of the 180 mm bed. Each half lies on its cut face with the long axis along
  the bed, 178.8 mm, so there is no brim; the wipe tower is at the left edge.
  The whole 7-colour model is shifted 15 mm back to clear the tower.)

1:1 (89 mm tall):

Larynx_v6_lifesize_whole_1colour.3mf   5 h 25 min, 54 g
Larynx_v6_lifesize_halves_1colour.3mf  5 h 55 min, 60 g
  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).
Larynx_v6_lifesize_whole_7colour.3mf   60 h 10 min, 725 g, 1714 colour changes (mostly purge)
Larynx_v6_lifesize_halves_7colour.3mf  26 h 02 min, 307 g, 661 colour changes (mostly purge)


VERSION 5 - wider framework and stage 3 (vocal-fold cover and supraglottic
tissues) - what changed from version 4
---------------------------------------------------------------------------
Two changes. 65 named parts (was 49). An independent reviewer that had not
seen the build checked it three times; what it still flagged is under
"Known limits".

1. Framework widened. The thyroid is 10% wider (superior-horn span 42.4 mm,
   was 38.6; men 41.5 +/- 7.2; angle between the laminae 81 degrees, was 75)
   and the cricoid's outer wall 10% wider at the ring (27.2 mm, was 24.8;
   published 27-31) with its lumen, the arytenoid joints and the glottis
   left exactly as in v3/v4. The inferior horns were re-seated on the
   cricoid. The v4 muscles were regenerated on the wider framework.

2. Stage 3 tissues. BodyParts3D has none of these; every one is constructed
   from published dimensions and placed on the v5 framework:
   Vocal fold cover (R, L)  1 mm layer of lamina propria and epithelium over
       the airway side and top of the fold core (ligament, thyroarytenoid,
       vocalis, conus), from just in front of the anterior commissure to the
       vocal process. The glottis between the covered folds is 101 mm2,
       7.8 mm wide at the back (ligament to ligament it is still 145). A
       7.5 mm ball still passes the whole airway (was 7.8).
   Thyroarytenoid cap  The muscle now stops 1.8 mm above the ligament so the
       laryngeal ventricle lies above the fold (floor 2.8 mm above the free
       edge; air reaches 4.3 mm out under the false fold).
   Vestibular (false) folds (R, L)  5 mm thick, rounded free edge 2.2-2.5 mm
       lateral of and 5.6 mm above the true-fold edge (published: 4-6 thick,
       edge 2-4 lateral, 4-7 above), inner thyroid angle to the front of the
       arytenoid. Each has a 1 mm vestibular ligament inside it.
   Ventricle lateral walls (R, L)  Mucosa closing the space between the
       true and false folds 3 mm out from the fold edge, so the laryngeal
       ventricle is a real 3 mm slot rather than a gap open to the cartilage.
   Quadrangular membranes (R, L)  0.6 mm sheet (1.2 at 2x) from the
       vestibular ligament up to the aryepiglottic fold; the thyro-
       epiglottic muscle lies lateral to it.
   Vestibular mucosa (R, L)  0.8 mm lining on the airway side of the
       quadrangular membrane and over the arytenoid above the vocal process.
   Aryepiglottic folds (R, L)  4.4 mm mucosal fold from the arytenoid apex
       to the side of the epiglottis, with the cuneiform (5.4 mm) and
       corniculate (4.8 mm) tubercles on its top edge.
   Epiglottic tubercle  7 x 6.4 mm bulge, 2-2.7 mm proud of the laryngeal
       face of the epiglottis above the anterior commissure.
   Interarytenoid mucosa  1.2 mm layer over the front of the transverse
       arytenoid between the arytenoid bodies (the posterior commissure).

Known limits (reviewer's residual list after the fourth pass):
  - The thyro-epiglottic muscle is now only the upper strip lateral of the
    quadrangular membrane (100 mm3 per side, was 220) and touches the thyroid
    over 1.6 mm2.
  - The membrane cuts the source aryepiglotticus, leaving thin slivers
    (solid in the one-colour print).
  - The aryepiglottic folds read thick (4.4 mm against 2-4 in life) and the
    narrowest gap between them is 6.5 mm at the corniculate tubercles.
  - The vestibular ligament attaches to the thyroid angle above the thyro-
    epiglottic ligament (the petiole sits low in this framework; in life the
    order is reversed).
  - The interarytenoid mucosa is a flat plate with a square top; the
    membrane's upper front margin by the epiglottis is unlined.
  - Thin feather edges under 0.3 mm at 1:1 on the membranes, ventricle walls
    and vestibular mucosa (about 20 mm2 each); everything else is 0.6 mm or
    more. 1.4% of the whole 2x surface is under 0.8 mm.
  - The pre-epiglottic and lower paraglottic spaces are still voids, sealed
    off from the airway; no pharynx, vallecula or piriform fossae.
  - The ventricle is a real cavity (3 mm tall x 3 mm deep at 1:1), so the
    false-fold underside is a short bridge in an upright print.

VERSION 5 - files
-----------------
Mucosa and fold cover have their own slot (slot 6, salmon), so the multi-
colour files are "6colour". The AMS lite has four slots: merge slot 6 into
slot 4 (pink) and slot 5 into any other, or accept the manual changes.

2x scale (162 mm tall):

Larynx_v5_2x_whole_1colour.3mf         13 h 32 min, 202 g
Larynx_v5_2x_halves_1colour.3mf        16 h 34 min, 203 g
  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).
Larynx_v5_2x_whole_6colour.3mf         87 h 34 min, 1102 g, 2356 colour changes (mostly purge)
Larynx_v5_2x_halfR_6colour.3mf         39 h 43 min, 479 g, 1019 colour changes (mostly purge)
Larynx_v5_2x_halfL_6colour.3mf         40 h 02 min, 482 g, 1023 colour changes (mostly purge)
  (halves 6-colour: one half per file, lying on its side along the bed; the
  six-slot wipe tower sits in the front-left corner)

1:1 (89 mm tall):

Larynx_v5_lifesize_whole_1colour.3mf   3 h 07 min, 31 g
Larynx_v5_lifesize_halves_1colour.3mf  3 h 45 min, 35 g
  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).
Larynx_v5_lifesize_whole_6colour.3mf   41 h 22 min, 498 g, 1180 colour changes (mostly purge)
Larynx_v5_lifesize_halves_6colour.3mf  19 h 41 min, 228 g, 511 colour changes (mostly purge)


VERSION 4, STAGE 2 - what changed from version 3
------------------------------------------------
Second of the five stages: the intrinsic muscles. The framework, joints,
ligaments and airway are version 3 unchanged (glottis 145 mm2, subglottis
16.0 x 16.9 mm, a 7.8 mm sphere still passes). 49 named parts (was 37).
An independent reviewer that had not seen the build checked it twice.

The BodyParts3D muscles are placeholders 5-10x too small (and the source
cricothyroid sits in the wrong place), so every muscle below was rebuilt as a
bundle of fibres running between attachment areas on the version-3 cartilages,
sized from published data, with the source used only to confirm position and
fibre direction. They are constructed anatomy, not scan data.

  Posterior cricoarytenoid (R, L)  Posterior face of the cricoid lamina (leaving
      the 4 mm bare strip at the bottom and a 5 mm gap at the midline ridge) up
      to the muscular process of the arytenoid. 370-380 mm3 per side, 22 mm tall,
      2.4 mm thick.
  Lateral cricoarytenoid (R, L)  Upper border of the lateral arch to the front
      of the muscular process, lateral to the conus. Only 60-66 mm3: the slot
      between the conus and the thyroid lamina is 2 mm wide in this framework.
  Cricothyroid, straight part (R, L)  Front of the arch to the lower border of
      the thyroid lamina, 4.5-9 mm from the midline, so the median cricothyroid
      ligament stays exposed between them (7 mm window). 330 mm3 per side.
  Cricothyroid, oblique part (R, L)  Lateral arch back and up to the front edge
      of the inferior horn. 415-440 mm3. Whole cricothyroid 740-775 mm3 per
      side, 3 mm thick (published 890 mm3, 0.94 g).
  Thyroarytenoid (R, L) and vocalis (R, L)  Inner surface of the thyroid angle
      to the side of the arytenoid, lateral to the vocal ligament and conus,
      never in the airway. The vocalis is the medial third next to the ligament.
      Together 410 mm3 per side, about half the MRI value for men (860 mm3):
      the paraglottic space of this framework holds no more (the thyroid is
      about 10% narrow). To be revisited when the thyroid is widened.
  Thyro-epiglottic part (R, L)  The upper sheet of the source thyroarytenoid,
      now tied to the thyroid lamina with short fibres.
  Transverse arytenoid  Source, unchanged (across the backs of both arytenoids).
  Oblique arytenoids (R, L)  Rebuilt: muscular process of one arytenoid to the
      apex of the other, crossing on the back of the transverse, continuing into
      the aryepiglottic strips.

Known limits (reviewer's residual list after the second pass):
  - The posterior cricoarytenoid reads as a slab with a bulge, not a fan
    converging on the muscular process; its arytenoid insertion is a 1 mm line
    and its top abuts the facet pad and the transverse arytenoid. The muscular
    process sits only 3 mm above the lamina top in this framework (stage 1).
  - The cricothyroid oblique part still laps round the side of the inferior
    horn to its back edge and its tip comes within 0.3 mm of the PCA.
  - The vocalis came out larger than the rest of the thyroarytenoid (53-57% of
    the pair, intended 35%) because of its 1.2 mm minimum thickness in the
    narrow back half; the thyroarytenoid is a thin shell there.
  - Lateral cricoarytenoid 74-83 mm3 with tapered ends and a feather edge
    against the conus.
  - Thyroarytenoid + vocalis 400 mm3 per side, 47% of the MRI value: the
    paraglottic space is the limit until the thyroid is widened.
  - Thin sheets at 1:1: vocalis, LCA, transverse arytenoid and TA each have
    14-18% of their surface under 0.6 mm (1.2 mm at 2x). Harmless in the
    single-material print (1.0% of the whole surface is under 0.8 mm).

VERSION 4 - files
-----------------
Muscle has its own filament slot now (slot 5, red), so the multi-colour files
are "5colour". The A1 mini's AMS lite has four slots: Bambu Studio will ask for
one manual filament change, or you can merge muscle into slot 4 (pink) in the
filament list before slicing.

2x scale (162 mm tall):

Larynx_v4_2x_whole_1colour.3mf         10 h 56 min, 174 g
Larynx_v4_2x_halves_1colour.3mf        13 h 31 min, 167 g
  Pins: 1.75 mm filament cut to 16 mm (hyoid) and 10 mm (cricoid).
Larynx_v4_2x_whole_5colour.3mf         71 h 57 min, 903 g, 1923 colour changes (mostly purge)
Larynx_v4_2x_halfR_5colour.3mf         31 h 10 min, 372 g, 784 colour changes (mostly purge)
Larynx_v4_2x_halfL_5colour.3mf         31 h 13 min, 373 g, 785 colour changes (mostly purge)
  (halves 5-colour: one half per file, as in v3)

1:1 (89 mm tall):

Larynx_v4_lifesize_whole_1colour.3mf   2 h 33 min, 27 g
Larynx_v4_lifesize_halves_1colour.3mf  3 h 06 min, 30 g
  Pins: 7.5 mm (hyoid), 4.5 mm (cricoid).
Larynx_v4_lifesize_whole_5colour.3mf   33 h 53 min, 407 g, 963 colour changes (mostly purge)
Larynx_v4_lifesize_halves_5colour.3mf  15 h 19 min, 176 g, 392 colour changes (mostly purge)


VERSION 3, STAGE 1 - what changed from version 2
------------------------------------------------
This is the first of the five planned stages (framework and joints). Everything
below was checked twice by an independent reviewer; what it still flagged is
listed under "Known limits".

1. Whole framework below the hyoid deepened 12% front-to-back, about the
   laryngeal prominence. The source thyroid is shallow (lamina 28-33 mm along
   the plate; adult men 37.7 +/- 3.4) and could not hold a normal-size cricoid
   and arytenoids. Now 33-36.5 mm. The hyoid was left alone: its depth (35 mm)
   already matches the male norm (33-34).
2. Cricoid placed between the thyroid's lower edge (2.5 mm behind it) and its
   posterior border (1 mm behind), widened 8% at the ring and 30% at the top of
   the back plate so the arytenoid joints sit 12 mm apart (published 11.8-12.6).
   Lumen below the cords 16.0 wide x 16.9 deep (men: deeper than wide, about
   17.4 deep). Back plate 21.4 mm tall as in v2.
3. Arytenoids enlarged to published size: vocal process to apex 16.1 mm (was
   9.4; men 16.2-17.5). Each sits on a small cartilage pad that fills the
   shoulder of the cricoid under its base. They rock 9 degrees outward on the
   joint axis into the quiet-breathing position.
4. Glottis 145-153 mm2 (men, quiet breathing: about 141; tidal inspiration
   126 +/- 8), 24.4 mm long (22.1 +/- 3.1), 8 mm wide at the back. Vocal
   ligament 15 mm. Largest ball through the whole airway 7.8 mm (1:1 scale).
5. Cricoid-to-trachea junction rebuilt: the tracheal lumen flows into the
   cricoid lumen with no step, bridged by a real cricotracheal ligament; the
   cricoid now stands proud of the trachea like a signet ring.
6. Hyo-epiglottic ligament rebuilt as a 9 x 2.5 mm band from the back of the
   hyoid body to the front of the epiglottis (it was a cut-off web).
7. Posterior cricoarytenoid ligaments added (0.8 mm cords behind each joint).
   They are buried inside the interarytenoid muscle until stage 2 reshapes it.
8. Cricothyroid joints fused on purpose so the print does not leave a sliver.
9. Membrane thickening halved (the 1.2 mm print minimum is met at 2x), so the
   thin tissues are closer to life. The 1:1 files use the full thickening.

Parts: 37 named objects (32 from v2, plus the cricotracheal ligament, the two
posterior cricoarytenoid ligaments and the two facet pads).

Known limits (reviewer's residual list):
  - Muscular process of each arytenoid sits about 4 mm in front of the
    thyroid's posterior border; one CT series gives 8. The arytenoids sit near
    the back edge of the thyroid shield.
  - Hyoid greater-horn tips are 2 mm in front of the thyroid superior-horn tips
    (they end level with or behind them in life).
  - The vocal process is only 3 degrees higher than the anterior commissure;
    in-vivo CT favours 7-14 degrees.
  - The conus elasticus and the median cricothyroid ligament leave a 1 mm seam
    between 40 and 46 mm up (no hole; they are one membrane in life).
  - The vocal folds are still strips (thyroarytenoid 1.3 mm, conus 1.1 mm);
    fold bulk is stage 3.
  - The facet pads are constructed shapes, not source anatomy.

VERSION 3 - files
-----------------
2x scale (162 mm tall; the whole model fits the A1 mini standing up, and the
halves fit side by side with a 3 mm brim):

Larynx_v3_2x_whole_1colour.3mf    9 h 02 min, 152 g
Larynx_v3_2x_halves_1colour.3mf   12 h 17 min, 151 g
  Pins: cut 1.75 mm filament to 16 mm for the hyoid holes and 10 mm for the
  cricoid holes (2.0 mm holes, 8 and 5 mm deep per side).
Larynx_v3_2x_whole_4colour.3mf    50 h 23 min, 1279 colour changes, ~638 g (mostly purge)
Larynx_v3_2x_halfR_4colour.3mf    24 h 31 min, 590 changes, ~288 g
Larynx_v3_2x_halfL_4colour.3mf    24 h 37 min, 591 changes, ~289 g
  (one half per file: two 2x halves plus the wipe tower do not fit the bed)

1:1 (89 mm tall):

Larynx_v3_lifesize_whole_1colour.3mf    2 h 05 min, 23.5 g
Larynx_v3_lifesize_halves_1colour.3mf   2 h 49 min, 27.6 g
  Pins: 7.5 mm for the hyoid holes, 4.5 mm for the cricoid holes.
Larynx_v3_lifesize_whole_4colour.3mf    23 h 17 min, 644 changes, ~280 g
Larynx_v3_lifesize_halves_4colour.3mf   12 h 02 min, 295 changes, ~135 g


VERSION 2 - files (unchanged)
-----------------------------
Larynx_lifesize_v2_whole_1colour.3mf    1 h 45 min, 19.9 g
Larynx_lifesize_v2_halves_1colour.3mf   2 h 27 min, 23.8 g; pins 7.5 / 4.5 mm
Larynx_lifesize_v2_whole_4colour.3mf    about 23 h, 656 changes, ~282 g
Larynx_lifesize_v2_halves_4colour.3mf   about 11 h 42 min, 294 changes, ~132 g
Glottis 139 mm2, cricoid lamina 21.4 mm, source-size arytenoids and thyroid.

VERSION 1 - files (unchanged)
-----------------------------
Larynx_lifesize_whole_1colour.3mf   about 1 h 38 min, 17.4 g
Larynx_lifesize_halves_1colour.3mf  about 2 h 08 min, 20.3 g; pins 7.5 / 6.0 mm
  Known fault: the cricoid pin hole breaks through the back of the lamina as a
  0.45 mm slot. The pin still holds.
Larynx_lifesize_whole_4colour.3mf   about 22 h, 633 changes, ~269 g
Larynx_lifesize_halves_4colour.3mf  about 11 h, 289 changes, ~128 g
Source anatomy: semi-closed glottis (4.6 mm clear), short cricoid.


COLOUR KEY (multi-colour files)
-------------------------------
  Slot 1 beige  - bone
  Slot 2 cyan   - hyaline cartilage (thyroid, cricoid and its facet pads,
                  arytenoids, tracheal C-rings)
  Slot 3 yellow - elastic cartilage (epiglottis, corniculates, cuneiforms)
  Slot 4 pink   - ligaments, membranes, tracheal membranous wall, annular and
                  cricotracheal ligaments (in v1-v3 also the vocal-fold and
                  interarytenoid muscles)
  Slot 5 red    - muscle (versions 4 and 5)
  Slot 6 salmon - mucosa and fold cover (version 5 only)
  A single nozzle changes colour on almost every layer; most of the filament
  in the 4-colour estimates is purge.
Every part is a named object, so you can recolour or hide structures in
Bambu Studio.


LIMITS OF ALL VERSIONS
----------------------
  - No pharynx, tongue base, vallecula or piriform fossae. Versions 1-4 have
    no mucosa, vestibular folds, ventricle or quadrangular membrane; versions
    1-3 have no PCA, LCA or cricothyroid muscles. See the project's feature
    inventory.
  - In versions 1-4 the vocal fold is a thin strip over the conus, not a
    layered fold.

Source: BodyParts3D, (c) The Database Center for Life Science, licensed under
CC Attribution 4.0 International. Rebuilt, corrected toward published adult-
male dimensions, and thickened for printing. The corrections are constructed
geometry, not scan data; the build notes list every one.

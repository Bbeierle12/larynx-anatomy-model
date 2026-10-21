## Version 6: stage 3b and 3c, the spaces, the fossae and the hypopharynx (2026-10-20)

The decision behind this version: show as much of the anatomy as possible and accept that the printed model becomes a solid block that has to be printed in halves to be seen inside. Version 6 therefore fills the spaces (fat), lines the fossae, and closes the back of the larynx with the hypopharynx. 81 named parts (v5: 66). Everything new is constructed anatomy except the two inferior constrictors, which are BodyParts3D meshes warped onto the frame.

### Framework change (`deform7.py`)

- Epiglottis lifted 5 mm (petiole and tip alike) so the thyro-epiglottic ligament attaches to the inner thyroid angle above the vestibular ligaments, as in life; the ligament's thyroid end is also moved 1.5 mm forward and 0.5 mm up so it seats on the floor of the superior thyroid notch (the review found that 1.5 mm up left it in the notch, 0.9 mm off cartilage). Leaf length unchanged (30.5 mm; ref 29.1 ± 0.5). The hyo-epiglottic ligament is rebuilt to the lifted leaf; the aryepiglottic strips and cuneiforms follow it.
- Cricothyroid muscles bedded: the fibres are pulled onto the cricothyroid membrane, conus and arch (no gap under the muscle), and the oblique part now fans onto the lower border of the lamina as well as the anterior border of the inferior horn. The lower paraglottic space is thereby closed from the outside.
- The voxel grid is derived from the source parts only, so it no longer depends on which constructed parts exist (a grid shift between runs had misregistered one intermediate build by 2 mm).

### Stage 3b: spaces, saccule, tendon, capsules

| Part | Construction | Reference |
|---|---|---|
| Tongue base and vallecula (67) | Block above the hyoid, x ±15, cut flat at the front and 1 mm above the epiglottis tip; vallecula pockets 6 mm wide × 12 deep either side of a 1.6 mm median glossoepiglottic fold; lateral glossoepiglottic folds at x ±9.5; pharyngo-epiglottic folds behind the margins back to the fossa's anterior wall; floor 2.5 mm thick on the hyo-epiglottic ligament | landmark for laryngoscopy; shape is a stub, not a tongue |
| Pre-epiglottic fat (68), paraglottic fat R/L (69, 70) | Filled from the enclosed voids: the air that is at least 1.4 mm from every surface and sealed from the outside, grown back to the walls; the fossa lumina count as walls. Split at x ±12 and above/below the fold level | men 4.5 ± 1.0 mL for both together on CT (Hermans 1997) |
| Ventricle lateral wall R/L (62, 63), reworked | Was a 4.5–10 mm slab of mucosa colour filling the paraglottic slot between the ventricle and the lamina. Now a 0.8 mm mucosal lining on the ventricle's lateral face, joined to the lamina by a rim along its roof, floor and ends; the pocket behind it is left for the fat fill (a second paraglottic seed at ventricle level) | the paraglottic space is fat and thyroarytenoid with only a mucosal ventricle lining (Reidenbach 1996; Sato & Hirano 1997) |
| Laryngeal saccules | Blind pouches carved out of the false fold, ventricle wall and fat: from the front of the ventricle up 8 mm between the fold and the lamina, lateral of the vestibular ligament, r 1.6 → 0.9 mm | 6–8 mm pouch (Gray) |
| Anterior commissure tendon (71) | 0.5 → 0.8 mm cone from 1.5 mm inside the thyroid angle to the vocal ligaments' ends, submucosal | Broyles' ligament |
| Cricoarytenoid and cricothyroid capsules (72–75) | 0.8 mm skin on either joint partner where the other is within 2 mm (the joint line), inside 4.5 / 4 mm of the joint centre. Printed without the usual sheet offset (bounded by cartilage on both sides) and ranked above the muscles that attach around the joint, so they are not carved to crumbs by the vocalis, PCA and LCA insertions | |

### Stage 3c: piriform fossae and hypopharynx

| Part | Construction | Reference |
|---|---|---|
| Piriform fossa lumen (carved) and lining R/L (76, 77) | The lumen is the space lateral of the aryepiglottic fold, quadrangular membrane, thyro-epiglottic muscle and arytenoid, medial of the lamina and thyrohyoid membrane, behind an anterior wall at y −93 (z 50) to −101 (z 80), above an apex at z 47.5, and lateral of the arytenoid body behind its front. It is carved out of the false-fold, ventricle-wall and mucosa tissue that filled it, smoothed, and lined with 0.8 mm of mucosa wherever tissue lies behind the lining (its top and back are open) | cadaver: 25 tall × 14–15 wide × 13 deep (Vadgaonkar 2024); lumen here 1.73 cm³ |
| (Lateral pharyngeal wall, 78/79: dropped) | A 1 mm sheet below the fossa apex was built first; once the constrictors were in place 89 of its 161 mm³ lay inside the constrictor and 72 inside the lamina. Below the piriform apex the lateral wall *is* the constrictor and its mucosa, so the part was removed | |
| Inferior pharyngeal constrictor R/L (80, 81) | BodyParts3D meshes (FMA46635/46636), warped like the thyroid above the lamina and like the cricoid below it | source |
| Hypopharyngeal mucosa (83) | The hypopharynx is collapsed in the source (constrictor on the back of the larynx), so the mucosa is a 0.8 mm layer on the cricoid lamina, arytenoid backs, PCA and folds wherever the constrictor lies within 2.5 mm of them (down to the oesophageal inlet), plus the constrictors' own inner layer where they touch, carved out of the constrictors; slivers of constrictor cut off by the carve are folded into it. Measured outward from the laryngeal surface only: the warp lets the constrictor sink about 0.5 mm into the cricoid, and a band measured into the cartilage was lost to it | |
| Oesophagus, upper end (82) | Collapsed muscular tube 20 × 9 mm directly on the membranous trachea (its front face 0.5 mm into the trachealis, which wins) from the base cut to the cricoid's lower border, with a 12 × 1.4 mm slit lumen | |
| Quadrangular membrane | Now clipped to the epiglottis's lateral margin (it had run across the petiole's laryngeal face) | |

### Airway and measurements

| Measure | v6 | v5 | Reference |
|---|---|---|---|
| Named parts | 81 | 65 | |
| Union | one watertight body, 47.5 cm³ (hairline cracks ≤0.5 mm closed: 0.27 cm³) | 23.5 cm³ | the tongue block, fat, constrictors and oesophagus add 24 cm³ |
| Glottis between the covered folds | 99 mm², 7.8 mm wide, 7.7 mm inscribed circle; 7.5 mm ball passes the whole airway | 101 mm², 7.5 mm ball | quiet breathing |
| Epiglottis, tip to petiole | 30.5 mm (lifted 5 mm whole) | 30.5 | 29.1 ± 0.5 (Vadgaonkar 2024) |
| Pre-epiglottic fat | 3.64 mL | void | pre-epiglottic + paraglottic together 4.5 ± 1.0 mL, men (Hermans 1997) |
| Paraglottic fat | 0.44 / 0.43 mL per side, three pockets each (lateral wing z+55–73, ventricle-level pocket z+47–53, infraglottic slit z+35–43) | void / mucosa slab | as above; total fat 4.51 mL |
| Piriform fossa lumen | 1.73 cm³ each, 8.5–9.5 wide × 14 deep, apex at the vocal-fold level, open above and behind | absent | 25 tall × 14–15 wide × 13 deep, ~1.8 cm³ (Vadgaonkar 2024) |
| Saccule | 8 mm pouch, lumen 9.5 mm² at the base tapering to <1 mm² at the tip, lateral of the vestibular ligament, lined | absent | 6–8 mm (Gray) |
| Joint capsules | CA 59 / 49 mm³, CT 32 / 32 mm³, 0.8 mm, one body each | absent | |
| Constrictors | 3.15 / 3.14 cm³ (BodyParts3D, warped) | absent | |
| Hypopharyngeal mucosa | 0.97 cm³, 0.8 mm, cricoid lamina to the oesophageal inlet | absent | |
| Oesophagus (upper end) | 3.18 cm³, on the trachealis and the cricoid lower border | absent | |
| Surface thinner than 0.8 mm (at 2×: 1.6 mm) | 0.8 % | 1.4 % | |
| Airway ring at every layer 0–30 mm | closes | closes | |

### Independent review

Three passes by a reviewer that had not seen the build (`review_v8/b8c_`, `b8d_`, `b8e_`), judged from the final part meshes and a 0.5 mm flood fill of all air.

- Pass 1 (clean rebuild): no must-fix. Should-fix: the ventricle wall slab was mucosa-coloured paraglottic tissue → made a lining with fat behind it; oesophagus 1 mm off the trachealis; postcricoid mucosa short of the inlet and of the arytenoid backs; thyro-epiglottic ligament ending in the notch; QM edge fringes; constrictor islands.
- Pass 2: two must-fix items of my own making: the oesophagus had moved backwards (my resume chain skipped the trachea fit after the source parts were restored, so it was placed against the raw mesh) and the saccule and ventricle recess were walled by bare fat once the slab became a lining. Both fixed (trachea fit restored in every resume; a lining step after the saccule carve converts the fat facing the air into mucosa and lines the bare lamina). The ligament had become a holed sheet because the vestibular ligaments ranked above it → ranked above them and seated 2 mm up.
- Pass 3: ready to export. No fat or bare cartilage on the laryngeal lumen boundary, saccule lumen intact (9.5 → 0.7 mm² over z+54–59), oesophagus on the trachealis and cricoid, ligament solid (median 2.0 mm).

Residuals recorded, none affecting the print:
- Thyro-epiglottic ligament tip is 0.7 mm off the cartilage, held by the anterior vestibule wall (it sits in the notch above the midline apex). Seating it 1 mm lower would put it level with the vestibular ligaments again.
- Hypopharyngeal mucosa meets the oesophageal inlet across a 0.4 mm seam (two pieces: the postcricoid sheet to z+26.1 and a rim over the inlet z+23.3–25.7); its contact with the arytenoid backs is a 0.04–0.23 mm seam. Both close in the union.
- Fringes under 0.3 mm at 1× on the quadrangular membranes (50 mm² each), ventricle linings (3 %) and vestibular mucosa: 0.6 mm at 2×.
- Two 5 mm³ crumbs of the anterior vestibule wall cut off by the ligament, and a 7 mm³ crumb of the right ventricle lining beside the petiole, all embedded.
- The fossa apex sits against the posterior ventricle with one 0.8 mm layer between (a 1.5–2 mm paraglottic layer would be more typical).
- The hypopharynx is collapsed (constrictor directly on the larynx); the tongue base is a block; the constrictors' upper border reaches 8.6 mm above the hyoid (no middle constrictor yet); cricothyroid oblique parts asymmetric in the source (419 vs 496 mm³); arytenoid medial faces below the vocal process unlined (since v5).

### Files

Folder `Documents\Blender\Larynx life-size\`, sliced copies in `sliced - ready to print\`. Seven filament slots (fat is slot 7, sunflower yellow), so the multi-colour files are 7-colour; the A1 mini's AMS lite has four, so merge slots in Bambu Studio or accept the manual changes. The 7-colour files are purge-dominated now that the block is solid (a 2× half: 13 h / 170 g in one colour, 53 h / 657 g in seven); the 1-colour halves are the practical print. The 2× halves are one half per file since v6 (two side by side need 199 mm of the 180 mm bed), lying on the cut face without a brim (178.8 mm long on a 180 mm bed), wipe tower at the left edge; the 2× whole 7-colour model is shifted 15 mm back to clear the tower. Everything inside is visible only on the halves; the whole model prints as a block whose only cavities are the airway, vallecula, fossae and oesophageal slit.

| File | Scale | Bambu Studio estimate |
|---|---|---|
| `Larynx_v6_2x_whole_1colour.3mf` | 2× (179 mm tall) | 23 h 04 min, 331 g |
| `Larynx_v6_2x_halfR_1colour.3mf` | 2×, one half per file; pins 16 mm hyoid, 10 mm cricoid | 13 h 09 min, 171 g |
| `Larynx_v6_2x_halfL_1colour.3mf` | 2×, one half per file | 13 h 10 min, 170 g |
| `Larynx_v6_2x_whole_7colour.3mf` | 2× | 126 h 03 min, 1630 g, 3416 colour changes (mostly purge) |
| `Larynx_v6_2x_halfR_7colour.3mf` | 2×, one half per file | 52 h 56 min, 657 g, 1325 colour changes (mostly purge) |
| `Larynx_v6_2x_halfL_7colour.3mf` | 2×, one half per file | 52 h 57 min, 657 g, 1326 colour changes (mostly purge) |
| `Larynx_v6_lifesize_whole_1colour.3mf` | 1:1 (81 mm) | 5 h 25 min, 54 g |
| `Larynx_v6_lifesize_halves_1colour.3mf` | 1:1; pins 7.5 / 4.5 mm | 5 h 55 min, 60 g |
| `Larynx_v6_lifesize_whole_7colour.3mf` | 1:1 | 60 h 10 min, 725 g, 1714 colour changes (mostly purge) |
| `Larynx_v6_lifesize_halves_7colour.3mf` | 1:1 | 26 h 02 min, 307 g, 661 colour changes (mostly purge) |

### Sources added

- Hermans, Van der Goten & Baert 1997, volume of the pre-epiglottic and paraglottic space on spiral CT (Surg Radiol Anat).
- Vadgaonkar et al. 2024, morphometry of the thyroid cartilage, epiglottis and piriform sinus (F1000Research 13:115).
- BodyParts3D FMA46635/46636 (inferior pharyngeal constrictors), FMA7131 (oesophagus, not used: a 132-face blob too far forward).

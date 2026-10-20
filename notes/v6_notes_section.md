## Version 6: stage 3b and 3c, the spaces, the fossae and the hypopharynx (2026-10-20)

The decision behind this version: show as much of the anatomy as possible and accept that the printed model becomes a solid block that has to be printed in halves to be seen inside. Version 6 therefore fills the spaces (fat), lines the fossae, and closes the back of the larynx with the hypopharynx. {PARTS} named parts (v5: 66). Everything new is constructed anatomy except the two inferior constrictors, which are BodyParts3D meshes warped onto the frame.

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
| Piriform fossa lumen (carved) and lining R/L (76, 77) | The lumen is the space lateral of the aryepiglottic fold, quadrangular membrane, thyro-epiglottic muscle and arytenoid, medial of the lamina and thyrohyoid membrane, behind an anterior wall at y −93 (z 50) to −101 (z 80), above an apex at z 47.5, and lateral of the arytenoid body behind its front. It is carved out of the false-fold, ventricle-wall and mucosa tissue that filled it, smoothed, and lined with 0.8 mm of mucosa wherever tissue lies behind the lining (its top and back are open) | cadaver: 25 tall × 14–15 wide × 13 deep (Vadgaonkar 2024); lumen here {FOSSA} cm³ |
| (Lateral pharyngeal wall, 78/79: dropped) | A 1 mm sheet below the fossa apex was built first; once the constrictors were in place 89 of its 161 mm³ lay inside the constrictor and 72 inside the lamina. Below the piriform apex the lateral wall *is* the constrictor and its mucosa, so the part was removed | |
| Inferior pharyngeal constrictor R/L (80, 81) | BodyParts3D meshes (FMA46635/46636), warped like the thyroid above the lamina and like the cricoid below it | source |
| Hypopharyngeal mucosa (83) | The hypopharynx is collapsed in the source (constrictor on the back of the larynx), so the mucosa is a 0.8 mm layer on the cricoid lamina, arytenoid backs, PCA and folds wherever the constrictor lies within 2.5 mm of them (down to the oesophageal inlet), plus the constrictors' own inner layer where they touch, carved out of the constrictors; slivers of constrictor cut off by the carve are folded into it. Measured outward from the laryngeal surface only: the warp lets the constrictor sink about 0.5 mm into the cricoid, and a band measured into the cartilage was lost to it | |
| Oesophagus, upper end (82) | Collapsed muscular tube 20 × 9 mm directly on the membranous trachea (its front face 0.5 mm into the trachealis, which wins) from the base cut to the cricoid's lower border, with a 12 × 1.4 mm slit lumen | |
| Quadrangular membrane | Now clipped to the epiglottis's lateral margin (it had run across the petiole's laryngeal face) | |

### Airway and measurements

{MEAS}

### Independent review

{REVIEW}

### Files

{FILES}

### Sources added

- Hermans, Van der Goten & Baert 1997, volume of the pre-epiglottic and paraglottic space on spiral CT (Surg Radiol Anat).
- Vadgaonkar et al. 2024, morphometry of the thyroid cartilage, epiglottis and piriform sinus (F1000Research 13:115).
- BodyParts3D FMA46635/46636 (inferior pharyngeal constrictors), FMA7131 (oesophagus, not used: a 132-face blob too far forward).

# Larynx model: anatomical feature inventory

Checked 2026-10-18 against version 2 (`Larynx_lifesize_v2_*`), the BodyParts3D 4.0 catalogue, and the "Larynx-Source-Models" package; the muscle table updated 2026-10-19 for version 4 (stage 2), the framework, ligament and mucosa tables 2026-10-20 for version 5 (widening and stage 3), and the joints, ligaments, mucosa, spaces and neighbours 2026-10-20 for version 6 (stages 3b and 3c). Status key:

- **v2**: in the current model (v3 and v4 keep everything v2 has).
- **v4**: added in version 4 (stage 2) as constructed anatomy.
- **v5**: added in version 5 (stage 3) as constructed anatomy, or changed by the version-5 widening.
- **v6**: added in version 6 (stages 3b and 3c: spaces, fossae, hypopharynx) as constructed anatomy, or changed by the version-6 epiglottis lift.
- **source**: in BodyParts3D 4.0 but not used yet (all at 99% polygon reduction, so shapes are coarse and volumes are low).
- **absent**: not in BodyParts3D or any open source we have; has to be sculpted from published dimensions and labelled as constructed.
- **n/a**: out of scope for a larynx model, or variable anatomy.

## Framework

| Structure | Status | Notes |
|---|---|---|
| Hyoid body, greater and lesser horns | v2 | Fused adult hyoid. Lesser horns present as small spurs. |
| Thyroid laminae, superior and inferior horns, oblique line, superior tubercle, laryngeal prominence | v5 (widened) | Widened 10 % in v5: superior-horn span 42.4 mm (men 41.5 ± 7.2), angle 81° overall, ~75° at fold level. Was 38.6 mm, slightly narrow. Inferior horns 21 mm apart (norm about 31 mm): narrow with the cricoid. |
| Thyroid notch | v2 | |
| Cricoid arch, lamina, cricothyroid facets, cricoarytenoid facets | v5 (reshaped, widened) | Lamina lengthened to 21.4 mm. Outer wall widened 10 % in v5 to 27.2 mm at the ring (norm 27–31); lumen 16.0 × 16.9 unchanged. Facets are the coarse source facets; no articular surface detail. |
| Arytenoids: body, vocal process, muscular process, apex, fovea | v2 (re-posed) | Undersized: vocal process to apex 9.4 mm vs 16.2–17.5 mm in men. Fovea triangularis/oblonga not resolved in the source. |
| Corniculate cartilages | v2 | 1 mm³ each; coarse. |
| Cuneiform cartilages | v2 | Present as rods inside the aryepiglottic folds. |
| Epiglottis with petiole and perforations | v6 (lifted) | Perforations present as pits. Whole leaf lifted 5 mm in v6 so the thyro-epiglottic ligament attaches above the vestibular ligaments; leaf 30.5 mm. Epiglottic tubercle added in v5, see below. |
| Triticeal cartilages | absent | Variable (present in roughly a third to a half of people). Optional. |
| Tracheal rings 1–5, annular ligaments, membranous wall (trachealis) | v2 (derived) | Rings are source geometry; the wall split is derived. |
| Cricotracheal ligament | v2 (derived band) | Modelled as the annular band under the cricoid, 0.6–1.8 mm tall. In life it is a distinct membrane 2–3 mm tall. |

## Joints

| Structure | Status | Notes |
|---|---|---|
| Cricothyroid joint: facets, capsule, ceratocricoid ligaments | facets v2; capsule v6; ceratocricoid ligaments absent | Horn tip sits 0.3 mm from the facet. Capsule: 0.8 mm sleeve on the joint line within 4 mm of the horn tip, 32/32 mm³. Facets at about half lamina height after the reshape; probably high. |
| Cricoarytenoid joint: facets, capsule, posterior cricoarytenoid ligament | facets v2; capsule v6; ligament in the model (parts 35/36) | Base seated on the lamina. Capsule: 0.8 mm sleeve on the joint line within 4.5 mm of the facet pad, 59/49 mm³, deep to the vocalis, PCA and LCA insertions. |

## Ligaments and membranes

| Structure | Status | Notes |
|---|---|---|
| Thyrohyoid membrane, median and lateral thyrohyoid ligaments | v2 | Thickened +0.2 mm per side for printing. Aperture for the internal laryngeal nerve and superior laryngeal vessels: not modelled. |
| Hyo-epiglottic ligament | v6 (rebuilt to the lifted leaf) | Band from the hyoid body to the lingual face of the lifted epiglottis (z0 + 71–76); floor of the vallecula above it. |
| Thyro-epiglottic ligament | v6 (re-seated) | Lifted with the petiole; thyroid end moved 1.5 mm forward and 0.5 mm up so it sits on the floor of the superior notch, above the vestibular ligaments (the v5 order was inverted). |
| Conus elasticus (cricovocal membrane) | v2 | Thickened one-sided, away from the airway. |
| Vocal ligaments | v2 | Straight in v2; 15–16 mm. |
| Median cricothyroid ligament | v2 | Prints as a bar in an open window because the cricothyroid muscles are absent. |
| Anterior commissure tendon (Broyles' ligament) | v6 (constructed) | 0.5 → 0.8 mm cone from 1.5 mm inside the thyroid angle to the vocal ligaments' ends, 2.7 mm³, submucosal. |
| Quadrangular membrane | v5 (constructed) | 0.6 mm ruled sheet from the vestibular ligament line up to the aryepiglottic line (arytenoid apex → aryepiglotticus → epiglottis margin); embedded in the false fold below, lined by mucosa on the airway side, thyro-epiglottic muscle lateral to it. Was absent: it is the sheet from the epiglottis and arytenoid that forms the aryepiglottic fold above and the vestibular ligament below. Without it the vestibule has no lateral walls. |
| Vestibular (ventricular) ligaments | v5 (constructed) | 1 mm cord inside the false fold from the thyroid angle to the anterolateral arytenoid; 19 mm³. Since v6 it attaches below the thyro-epiglottic ligament, the right order. |
| Cricoarytenoid and cricothyroid joint capsules | v6 (constructed) | See joints. |

## Intrinsic muscles (version 4, stage 2)

| Muscle | Status | Notes |
|---|---|---|
| Thyroarytenoid (external part) | v4 (constructed) | Fibres from the inner thyroid angle to the lateral surface, vocal and muscular processes of the arytenoid; lateral to the ligament and conus. 172–188 mm³ per side after the vocalis is split off. |
| Vocalis | v4 (constructed) | Medial 35 % of the thyroarytenoid complex next to the ligament and conus, full fold height, reaching the thyroid. 213–233 mm³. Complex 401–404 mm³ per side against 860–890 by MRI: the paraglottic space of this framework holds no more. |
| Posterior cricoarytenoid | v4 (constructed) | 70 fibres from the posterior lamina (4 mm bare strip below, 5.7 mm gap at the ridge) to the muscular process. 376–387 mm³, 22 mm tall, 2.6 mm thick. Reads as a slab with a bulge rather than a fan because the muscular process sits only 3 mm above the lamina top. |
| Lateral cricoarytenoid | v4 (constructed) | Upper border of the lateral arch to the front of the muscular process, lateral to the conus. 74–83 mm³, a 1.4 mm strap: the slot between conus and lamina is 2 mm wide here. |
| Cricothyroid, straight and oblique parts | v4 (constructed) | Front and lateral arch to the lamina's lower border and the inferior horn's anterior border; 7.4 mm of the median cricothyroid ligament left exposed. 722–755 mm³ per side (Cox 1999: 890), 3 mm thick. Fills the "window" of v1–v3. |
| Transverse arytenoid | v2 | Source, scaled 1.9× with the arytenoids in stage 1. 254 mm³. |
| Oblique arytenoids | v4 (constructed) | Muscular process of one arytenoid to the apex of the other and into the opposite aryepiglotticus, crossing on the back of the transverse. 120–141 mm³. The source bands touched neither arytenoid. |
| Aryepiglotticus | v2 | Source strip, 36 mm³, inside the v5 aryepiglottic fold; the quadrangular membrane now cuts it, leaving thin slivers (harmless in the union). |
| Thyroepiglotticus | v5 (trimmed) | The upper sheet of the source thyroarytenoid, trimmed in v5 to the lateral side of the quadrangular membrane: 100 mm³ per side, z0 + 8 up to the epiglottis margin, thyroid attachment reduced to a 1.6 mm² patch. |
| Ventricularis (superior thyroarytenoid in the false fold) | absent | The false fold exists from v5; the muscle slip is not modelled (variable, small). |

## Mucosa and soft-tissue structures (none in the source)

| Structure | Status | Relevance |
|---|---|---|
| Vocal fold cover: epithelium, superficial lamina propria (Reinke's space), intermediate and deep layers | v5 (constructed, one layer) | 1.0 mm cover over the fold core (line of sight to the axis), anterior commissure to vocal process, 6 mm down the infraglottic face; 218–225 mm³ per side; glottis between the covered folds 101 mm². Layers not separated. Was absent. Core of the body-cover model. Life thickness about 1.1 mm for the cover; at 2× it can be a 2 mm shell. |
| Macula flavae (anterior and posterior) | absent | Small; relevant to ligament anatomy teaching. |
| Vocal fold bulk (medial contour, infraglottic slope) | v5 | Rounded free edge from the cover; upper surface at z0 + 2.8 (ventricle floor); infraglottic slope is the covered conus. |
| Vestibular (false) folds | v5 (constructed) | Capsule-chain fold, 5 mm thick, rounded edge 2.2–2.5 mm lateral of and 5.6 mm above the true-fold edge, thyroid angle to the anterolateral arytenoid; 580 mm³ per side with the ligament and membrane embedded. |
| Laryngeal ventricle (Morgagni) and saccule | v6 (saccule; ventricle wall reworked) | Ventricle from v5. In v6 the lateral wall is a 0.8 mm mucosal lining (275 mm³ per side) with paraglottic fat behind it, and a saccule rises 8 mm from the front of each ventricle between the false fold and the lamina, lateral of the vestibular ligament (r 1.6 → 0.9 mm; lumen 9.5 mm² at its base tapering to under 1 mm² at the tip). |
| Aryepiglottic folds as mucosal folds | v5 (constructed) | 4.4 mm mucosal tube along the aryepiglottic line enclosing the muscle and membrane; 420 mm³ per side. Reads thicker than life (2–4 mm). |
| Cuneiform and corniculate tubercles | v5 (constructed) | 5.4 and 4.8 mm bumps on the fold over the cartilages. |
| Interarytenoid notch / posterior commissure mucosa | v5 (constructed) | 1.2 mm plate on the front of the transverse arytenoid between the arytenoid bodies (110 mm³); flat, square-topped, reaches the cricoid lamina. |
| Epiglottic tubercle | v5 (constructed) | Half-ellipsoid 7 × 6.4 mm, 2–2.7 mm proud of the laryngeal face of the petiole at the midline, z0 + 8.5. |
| Vallecula, median and lateral glossoepiglottic folds, tongue base | v6 (constructed stub) | Tongue base as a flat-fronted block above the hyoid (7.8 cm³) with two vallecula pockets 6 × 12 mm either side of a median glossoepiglottic fold, lateral folds at x ±9.5, floor 2.5 mm on the hyo-epiglottic ligament. A landmark, not a tongue. |
| Piriform fossae | v6 (constructed) | Open recesses lateral of the aryepiglottic fold, quadrangular membrane and arytenoid, medial of the lamina and thyrohyoid membrane, apex at the vocal-fold level, 1.73 cm³ each (cadaver ~1.8, Vadgaonkar 2024); 0.8 mm lining (654 mm³) wherever tissue backs it. 8.5–9.5 mm wide, narrower than life (14–15) because the framework lamina is 19 mm from the midline. |
| Postcricoid region and oesophageal inlet | v6 (constructed) | Upper oesophagus as a collapsed 20 × 9 mm muscular tube on the membranous trachea from the base cut to the cricoid's lower border, 12 × 1.4 mm slit lumen (3.2 cm³); the source oesophagus (FMA7131) was a 132-face blob and is not used. Postcricoid mucosa is part of the hypopharyngeal mucosa below. |
| Posterior and lateral pharyngeal walls | v6 (source constrictors + constructed mucosa) | Inferior constrictors from BodyParts3D warped onto the frame (3.2/3.1 cm³), meeting at the median raphe, attached along the oblique-line zone and continuous with the oesophagus. The hypopharynx is collapsed in the source (constrictor on the back of the larynx), so the mucosa (971 mm³) is a 0.8 mm layer on the cricoid lamina, arytenoid backs, PCA and folds wherever the constrictor lies within 2.5 mm, plus the constrictors' inner layer where they touch: a slit, not a lumen. |
| Vestibular mucosa (over the quadrangular membrane and arytenoid medial face) | v5 (constructed) | 0.8 mm lining above the vocal-process level; 140 mm³ per side. The QM's anterior-upper margin near the epiglottis is unlined. |
| Anterior vestibule wall (petiole, thyroid angle) | v5 (constructed) | Plug between the ventricle walls, the thyro-epiglottic ligament and the petiole's laryngeal face, so the vestibule does not open into the pre-epiglottic space; ~270 mm³. |
| Subglottic and tracheal mucosa | absent | Printed lumen is cartilage/ligament surface. |
| Laryngeal glands | n/a | |

## Spaces

| Space | Status | Notes |
|---|---|---|
| Pre-epiglottic space (fat) | v6 (filled) | Fat filled from the enclosed void: 3.64 mL, bounded by the epiglottis, thyrohyoid membrane and median ligament, hyo-epiglottic ligament, hyoid, thyroid, quadrangular membranes, false-fold tops and the tongue block. Yellow (slot 7) in the 7-colour files. |
| Paraglottic space (fat) | v6 (filled) | 0.44/0.43 mL per side: the lateral wing beside the quadrangular membrane and fossa, the 1–2.5 mm pocket between the ventricle lining and the lamina, and the slit lateral of the conus below the fold. Total fat 4.51 mL (Hermans 1997: 4.5 ± 1.0 mL for both spaces, men). |

## Extrinsic muscles and neighbours (all in source, none in model)

Thyrohyoid, sternothyroid, sternohyoid, omohyoid, stylohyoid and stylohyoid ligament, digastric, mylohyoid, geniohyoid, palatopharyngeus, stylopharyngeus. The inferior pharyngeal constrictor (thyropharyngeus + cricopharyngeus as one mesh) is in the model from v6; its upper border reaches 8.6 mm above the hyoid, high for the inferior constrictor alone, acceptable until a middle constrictor exists. Sternothyroid and thyrohyoid are the ones singing pedagogy discusses for laryngeal height; the inferior constrictor defines the pharyngeal wall and the piriform fossae.

## Neurovascular (not in source)

Superior laryngeal nerve (internal and external branches), recurrent laryngeal nerve, superior and inferior laryngeal arteries and veins, and the thyrohyoid-membrane aperture they pass through. Could be added as coloured cords at 2× if wanted; nothing in the source to place them from except the membrane.

## What this changes in the plan

- Stage 1 (framework and joints) should also build a proper cricotracheal ligament, add the posterior cricoarytenoid ligament, and leave a defined site for the quadrangular membrane on the arytenoid and epiglottis.
- Stage 2 (muscles): done in version 4. The source muscles were 5–10× too small and the cricothyroid misplaced, so every muscle except the transverse arytenoid and aryepiglotticus was rebuilt as fibre bundles between attachment areas on the v3 cartilages (see the build notes). The ventricularis waits for the false fold.
- Stage 3 (folds and supraglottis): done in version 5; the spaces, saccules, capsules and tendon (3b) and the vallecula, piriform fossae and hypopharynx (3c) in version 6, which is the point where the model becomes a solid block that has to be printed in halves to be seen inside. It had no source geometry at all: the cover layers, false folds, ventricle, quadrangular membrane, aryepiglottic folds, tubercles, vallecula and piriform fossae are all sculpted. That is the largest block of constructed anatomy in the whole model and must be labelled as such.

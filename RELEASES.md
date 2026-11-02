# Releases

Model files (Bambu Studio 3MF projects for the A1 mini) are attached to GitHub releases, not committed; the repo holds the pipeline that produces them.

## v6 — 2026-10-21
Stages 3b and 3c: fat-filled pre-epiglottic and paraglottic spaces, saccules, joint capsules, Broyles tendon, piriform fossae, inferior constrictors, hypopharyngeal mucosa, upper oesophagus, tongue base with vallecula. 81 parts. Ten 3MFs: 2x whole and single halves (1- and 7-colour) and 1:1 whole and halves (1- and 7-colour). Everything inside is visible only on the halves. Slice estimates are in docs/PRINT-README.txt and notes/Larynx_v6_summary.xlsx.

## v6.2 — 2026-11-02 (files built; release not yet published)
Sculpted tongue base in place of the v6 block: same vallecula (6 x 12 mm pockets), median and lateral glossoepiglottic folds, pharyngo-epiglottic fold and floor on the hyo-epiglottic ligament, but a convex forward-leaning front following the hyoid body, rounded vertical edges, and paramedian lingual-tonsil mounds (vallecula gap 6 -> 4 mm; Sung 2013, doi 10.1001/jamaoto.2013.3263). Labelled "Adult male larynx" in title, description and object names. 81 parts. Built from the v6 release files by `scripts/tongue/make_v6_2.ps1` (no pipeline run; see `scripts/tongue/`). Ten 3MFs as v6, plus `Larynx_v6_2_2x_halves_P1S_1colour.3mf`: both 2x halves on one Bambu Lab P1S plate (`scripts/tongue/p1s_plate.ps1`, with `scripts/v6_1/`).

## v6.1 — 2026-11-01 (superseded by v6.2, never published)
v6 with the tongue block removed and the adult-male labels. The block was the problem, not the tongue; v6.2 puts the tongue back.

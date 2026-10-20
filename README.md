# Larynx anatomy model (BodyParts3D 4.0 rebuild) — build pipeline

Scripts, notes and renders for a printable larynx and upper trachea rebuilt from BodyParts3D 4.0 in stages
(1 framework and joints, 2 intrinsic muscles, 3 fold and supraglottic tissues, 3b spaces/saccules/capsules,
3c piriform fossae and hypopharynx), printed on a Bambu Lab A1 mini at 2× and 1:1.

- `scripts/` — the voxel pipeline (deform → voxelise → constructed muscles and tissues → SDF offset/priority assembly → union → QA) and the 3MF exporter. Entry points: `pipeline8b.sh` (full version-6 chain), `pipeline6b.sh` (assembly + QA), `build3mf.py` / `export_v6.sh` (3MF export).
- `docs/` — the build notes for every version (`larynx-lifesize-rebuild.md`) and the print README that ships with the 3MFs.
- `notes/` — per-version README and notes sections.
- `renders/` — summary figures.

Source meshes (BodyParts3D, CC BY 4.0) and the build directories (`build*/`, `out*/`, `.ply`, `.npz`, `.3mf`) are not in the repo.
Everything beyond the source cartilages is constructed anatomy from published dimensions and is labelled as such in the notes.

# v6.2: the sculpted tongue base added to every v6.1 file, from the v6 release files.
# Run from the repo root:  powershell -ExecutionPolicy Bypass -File scripts\tongue\make_v6_2.ps1
# Needs .venv-tongue (python 3.12: numpy scipy scikit-image trimesh edt manifold3d rtree shapely fast_simplification).
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = Join-Path $repo ".venv-tongue\Scripts\python.exe"
$L = Join-Path $env:USERPROFILE "Documents\Blender\Larynx life-size"
$src = Join-Path $L "v6_2\src"; $v61 = Join-Path $L "v6_1"; $out = Join-Path $L "v6_2"; $work = Join-Path $L "v6_2\work"
New-Item -ItemType Directory -Force $src, $work | Out-Null
$env:PYTHONPATH = $PSScriptRoot

$names = @("lifesize_whole", "lifesize_halves", "2x_whole", "2x_halfR", "2x_halfL")
# 1. the v6 release files (the PC's own 2x whole differs from the release; take the release for all)
foreach ($n in $names) { foreach ($c in @("1colour", "7colour")) {
    $f = "Larynx_v6_${n}_$c.3mf"
    if (-not (Test-Path (Join-Path $src $f))) {
        Write-Host "downloading $f"
        Invoke-WebRequest -Uri "https://github.com/Bbeierle12/larynx-anatomy-model/releases/download/v6/$f" -OutFile (Join-Path $src $f)
    }
} }
# 2. v6.1 (block removed, adult-male labels) for every file that is not there yet
foreach ($n in $names) { foreach ($c in @("1colour", "7colour")) {
    $o = Join-Path $v61 "Larynx_v6_1_${n}_$c.3mf"
    if (-not (Test-Path $o)) { & $py -W ignore (Join-Path $v61 "make_v6_1.py") (Join-Path $src "Larynx_v6_${n}_$c.3mf") $o }
} }
# 3. the tongue meshes: whole at each scale, then clipped and mapped into each half
& $py (Join-Path $PSScriptRoot "build_tongue.py") (Join-Path $src "Larynx_v6_lifesize_whole_1colour.3mf") 1 (Join-Path $work "tongue_1x.npz")
& $py (Join-Path $PSScriptRoot "build_tongue.py") (Join-Path $src "Larynx_v6_2x_whole_1colour.3mf") 2 (Join-Path $work "tongue_2x.npz")
foreach ($s in @("R", "L")) {
    & $py (Join-Path $PSScriptRoot "halves.py") (Join-Path $src "Larynx_v6_lifesize_whole_1colour.3mf") (Join-Path $src "Larynx_v6_lifesize_halves_1colour.3mf") $s (Join-Path $work "tongue_1x.npz") (Join-Path $work "tongue_1x_half$s.npz")
    & $py (Join-Path $PSScriptRoot "halves.py") (Join-Path $src "Larynx_v6_2x_whole_1colour.3mf") (Join-Path $src "Larynx_v6_2x_half${s}_1colour.3mf") $s (Join-Path $work "tongue_2x.npz") (Join-Path $work "tongue_2x_half$s.npz")
}
# 4. the ten v6.2 files
foreach ($c in @("1colour", "7colour")) {
    & $py (Join-Path $PSScriptRoot "add_part.py") (Join-Path $v61 "Larynx_v6_1_lifesize_whole_$c.3mf") (Join-Path $out "Larynx_v6_2_lifesize_whole_$c.3mf") "1000=$work\tongue_1x.npz"
    & $py (Join-Path $PSScriptRoot "add_part.py") (Join-Path $v61 "Larynx_v6_1_lifesize_halves_$c.3mf") (Join-Path $out "Larynx_v6_2_lifesize_halves_$c.3mf") "1000=$work\tongue_1x_halfR.npz" "1001=$work\tongue_1x_halfL.npz"
    & $py (Join-Path $PSScriptRoot "add_part.py") (Join-Path $v61 "Larynx_v6_1_2x_whole_$c.3mf") (Join-Path $out "Larynx_v6_2_2x_whole_$c.3mf") "1000=$work\tongue_2x.npz"
    & $py (Join-Path $PSScriptRoot "add_part.py") (Join-Path $v61 "Larynx_v6_1_2x_halfR_$c.3mf") (Join-Path $out "Larynx_v6_2_2x_halfR_$c.3mf") "1000=$work\tongue_2x_halfR.npz"
    & $py (Join-Path $PSScriptRoot "add_part.py") (Join-Path $v61 "Larynx_v6_1_2x_halfL_$c.3mf") (Join-Path $out "Larynx_v6_2_2x_halfL_$c.3mf") "1000=$work\tongue_2x_halfL.npz"
}
Get-ChildItem $out -Filter "Larynx_v6_2_*.3mf" | Select-Object Name, Length

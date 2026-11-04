# Both 2x halves of a version on one P1S plate, re-saved and sliced by Bambu Studio's CLI.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\tongue\p1s_plate.ps1 -Ver v6_2 [-Upright]
#   -Upright: the halves stand on their base cut (anatomical z up), tree supports from the build plate only,
#             8 mm brim (p1s_process_upright.json); otherwise they lie on the cut face (p1s_process_larynx.json).
param([string]$Ver = "v6_2", [switch]$Upright)
$ErrorActionPreference = "Stop"
$L = Join-Path $env:USERPROFILE "Documents\Blender\Larynx life-size"
$tools = Join-Path $L "v6_1"          # merge scripts, apply_p1s.py and the flattened P1S presets live here
$dir = Join-Path $L $Ver
$bs = "C:\Program Files\Bambu Studio\bambu-studio.exe"
if ($Upright) { $plate = "Larynx_${Ver}_2x_halves_upright_P1S_1colour"; $merge = "merge_halves_upright.py"; $ov = "p1s_process_upright.json" }
else          { $plate = "Larynx_${Ver}_2x_halves_P1S_1colour";         $merge = "merge_halves.py";         $ov = "p1s_process_larynx.json" }
Set-Location $tools
python $merge (Join-Path $dir "Larynx_${Ver}_2x_halfR_1colour.3mf") (Join-Path $dir "Larynx_${Ver}_2x_halfL_1colour.3mf") (Join-Path $dir "merged_2x_halves.3mf") 256
python apply_p1s.py (Join-Path $dir "merged_2x_halves.3mf") (Join-Path $dir "$plate.tmp.3mf") $ov
Set-Location $dir
Remove-Item result.json -ErrorAction SilentlyContinue
# Bambu Studio is a GUI executable: PowerShell's & returns at once, so wait for it explicitly
Start-Process -FilePath $bs -ArgumentList @("--debug", "2", "--export-3mf", "$plate.3mf", "$plate.tmp.3mf") -Wait -WindowStyle Hidden
Get-Content result.json | Select-String "error_string|return_code"
Remove-Item result.json -ErrorAction SilentlyContinue
Start-Process -FilePath $bs -ArgumentList @("--debug", "2", "--slice", "0", "--export-3mf", "$plate.gcode.3mf", "$plate.3mf") -Wait -WindowStyle Hidden
Get-Content result.json | Select-String "error_string|return_code"
Remove-Item "$plate.tmp.3mf", "merged_2x_halves.3mf" -ErrorAction SilentlyContinue
python -c "import zipfile,re,sys;z=zipfile.ZipFile(sys.argv[1]);s=z.read('Metadata/slice_info.config').decode();print('prediction s', re.search(r'prediction. value=.(\d+)',s).group(1), 'weight g', re.search(r'weight. value=.([\d.]+)',s).group(1));g=[n for n in z.namelist() if n.endswith('.gcode')][0];h=z.read(g)[:8000].decode(errors='ignore');print([l for l in h.splitlines() if 'printing time' in l or 'max_z_height' in l])" "$plate.gcode.3mf"

# Both 2x halves of a version on one P1S plate, re-saved and sliced by Bambu Studio's CLI.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\tongue\p1s_plate.ps1 -Ver v6_2
param([string]$Ver = "v6_2")
$ErrorActionPreference = "Stop"
$L = Join-Path $env:USERPROFILE "Documents\Blender\Larynx life-size"
$tools = Join-Path $L "v6_1"          # merge_halves.py, apply_p1s.py and the flattened P1S presets live here
$dir = Join-Path $L $Ver
$bs = "C:\Program Files\Bambu Studio\bambu-studio.exe"
$plate = "Larynx_${Ver}_2x_halves_P1S_1colour"
Set-Location $tools
python merge_halves.py (Join-Path $dir "Larynx_${Ver}_2x_halfR_1colour.3mf") (Join-Path $dir "Larynx_${Ver}_2x_halfL_1colour.3mf") (Join-Path $dir "merged_2x_halves.3mf") 256
python apply_p1s.py (Join-Path $dir "merged_2x_halves.3mf") (Join-Path $dir "$plate.tmp.3mf")
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

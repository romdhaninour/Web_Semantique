$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m pip install -r backend\requirements.txt
Set-Location frontend
npm install

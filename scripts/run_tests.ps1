$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
pytest backend\tests\test_backend.py -q
Set-Location frontend
npm run build

$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root 'frontend')
npm start -- --host 0.0.0.0 --port 4200

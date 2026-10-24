$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
New-Item -ItemType Directory -Force -Path docs\screenshots | Out-Null
Write-Host 'Screenshot automation placeholder. Run the app and capture UI manually if needed.'

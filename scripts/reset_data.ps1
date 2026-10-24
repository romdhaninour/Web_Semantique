$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Remove-Item backend\data\working_graph.ttl -ErrorAction SilentlyContinue
python backend\data\generate_seed.py

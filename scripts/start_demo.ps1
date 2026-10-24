$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $root 'frontend'
$logRoot = Join-Path $env:TEMP 'smart-grid-demo'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

$python = Get-Command python -ErrorAction Stop
$npm = Get-Command npm.cmd -ErrorAction Stop

& $python.Source -c 'import fastapi, uvicorn, rdflib' 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Installing missing Python dependencies…'
  & $python.Source -m pip install -r (Join-Path $root 'backend\requirements.txt')
  if ($LASTEXITCODE -ne 0) {
    throw 'Python dependencies could not be installed. Check your Python/pip setup and try again.'
  }
}

if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
  Write-Host 'Installing frontend dependencies…'
  & $npm.Source install --prefix $frontend
  if ($LASTEXITCODE -ne 0) {
    throw 'Frontend dependencies could not be installed. Check your Node.js/npm setup and try again.'
  }
}

function Test-PortAvailable([int]$Port) {
  $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return $null -eq $listeners
}

function Wait-ForHttp([string]$Url, [int]$TimeoutSeconds) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
        return $true
      }
    } catch {
      Start-Sleep -Milliseconds 700
    }
  }
  return $false
}

$healthUrl = 'http://127.0.0.1:8002/api/health'
if (Test-PortAvailable 8002) {
  $backendOut = Join-Path $logRoot 'backend.log'
  $backendErr = Join-Path $logRoot 'backend-error.log'
  Start-Process -FilePath $python.Source `
    -ArgumentList @('-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', '8002') `
    -WorkingDirectory $root -WindowStyle Hidden `
    -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr | Out-Null

  if (-not (Wait-ForHttp $healthUrl 30)) {
    throw "Backend did not start. Check logs at $logRoot"
  }
} else {
  try {
    Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3 | Out-Null
  } catch {
    throw 'Port 8002 is occupied by another service, and the Smart Grid API is not responding there.'
  }
}

$frontendPort = 4200
while ($frontendPort -lt 4300 -and -not (Test-PortAvailable $frontendPort)) {
  $frontendPort++
}
if ($frontendPort -ge 4300) {
  throw 'No available frontend port was found between 4200 and 4299.'
}

$frontendOut = Join-Path $logRoot 'frontend.log'
$frontendErr = Join-Path $logRoot 'frontend-error.log'
Start-Process -FilePath $npm.Source `
  -ArgumentList @('start', '--', '--host', '127.0.0.1', '--port', "$frontendPort") `
  -WorkingDirectory $frontend -WindowStyle Hidden `
  -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr | Out-Null

$appUrl = "http://127.0.0.1:$frontendPort"
if (-not (Wait-ForHttp $appUrl 90)) {
  throw "Frontend did not start. Check logs at $logRoot"
}

Start-Process $appUrl
Write-Host "Smart Grid Sémantique is ready: $appUrl" -ForegroundColor Green
Write-Host 'Demo login: admin / admin123'
Write-Host "Logs: $logRoot"

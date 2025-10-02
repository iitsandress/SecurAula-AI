param(
  [int]$Port = 8000
)

if (-not $env:EDUMON_API_KEY) {
  Write-Error "EDUMON_API_KEY no está definido. Establézcalo antes de ejecutar."
  exit 1
}

Push-Location "$PSScriptRoot\..\server"
$env:PYTHONUTF8=1
uvicorn main:app --host 0.0.0.0 --port $Port
Pop-Location

if (-not (Test-Path "$PSScriptRoot\..\agent\config.json")) {
  Write-Error "Falta agent\\config.json. Copie config.example.json y edítelo."
  exit 1
}

Push-Location "$PSScriptRoot\..\agent"
$env:PYTHONUTF8=1
python main.py
Pop-Location

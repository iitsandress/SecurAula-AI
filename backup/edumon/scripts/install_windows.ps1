# Requiere PowerShell 5+
param(
  [string]$Python = "python",
  [string]$ServerPort = "8000"
)

Write-Host "==> Instalando dependencias del servidor"
Push-Location "$PSScriptRoot\..\server"
$env:PYTHONUTF8=1
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
Pop-Location

Write-Host "==> Instalando dependencias del agente"
Push-Location "$PSScriptRoot\..\agent"
& $Python -m pip install -r requirements.txt
Pop-Location

Write-Host "==> Listo. Configure variables y arranque manualmente"
Write-Host "Servidor:"
Write-Host "  set EDUMON_API_KEY=su-clave-segura"
Write-Host "  set EDUMON_DATA_DIR=.\data (opcional)"
Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port $ServerPort"
Write-Host "Agente:"
Write-Host "  Copie agent\\config.example.json a agent\\config.json y edite server_url y api_key"
Write-Host "  python agent\\main.py"
